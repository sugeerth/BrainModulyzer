import os,sys
"""
If you made it this far congrats!!
CHANGE the paths below to visit and your directory
"""
import os.path as path
import sys

CURR =  path.abspath(path.join(__file__ ,"..")) # going one directory up 
CURR = os.path.join(CURR, "brain-vis/BrainViewer.py")

os.system("python "+str(CURR))
