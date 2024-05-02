import asyncio
import urwid
from cli.error import ErrorWindow
from logic.transactions import MoveTransaction, RemoveTransaction
from logic.workspace import *
from cli.entry import *
import typing

def sigtest():
    pass



class VisibleInfoMiddle(typing.NamedTuple):
    """Named tuple for ListBox internals."""

    offset: int
    focus_widget: urwid.Widget
    focus_pos: Hashable
    focus_rows: int
    cursor: tuple[int, int] | tuple[int] | None


class VisibleInfoFillItem(typing.NamedTuple):
    """Named tuple for ListBox internals."""

    widget: urwid.Widget
    position: Hashable
    rows: int


class VisibleInfoTopBottom(typing.NamedTuple):
    """Named tuple for ListBox internals."""

    trim: int
    fill: list[VisibleInfoFillItem]

    @classmethod
    def from_raw_data(
        cls,
        trim: int,
        fill: Iterable[tuple[urwid.Widget, Hashable, int]],
    ) :
        """Construct from not typed data.

        Useful for overridden cases."""
        return cls(trim=trim, fill=[VisibleInfoFillItem(*item) for item in fill])  # pragma: no cover


class VisibleInfo(typing.NamedTuple):
    middle: VisibleInfoMiddle
    top: VisibleInfoTopBottom
    bottom: VisibleInfoTopBottom

    @classmethod
    def from_raw_data(
        cls,
        middle: tuple[int, urwid.Widget, Hashable, int, tuple[int, int] | tuple[int] | None],
        top: tuple[int, Iterable[tuple[urwid.Widget, Hashable, int]]],
        bottom: tuple[int, Iterable[tuple[urwid.Widget, Hashable, int]]],
    ):
        """Construct from not typed data.

        Useful for overridden cases.
        """
        return cls(  # pragma: no cover
            middle=VisibleInfoMiddle(*middle),
            top=VisibleInfoTopBottom.from_raw_data(*top),
            bottom=VisibleInfoTopBottom.from_raw_data(*bottom),
        )







