from typing import Callable
class Subscriptable:
    def __init__(self) -> None:
        self._subscripted=[]

    def subscribe(self,value:Callable)->None:
        self._subscripted.append(value)
    def unsubscribe(self,value:Callable)->None:
        self._subscripted.remove(value)
    def send_update(self,*args,**kwargs)->None:
        for h in self._subscripted:
            h(*args,**kwargs)