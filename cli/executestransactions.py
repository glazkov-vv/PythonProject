from cli.error import ErrorWindow
from cli.manager import Manager
from cli.stackedview import StackedView


class ExecutesTransactions(StackedView):
    def __init__(self) -> None:
        super().__init__()

    async def execute_transaction(self,transaction)->None:
        res=transaction.execute()
        if (res!=None):
            self.push_on_stack(ErrorWindow(res))
            await self._updated_event
