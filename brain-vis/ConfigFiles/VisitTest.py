import visit
import PySide

from PySide.QtUiTools import *
 
SetAutoUpdate(True)
 
visitgui = GetUIWindow()
 
class IsoContourWindow(QWidget):
 
    def __init__(self,windowID):
        super(IsoContourWindow,self).__init__()
        lout = QVBoxLayout(self)
        self.slider = QSlider(Qt.Horizontal,self)
        self.slider.setMinimum(1)
        self.slider.setMaximum(99)
        rwin = pyside_support.GetRenderWindow(windowID)
        lout.addWidget(rwin)
        lout.addWidget(self.slider)
        self.windowID = windowID
 
    def open(self,filename,var):
        SetActiveWindow(self.windowID)
        OpenDatabase(filename)
        AddPlot("Contour",var)
        self.isovalue_update(1)
        self.slider.valueChanged.connect(self.slide_update)
        #ResizeWindow(1,800,600)
        DrawPlots()
 
    def isovalue_update(self,perc):
        SetActiveWindow(self.windowID)
        ContourAtts = ContourAttributes()
        ContourAtts.colorType = ContourAtts.ColorByColorTable
        ContourAtts.colorTableName = "hot_desaturated"
        ContourAtts.contourPercent = (perc)
        ContourAtts.contourMethod = ContourAtts.Percent  # Level, Value, Percent
        SetPlotOptions(ContourAtts)
 
    def slide_update(self):
        SetActiveWindow(self.windowID)
        perc = self.slider.value()
        self.isovalue_update(perc)
        print "slider updating self.", perc, self.windowID
 
nextRenderWindowIndex = 0
RenderWindowList = [ IsoContourWindow(1) ]
 
 
def ReturnNextWindow():
    global RenderWindowList
    global nextRenderWindowIndex
    global IsocontourWindow
 
    if nextRenderWindowIndex < len(RenderWindowList) :
        window = RenderWindowList[nextRenderWindowIndex]
    else:
        AddWindow()
        window = IsoContourWindow(nextRenderWindowIndex+1)
        RenderWindowList.append( window )
    nextRenderWindowIndex = nextRenderWindowIndex + 1
    return window
 
#create custom ui loader to handle VisIt render windows
class CustomQUiLoader(QUiLoader):
    def createWidget(self,classname,parent,name):
        if classname == "RenderWindow":
            return ReturnNextWindow()
        return QUiLoader.createWidget(self,classname,parent,name)
 
a = CustomQUiLoader()
gui = a.load("scipydemo.ui")
 
#functions and connections
def showVisItGUI():
    if visitgui.isVisible():
        visitgui.hide()
    else:
        visitgui.show()
 
def showLoadFile():
    loadWin = GetOtherWindow("File open")
    loadWin.show()
 
loadFile = gui.findChild(QPushButton, "loadFile")
loadFile.pressed.connect(showLoadFile)
 
showVisItWindow = gui.findChild(QPushButton,"showVisItWindow")
showVisItWindow.pressed.connect(showVisItGUI)
 
filename = "/Users/sugeerthmurugesan/LBLProjects/TCBBDownload/LastVisit1/visit2.10.0/data/noise.silo"
var1 = "hardyglobal"
var2 = "shepardglobal"
 
RenderWindowList[0].open(filename,var1)
RenderWindowList[1].open(filename,var2)
 
gui.show()