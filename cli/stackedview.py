class StackedView:
    def __init__(self) -> None:
        pass
    
    def assign_prev(self,prev:StackedView, fun:function)->None:
        self._prev_in_stack=prev
        self._fun_for_stack=fun
    
    def pop_on_stack(self)->None:
        self._fun_for_stack(self._prev_in_stack)
        self._prev_in_stack.rebuild()

