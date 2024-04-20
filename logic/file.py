import os
import os.path

class File:
    _path:str
    _selected:bool
    def getSize(self)->int | None:
        return os.path.getsize(self._path)
    
    def getSelectedFormatted(self)->str:
        return "(*)" if self._selected else "( )"
    def getSelected(self)->bool:
        return self._selected

    def setSelected(self,value:bool)->None:
        self._selected=value
        

    def getFormattedSize(self)->str:
        sz=self.getSize()
        if sz is None:
           return ""
        sfx=["bytes","KB","MB","GB","TB"]
        pos=0
        while sz>=1024:
            sz/=1024
            pos+=1
        return "{:.2f}".format(sz)+" "+sfx[pos]
    
    def isDir(self)->bool:
        return os.path.isdir(self._path)

    @staticmethod
    def fromPath(path:str)->str:
        file=File()
        file._path=path
        file._selected=False
        return file

    def getPath(self)->str:
        return self._path
