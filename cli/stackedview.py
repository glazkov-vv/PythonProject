class StackedView:
    def __init__(self) -> None:
        pass
    
    def assign_prev(self,prev, fun)->None: # type: ignore
        self._prev_in_stack=prev
        self._fun_for_stack=fun
    
    def push_on_stack(self,next)->None: # type: ignore
        next.assign_prev(self,self._fun_for_stack)
        self._fun_for_stack(next)

    def pop_on_stack(self)->None:
        self._fun_for_stack(self._prev_in_stack)
        self._prev_in_stack.rebuild()

