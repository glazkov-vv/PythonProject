import tempfile
import pytest
import os
from logic.file import File
from logic.workspace import Workspace
from logic.transactions import *

@pytest.fixture
def setupdir():
    global tmpdir
    tmpdir=tempfile.mkdtemp(suffix="td")
    
    global tmpdir_file
    tmpdir_file=File.fromPath(tmpdir)

    os.mkdir(os.path.join(tmpdir,"A"))
    os.mkdir(os.path.join(tmpdir,"A","B"))
    os.mkdir(os.path.join(tmpdir,"A","C"))
    with open(os.path.join(tmpdir,"A","C","x.txt"),"w") as f:
        f.write("1")

    with open(os.path.join(tmpdir,"A","B","y.txt"),"w") as f:
        f.write("11")
    global wspace
    wspace=Workspace(tmpdir)

@pytest.mark.asyncio
async def test_copy_removal(setupdir):
    cpath=os.path.join(tmpdir,"A","C")
    
    c1=CopyTransaction(Selection([cpath]),os.path.join(tmpdir,"A","B"))
    await c1.execute()
    assert(os.path.getsize(os.path.join(tmpdir,'A',"B","C","x.txt"))==1) 
    
    await c1.revert().execute()
    assert(not os.path.exists(os.path.join(tmpdir,"A","B","C")))

@pytest.mark.asyncio
async def test_copy(setupdir):
    cpath=os.path.join(tmpdir,"A","C")
    
    c1=CopyTransaction(Selection([cpath]),os.path.join(tmpdir,"A","B"))
    await c1.execute()
    assert(os.path.getsize(os.path.join(tmpdir,'A',"B","C","x.txt"))==1) 
    
    await c1.revert().execute()
    assert(not os.path.exists(os.path.join(tmpdir,"A","B","C")))

@pytest.mark.asyncio
async def test_move(setupdir):
    cpath=os.path.join(tmpdir,"A","C")
    
    c1=MoveTransaction(Selection([cpath]),os.path.join(tmpdir,"A","B"))
    await c1.execute()
    assert(os.path.getsize(os.path.join(tmpdir,'A',"B","C","x.txt"))==1) 
    assert(not os.path.exists(os.path.join(tmpdir,"A","C")))

    await c1.revert().execute()
    assert(not os.path.exists(os.path.join(tmpdir,"A","B","C")))
    assert(os.path.exists(os.path.join(tmpdir,"A","C")))


@pytest.mark.asyncio
async def test_change_permissions_and_unsuccessful_copy_move(setupdir):
    cpath=os.path.join(tmpdir,"A","C")
    cperm=File.fromPath(cpath).get_permissions()
    nperm=[True,False,True]*3
    c1=ChangePermissionTransaction(cpath,cperm,nperm)
    await c1.execute()
    assert(File.fromPath(cpath).get_permissions()==nperm)
    
    c2=MoveTransaction(Selection([cpath]),os.path.join(tmpdir,"A","B"))
    res=await c2.execute()
    assert(res!=None)

    c1.revert().execute()
    #assert(File.fromPath(cpath).get_permissions()==cperm)