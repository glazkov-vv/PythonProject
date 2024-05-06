from __future__ import annotations
import debugpy
import time
from os import listdir
import os

import os.path
from os.path import isfile, join
import urwid
from cli.twotabs import *
from cli.entry import *
from logic.file import *
from logic.workspace import *
import sys

if "-d" in sys.argv:
    # Allow other computers to attach to debugpy at this IP address and port.
    debugpy.listen(('0.0.0.0', 5678))
    print("Waiting for debugger to attach...")

    # Pause the script until a debugger is attached
    debugpy.wait_for_client()

palette = [
    ("banner", "", "", "", "#ffa", "#60d"),
    ("streak", "", "", "", "g50", "#60a"),
    ("inside", "", "", "", "g38", "#808"),
    ("outside", "", "", "", "g27", "#a06"),
    ("bg", "", "", "", "g7", "#d06"),
]   

lastTbx=0













    
# def build_list(fileEntries:iterable[file]) -> urwid.Filler:
#     space_distr=[0.6,0.4]
#     finres=[]
#     for h in fileEntries:

#         temp=FileEntry(h,1)
#         finres.append(temp)
#     lbx=urwid.ListBox(finres)
#     #lbx.set_focus(0)
#     ans=urwid.Filler(lbx,height=20)
#     return ans

#list=build_list(build_table())
Manager.active_workspaces[0]=Workspace(".")
Manager.active_workspaces[1]=Workspace(".")

content=TwoTabs({},Manager.active_workspaces)   
top = content


def update(value:StackedView):
    value._updated_event.set()
    value._updated_event.clear()
    loop.widget=value
    loop.draw_screen()

content.assign_prev(None,update)


loop=urwid.MainLoop(top,palette=[("normal","default","default"),
                                     ("rev normal","standout",""),
                                     ("reversed", "standout", ""),
                                     ("execs","light green",'default'),
                                     ("rev execs","light green","light gray"),
                                     ("folds","dark blue","default"),
                                     ("rev folds","dark blue","light gray")],event_loop=urwid.AsyncioEventLoop())
never_event=asyncio.Event()
Manager.loop=loop


loop.run()
#while (True):
 #   pass
