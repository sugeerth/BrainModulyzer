from PySide import QtCore, QtGui , QtUiTools
import os
import sys

#Loading UI Files
loader = QtUiTools.QUiLoader()
CURR = sys.path[0]
ui = loader.load(os.path.join(CURR, "UIFiles/interface.ui"))
dataSetLoader = loader.load(os.path.join(CURR, "UIFiles/datasetviewer.ui"))
screenshot = loader.load(os.path.join(CURR, "UIFiles/screeshot.ui"))

def setTitle():
    ui.setWindowTitle('Brain Visualizer')

setTitle()