class MonitoredListBox(urwid.ListBox):

    def calculate_visible(
        self,
        size: tuple[int, int],
        focus: bool = False,
    ) -> VisibleInfo | tuple[None, None, None]:
        """
        Returns the widgets that would be displayed in
        the ListBox given the current *size* and *focus*.

        see :meth:`Widget.render` for parameter details

        :returns: (*middle*, *top*, *bottom*) or (``None``, ``None``, ``None``)

        *middle*
            (*row offset*(when +ve) or *inset*(when -ve),
            *focus widget*, *focus position*, *focus rows*,
            *cursor coords* or ``None``)
        *top*
            (*# lines to trim off top*,
            list of (*widget*, *position*, *rows*) tuples above focus in order from bottom to top)
        *bottom*
            (*# lines to trim off bottom*,
            list of (*widget*, *position*, *rows*) tuples below focus in order from top to bottom)
        """
        (maxcol, maxrow) = size

        # 0. set the focus if a change is pending
        if self.set_focus_pending or self.set_focus_valign_pending:
            self._set_focus_complete((maxcol, maxrow), focus)

        # 1. start with the focus widget
        focus_widget, focus_pos = self._body.get_focus()
        if focus_widget is None:  # list box is empty?
            return None, None, None
        top_pos = focus_pos

        offset_rows, inset_rows = self.get_focus_offset_inset((maxcol, maxrow))
        #    force at least one line of focus to be visible
        if maxrow and offset_rows >= maxrow:
            offset_rows = maxrow - 1

        #    adjust position so cursor remains visible
        cursor = None
        if maxrow and focus_widget.selectable() and focus and hasattr(focus_widget, "get_cursor_coords"):
            cursor = focus_widget.get_cursor_coords((maxcol,))

        if cursor is not None:
            _cx, cy = cursor
            effective_cy = cy + offset_rows - inset_rows

            if effective_cy < 0:  # cursor above top?
                inset_rows = cy
            elif effective_cy >= maxrow:  # cursor below bottom?
                offset_rows = maxrow - cy - 1
                if offset_rows < 0:  # need to trim the top
                    inset_rows, offset_rows = -offset_rows, 0

        #    set trim_top by focus trimmimg
        trim_top = inset_rows
        focus_rows = focus_widget.rows((maxcol,), True)

        # 2. collect the widgets above the focus
        pos = focus_pos
        fill_lines = offset_rows
        fill_above = []
        top_pos = pos
        while fill_lines > 0:
            prev, pos = self._body.get_prev(pos)
            if prev is None:  # run out of widgets above?
                offset_rows -= fill_lines
                break
            top_pos = pos

            p_rows = prev.rows((maxcol,))
            if p_rows:  # filter out 0-height widgets
                fill_above.append(VisibleInfoFillItem(prev, pos, p_rows))
            if p_rows > fill_lines:  # crosses top edge?
                trim_top = p_rows - fill_lines
                break
            fill_lines -= p_rows

        trim_bottom = max(focus_rows + offset_rows - inset_rows - maxrow, 0)

        # 3. collect the widgets below the focus
        pos = focus_pos
        fill_lines = maxrow - focus_rows - offset_rows + inset_rows
        fill_below = []
        while fill_lines > 0:
            next_pos, pos = self._body.get_next(pos)
            if next_pos is None:  # run out of widgets below?
                break

            n_rows = next_pos.rows((maxcol,))
            if n_rows:  # filter out 0-height widgets
                fill_below.append(VisibleInfoFillItem(next_pos, pos, n_rows))
            if n_rows > fill_lines:  # crosses bottom edge?
                trim_bottom = n_rows - fill_lines
                fill_lines -= n_rows
                break
            fill_lines -= n_rows

        # 4. fill from top again if necessary & possible
        fill_lines = max(0, fill_lines)

        if fill_lines > 0 and trim_top > 0:
            if fill_lines <= trim_top:
                trim_top -= fill_lines
                offset_rows += fill_lines
                fill_lines = 0
            else:
                fill_lines -= trim_top
                offset_rows += trim_top
                trim_top = 0
        pos = top_pos
        while fill_lines > 0:
            prev, pos = self._body.get_prev(pos)
            if prev is None:
                break

            p_rows = prev.rows((maxcol,))
            fill_above.append(VisibleInfoFillItem(prev, pos, p_rows))
            if p_rows > fill_lines:  # more than required
                trim_top = p_rows - fill_lines
                offset_rows += fill_lines
                break
            fill_lines -= p_rows
            offset_rows += p_rows

        # 5. return the interesting bits
        return VisibleInfo(
            VisibleInfoMiddle(offset_rows - inset_rows, focus_widget, focus_pos, focus_rows, cursor),
            VisibleInfoTopBottom(trim_top, fill_above),
            VisibleInfoTopBottom(trim_bottom, fill_below),
        )


    def render(
        self,
        size: tuple[int, int],  # type: ignore[override]
        focus: bool = False,
    ) -> urwid.CompositeCanvas | urwid.SolidCanvas:
        """
        Render ListBox and return canvas.

        see :meth:`Widget.render` for details
        """
        (maxcol, maxrow) = size

        self._rendered_size = size

        middle, top, bottom = self.calculate_visible((maxcol, maxrow), focus=focus)
        if middle is None:
            return urwid.SolidCanvas(" ", maxcol, maxrow)

        _ignore, focus_widget, focus_pos, focus_rows, cursor = middle  # pylint: disable=unpacking-non-sequence
        trim_top, fill_above = top  # pylint: disable=unpacking-non-sequence
        trim_bottom, fill_below = bottom  # pylint: disable=unpacking-non-sequence

        combinelist = []
        rows = 0
        fill_above.reverse()  # fill_above is in bottom-up order
        for widget, w_pos, w_rows in fill_above:
            canvas = widget.render((maxcol,))
            if w_rows != canvas.rows():
                raise NameError(
                    f"Widget {widget!r} at position {w_pos!r} "
                    f"within listbox calculated {w_rows:d} rows "
                    f"but rendered {canvas.rows():d}!"
                )
            rows += w_rows
            combinelist.append((canvas, w_pos, False))

        focus_canvas = focus_widget.render((maxcol,), focus=focus)

        if focus_canvas.rows() != focus_rows:
            raise urwid.ListBoxError(
                f"Focus Widget {focus_widget!r} at position {focus_pos!r} "
                f"within listbox calculated {focus_rows:d} rows "
                f"but rendered {focus_canvas.rows():d}!"
            )
        c_cursor = focus_canvas.cursor
        if cursor is not None and cursor != c_cursor:
            raise urwid.ListBoxError(
                f"Focus Widget {focus_widget!r} at position {focus_pos!r} "
                f"within listbox calculated cursor coords {cursor!r} "
                f"but rendered cursor coords {c_cursor!r}!"
            )

        rows += focus_rows
        combinelist.append((focus_canvas, focus_pos, True))

        for widget, w_pos, w_rows in fill_below:
            canvas = widget.render((maxcol,))
            if w_rows != canvas.rows():
                raise urwid.ListBoxError(
                    f"Widget {widget!r} at position {w_pos!r} "
                    f"within listbox calculated {w_rows:d} "
                    f"rows but rendered {canvas.rows():d}!"
                )
            rows += w_rows
            combinelist.append((canvas, w_pos, False))

        final_canvas = urwid.CanvasCombine(combinelist)

        if trim_top:
            final_canvas.trim(trim_top)
            rows -= trim_top
        if trim_bottom:
            final_canvas.trim_end(trim_bottom)
            rows -= trim_bottom

        if rows > maxrow:
            raise urwid.ListBoxError(
                f"Listbox contents too long!\nRender top={top!r}, middle={middle!r}, bottom={bottom!r}\n"
            )

        if rows < maxrow:
            if trim_bottom != 0:
                raise urwid.ListBoxError(
                    f"Listbox contents too short!\n"
                    f"Render top={top!r}, middle={middle!r}, bottom={bottom!r}\n"
                    f"Trim bottom={trim_bottom!r}"
                )

            bottom_pos = focus_pos
            if fill_below:
                bottom_pos = fill_below[-1][1]

            rendered_positions = frozenset(idx for _, idx, _ in combinelist)
            widget, next_pos = self._body.get_next(bottom_pos)
            while all(
                (
                    widget is not None,
                    next_pos is not None,
                    next_pos not in rendered_positions,
                )
            ):
                if widget.rows((maxcol,), False):
                    raise urwid.ListBoxError(
                        f"Listbox contents too short!\n"
                        f"Render top={top!r}, middle={middle!r}, bottom={bottom!r}\n"
                        f"Not rendered not empty widgets available (first is {widget!r} with position {next_pos!r})"
                    )

                widget, next_next_pos = self._body.get_next(next_pos)
                if next_pos == next_next_pos:
                    raise urwid.ListBoxError(
                        f"Next position after {next_pos!r} is invalid (points to itself)\n"
                        f"Looks like bug with {self._body!r}"
                    )
                next_pos = next_next_pos

            final_canvas.pad_trim_top_bottom(0, maxrow - rows)

        return final_canvas

