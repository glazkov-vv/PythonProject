import os
import tempfile
import pytest
import time
from logic.file import File

tmp=None
tmp_file=None

@pytest.fixture
def setupfile():
    global tmp
    a,tmp=tempfile.mkstemp(suffix="tf.txt")
    global tmp_file
    tmp_file=File.fromPath(tmp)

def test_name(setupfile):
    assert(tmp_file.get_name().endswith("tf.txt"))

def test_path(setupfile):
    path=tmp_file.getPath()
    name=tmp_file.get_name()
    assert(path.endswith(name) and path!=name)

def test_size(setupfile):
    assert tmp_file.getSize()==0

    with open(tmp,"w") as file:
        file.write("abc")
    assert tmp_file.getSize()==3

def test_date(setupfile):
    
    assert (tmp_file.get_modified().timestamp()-time.time())<1

def test_other_properties(setupfile):
    assert tmp_file.get_pars()==[]
    assert tmp_file.get_depth()==0
    assert not tmp_file.isDir()

def test_permissions(setupfile):
    os.chmod(tmp,0o612)
    assert tmp_file.get_permissions()==[True,True,False,False,False,True,False,True,False]


tmpdir=None
tmpdir_file=None

