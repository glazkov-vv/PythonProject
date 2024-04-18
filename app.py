from __future__ import annotations
import debugpy
import time

import urwid


# Allow other computers to attach to debugpy at this IP address and port.
debugpy.listen(('0.0.0.0', 5678))
print("Waiting for debugger to attach...")

# Pause the script until a debugger is attached
debugpy.wait_for_client()





def exit_on_q(key):
    if key in {"q", "Q"}:
        present=top.contents
        updated=[present[0],(build_list(),present[1][1])]
        top.contents[1]=(build_list(),present[1][1])
        top.top_w=build_list()
        top._invalidate()
        loop.draw_screen()


palette = [
    ("banner", "", "", "", "#ffa", "#60d"),
    ("streak", "", "", "", "g50", "#60a"),
    ("inside", "", "", "", "g38", "#808"),
    ("outside", "", "", "", "g27", "#a06"),
    ("bg", "", "", "", "g7", "#d06"),
]   

lastTbx=0


def build_list() -> urwid.ListBox:
    space_distr=[0.6,0.4]
    finres=[]
    for i in range(3):
        t1=urwid.Button("abc"+str(time.thread_time()))
        t2=urwid.Button("defragmentation impending",)
        global lastTbx
        lastTbx=t2
        innerEl=urwid.Columns([('weight',2,t1),('weight',1,t2)],)
        finalEl=urwid.AttrMap(innerEl,None,focus_map="reversed")
        finres.append(finalEl)
    
    lbx=urwid.ListBox(finres)
    lbx.set_focus(0)
    ans=urwid.Filler(lbx,height=20)
    return ans

list=build_list()
top = urwid.Overlay(
    list,
    urwid.SolidFill("\N{MEDIUM SHADE}"),
    align=urwid.CENTER,
    width=(urwid.RELATIVE, 85),
    valign=urwid.MIDDLE,
    height=(urwid.RELATIVE, 85),
    min_width=20,
    min_height=9,
)

loop=urwid.MainLoop(top,palette=[("reversed", "standout", "")],unhandled_input=exit_on_q)
loop.run()