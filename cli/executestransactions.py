from cli.error import ErrorWindow
from cli.manager import Manager
from cli.stackedview import StackedView
from logic.transactions import Transaction


class ExecutesTransactions(StackedView):
    def __init__(self) -> None:
        super().__init__()

    async def execute_transaction(self,transaction:Transaction,is_cancellation=False)->None:
        res=transaction.execute()
        if (res!=None):
            self.push_on_stack(ErrorWindow(res))
            await self._updated_event.wait()
            return 
        if (not is_cancellation):
                Manager.push_to_queue(transaction.revert())