import csv
import sys
import math
from collections import defaultdict
from PySide import QtCore, QtGui
from sys import platform as _platform
import weakref
import cProfile
import os

class ProcessQuantTable(QtGui.QWidget):
    def __init__(self,widget,Ui):
        super(ProcessQuantTable,self).__init__()
        print "In Quant Table ?"
        Ui.BrainList.addItem('Regions Centrality Participation closeness betweenness')
        for i in range(10):
        	Ui.BrainList.addItem('Item %s' % (i + 1))