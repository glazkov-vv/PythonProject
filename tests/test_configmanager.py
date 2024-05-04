import sys
import os
#sys.path.append(os.path.abspath(""))

#print(sys.path)


from logic.configmanager import ConfigManager
def test_txt():
    assert(ConfigManager.get_command("/test1/test2.txt")!= None)
def test_notxt():
    assert(ConfigManager.get_command("/test1/test2.py")==None)