class FilePanel(urwid.Filler):



    def __init__(self,custom_data,workspace:Workspace,pos:int=0) -> None:
        self._workspace=workspace
        self.pos=pos
        self._custom_data=custom_data.copy()
        self._custom_data["FilePanel"]=self
        self._custom_data["Workspace"]=workspace
        self._infocus=None
        #temp=build_table(path)

        lbx=MonitoredListBox([urwid.Text("OPS")]+[TitleEntry(self._custom_data)]+[FileEntry(self._custom_data,h,self.pos,workspace) for h in workspace.get_contents()])
        super().__init__(lbx,height=('relative',80))
        self._lastClick=0
    
    _path:str

    def get_sort(self)->tuple[None|str,None|Literal["asc","desc"]]:
        return self._workspace.get_sort()

    def report_focus(self,child:urwid.Widget):
        if (self._infocus!=child):
            if (self._infocus!=None):
                self._infocus.clear_focus()
            self._infocus=child
    

    def getPath(self)->str:
        return self._workspace.get_path()
    """ def update(self)->None:
        temp=build_table(self._path)
        lbx=urwid.ListBox([FileEntry(h,self.pos) for h in temp])
        self.body=lbx """
    
    

    def rebuild(self,in_focus:bool=False)->None:
        lbx=MonitoredListBox([urwid.Text("OPS")]+[TitleEntry(self._custom_data)]+[FileEntry(self._custom_data,h,self.pos,self._workspace) for h in self._workspace.get_contents()])
        oldpath=self.body.get_focus_path()
        self.body=lbx

        if (in_focus):
            #pass
            self.body.set_focus_path(oldpath)
            
            #self.body.focus_position=1
            self.body.set_focus_pending=None
            #titleentry=self.body.body.contents[1]
            #cols=titleentry.contents[0][0]
            
        
        self._invalidate()

        #self.body.set_focus_path(oldpath)
    
    def _start_selection(self,mode)->None|str:
        Manager.active_selection=self._workspace.get_selection()
        if (Manager.active_selection.empty()):
            async def fun():
                self._custom_data["TwoTabs"].push_on_stack(ErrorWindow("No files selected"))
                await self._custom_data["TwoTabs"]._updated_event.wait()
            asyncio.create_task(fun())
        else:
            Manager.set_lock(self.pos^1)
            Manager.operation_mode=mode
        return None

    

    def keypress(self, size: tuple[int, int] | tuple[()], key: str) -> str | None:
        if (key=='esc'):
            Manager.set_lock(None)
        
        if (key=='delete' and Manager.operation_mode=='normal'):
            sel=self._workspace.get_selection()
            asyncio.create_task(self._custom_data["TwoTabs"].execute_transaction(RemoveTransaction(sel)))
            return None

        if (key=='t' and Manager.operation_mode=='normal'):
            self._workspace.set_tree(not self._workspace.get_tree())


        if (key=='x' and Manager.operation_mode=="normal"):
            return self._start_selection("select_for_move")
            #self.contents[0][0]
        if (key=='c' and Manager.operation_mode=="normal"):
            return self._start_selection("select_for_copy")

        if (key=='backspace'):
            res=self._workspace.step_up()
            if (res!=None):
                asyncio.create_task(self._custom_data["TwoTabs"].push_on_stack(ErrorWindow(res)))
            return None
        
        return super().keypress(size, key)

    def render(self, size: tuple[int, int] | tuple[int], focus: bool = False) -> urwid.CompositeCanvas:
        return super().render(size, focus)
    

    def doubleClick():
        pass
    def mouse_event(self, size: tuple[int, int] | tuple[int], event, button: int, col: int, row: int, focus: bool) -> bool | None:
        
        return super().mouse_event(size, event, button, col, row, focus)

