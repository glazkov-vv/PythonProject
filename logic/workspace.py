from os import listdir
import os.path
from logic.file import *
from typing import Iterable
from typing import Literal
from functools import cmp_to_key
from logic.selection import Selection
from logic.subscriptable import Subscriptable


def build_table(path=None,tree=False)->Iterable[File]:
    if (not tree):
        return [File.fromPath(os.path.join("" if path is None else path,h)) for h in listdir(path)]
    
    walkres=os.walk(path)
    ans=[]
    binds={}
    for (dir,dirnames,filenames) in walkres:
        total=dirnames+filenames
        for h in total:
            cfile=File.fromPath(os.path.join(dir,h),None if dir not in binds else binds[dir])
            binds[cfile.getPath()]=cfile
            ans.append(cfile)
    return ans


class Workspace(Subscriptable):
    def __del__(self)->None:
        WorkspaceManager._instances.remove(self)
    def __init__(self,path) -> None:
        super().__init__()
        self._path=path
        self._sort=("name","asc")
        self._contents:list=None
        self._tree=False
        self.rebuild()
        WorkspaceManager._instances.append(self)
    
    def get_tree(self)->bool:
        return self._tree
    
    def set_tree(self,val:bool)->None:
        self._tree=val
        self.rebuild()

    def rebuild(self,prop=None)->None:
        self._contents=build_table(self.get_path(),self._tree)

        (prop,type)=self._sort
        reverse= -1 if type=="desc" else 1
        def cmp(x:File,y:File)->int:
            c=1

            if (x.get_depth()>y.get_depth()):
                (x,y)=(y,x)
                c*=-1
            
            y=y.get_kth_par(y.get_depth()-x.get_depth())
            if y==x:
                return -1*c

            if (x._par!=y._par):
                return cmp(x._par,y._par)
            xkey=File.props[prop](x)
            ykey=File.props[prop](y)
            if xkey<ykey:
                return -1*c*reverse
            return 1*c*reverse
            

        self._contents.sort(key=cmp_to_key(cmp))


        self.send_update(prop)
    def get_contents(self)->Iterable[File]:
        return self._contents
    def get_path(self)->str:
        return self._path
    
    def get_sort(self):
        return self._sort

    def set_sort(self,prop:str,type:Literal["asc","desc"]):
        #assert(prop in [h[0] for h in File.props])
        #assert(type in ["asc","desc"])
        self._sort=(prop,type)
        self.rebuild(prop)

    """ def update_view(self)->None:
        if self._callback_object is not None:
            self._callback_object.update_from_top() """

    """ def set_callback_object(self,value:object)->None:
        self._callback_object=value """

    def get_children(self,file:File)->list[File]:
        return [h for h in self._contents if file in h.get_pars()]

    def set_selected(self,file:File,value:bool)->int:
        if (value==False):
            file.setSelected(False)
            for h in self.get_children(file):
                h.setSelected(False)
        if (value==True):
            file.setSelected(True)
            for h in self.get_children(file):
                h.setSelected('unavailable')

    def step_in(self,path)->None|str:
        if (not os.access(path,os.X_OK) or not os.access(path,os.R_OK)):
            return "Insufficient permissions to read the directory"

        self._path=path
        self.rebuild()
        self.send_update()
    
    def step_up(self)->None|str:
        return self.step_in(os.path.dirname(self._path))
        
        
    def get_selection(self)->Selection:
        return Selection([h.getPath() for h in self._contents if h.getSelected()==True])
    
    