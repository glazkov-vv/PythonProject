import tempfile
import pytest
import os
from logic.file import File
from logic.workspace import Workspace



@pytest.fixture
def setupdir():
    global tmpdir
    tmpdir=tempfile.mkdtemp(suffix="td")
    
    global tmpdir_file
    tmpdir_file=File.fromPath(tmpdir)

    os.mkdir(os.path.join(tmpdir,"A"))
    os.mkdir(os.path.join(tmpdir,"A","B"))
    os.mkdir(os.path.join(tmpdir,"A","C"))
    with open(os.path.join(tmpdir,"A","C","x.txt"),"w"):
        pass
    global wspace
    wspace=Workspace(tmpdir)

def test_basic(setupdir):
    assert(len(wspace.get_contents())==1)

def test_sort(setupdir):
    wspace.set_sort("name","desc")
    wspace.set_tree(True)
    arr=wspace.get_contents()
    assert([h.get_name() for h in arr]==["A","C","x.txt","B"])

def getfile(name):
    return [h for h in wspace.get_contents() if h.get_name()==name][0]


def test_selection(setupdir):
    wspace.set_tree(True)
    Cfile=getfile("C")
    xfile=getfile("x.txt")
    Afile=getfile("A")
    wspace.set_selected(Cfile,True)
    assert(Cfile.getSelected()==True)
    assert(xfile.getSelected()=="unavailable")
    assert(Afile.getSelected()==False)

    #wspace.set_selected(xfile,False)
    #assert(Cfile.getSelected()==True)
    #assert(xfile.getSelected()=="unavailable")
    #assert(Afile.getSelected()==False)

    wspace.set_selected(Afile,True)
    for h in wspace.get_contents():
        assert(h.getSelected()==(True if h==getfile("A") else "unavailable"))

    
def test_step(setupdir):
    Afile=getfile("A")
    cpath=wspace.get_path()
    wspace.step_in(os.path.join(cpath,"A","C"))
    wspace.set_tree(True)
    assert([h.get_name() for h in wspace.get_contents()]==["x.txt"])
    wspace.step_up()
    wspace.step_up()
    assert(cpath==wspace.get_path())