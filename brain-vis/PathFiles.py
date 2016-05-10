from PySide import QtCore, QtGui , QtUiTools
import os

#Loading UI Files
loader = QtUiTools.QUiLoader()

CURR = os.environ['PYTHONPATH']
ui = loader.load(os.path.join(CURR, "UIFiles/interface.ui"))
dataSetLoader = loader.load(os.path.join(CURR, "UIFiles/datasetviewer.ui"))
screenshot = loader.load(os.path.join(CURR, "UIFiles/screeshot.ui"))

def setTitle():
    ui.setWindowTitle('Brain Visualizer')

setTitle()