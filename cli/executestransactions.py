from cli.error import ErrorWindow
from cli.manager import Manager
from cli.progress import ProgressWindow
from cli.stackedview import StackedView
from logic.transactions import Transaction


class ExecutesTransactions(StackedView):
    def __init__(self) -> None:
        super().__init__()

    async def execute_transaction(
            self, transaction: Transaction, is_cancellation=False) -> None:
        prog_wnd = None
        if (transaction.__class__.reports_progress()):
            prog_wnd = ProgressWindow()
            transaction.set_callback(prog_wnd.callback)
            self.push_on_stack(prog_wnd)

        res = await transaction.execute()
        if (prog_wnd is not None):
            prog_wnd.pop_on_stack()

        if (res is not None):
            self.push_on_stack(ErrorWindow(res))
            await self._updated_event.wait()
            return
        if (not is_cancellation):
            Manager.push_to_queue(transaction.revert())
