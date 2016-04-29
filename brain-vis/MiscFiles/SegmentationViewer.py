import math
import nibabel as nib
import numpy as np
import os
from PySide import QtCore, QtGui
import re

def GetColor(colortable, value):
    print "Redrawing stuff" 
    ct = GetColorTable(colortable)
    if ct.smoothing != ct.Linear:
        raise Exception("Unimplemented interploation method!")
    if value <= 0:
        return ct.GetControlPoints(0).colors
    elif value >= 1:
        return ct.GetControlPoints(ct.GetNumControlPoints()-1).colors
    else:
        np = 0
        while ct.GetControlPoints(np).position < value:
            np += 1
        cp0 = ct.GetControlPoints(np-1)
        cp1 = ct.GetControlPoints(np)
        t = (value - cp0.position) / (cp1.position - cp0.position)
        return tuple([(1-t)*a + t*b for a, b in zip(cp0.colors, cp1.colors)])

def ColorToInt(color):
    r, g, b, a = map(np.uint32, color)
    return a << 24 | r << 16 | g << 8 | b

class SliceViewer(QtGui.QWidget):
    regionToggled = QtCore.Signal(int)

    def __init__(self, segmentation_data, axis, colorTable):
        super(SliceViewer, self).__init__()

        self.segmentation = segmentation_data
        self.axis = axis
        self.displayedSlice = 0

        self.clut = np.array([ColorToInt(col + (255,)) for col in colorTable], dtype=np.uint32)

        slice_view_layout = QtGui.QHBoxLayout()
        self.setLayout(slice_view_layout)

        slider = QtGui.QSlider()
        slider.setRange(0, segmentation_data.shape[self.axis]-1)
        slider.valueChanged.connect(self.setDisplayedSlice)
        slider.setValue(self.displayedSlice)
        slice_view_layout.addWidget(slider)

        self.label = QtGui.QLabel()
        self.updateSliceLabel()
        label_layout = QtGui.QVBoxLayout()
        slice_view_layout.addLayout(label_layout)
        label_layout.addStretch(1)
        label_layout.addWidget(self.label)
        label_layout.addStretch(1)

    def extractSlice(self, volData):
        if self.axis == 0:
            return volData[self.displayedSlice, :, :]
        elif self.axis == 1:
            return volData[:, self.displayedSlice, :]
        else:
            return volData[:, :, self.displayedSlice]

    def updateSliceLabel(self):
        segmentation_slice = self.extractSlice(self.segmentation)
        image_data = self.clut[segmentation_slice]
        image_data = np.array(image_data[:, ::-1], order='F')
        image = QtGui.QImage(image_data, image_data.shape[0], image_data.shape[1], QtGui.QImage.Format_RGB32)
        self.label.setPixmap(QtGui.QPixmap.fromImage(image))

    def setDisplayedSlice(self, sliceNo):
        self.displayedSlice = sliceNo
        self.updateSliceLabel()

    def mousePressEvent(self, event):
        pos = self.label.mapFromParent(event.pos())
        x, y = pos.x(), pos.y()

        segmentation_slice = self.extractSlice(self.segmentation)[:, ::-1]
        if x in range(segmentation_slice.shape[0]) and y in range(segmentation_slice.shape[1]):
            newId = segmentation_slice[x, y]
            if newId != 0:
                print "Select region %d" % newId
                self.regionToggled.emit(newId)

class SegmentationPlot(QtCore.QObject):
    #regionToggled = QtCore.Signal(int)

    def __init__(self, segmentation_filename, colorTable):
        super(SegmentationPlot, self).__init__()

        ccpl = ColorControlPointList()
        ccpl.smoothing = ccpl.None
        for i, col in enumerate(colorTable):
            cp = ColorControlPoint()
            cp.position = float(i) / float(len(colorTable)-1)
            cp.colors = col + (255,)
            ccpl.AddControlPoints(cp)
        AddColorTable("parcel_color_table", ccpl)

        self.selected = [ 0 ] * len(colorTable)
        self.CreateSelectedExpression()

        OpenDatabase(segmentation_filename)
        self.segmentation_filename = segmentation_filename
        self.segmentationPlotId = GetNumPlots()
        AddPlot('Pseudocolor', 'var')
        patts = PseudocolorAttributes()
        patts.colorTableName = "parcel_color_table"
        patts.legendFlag = 0
        SetPlotOptions(patts)
        AddOperator("DualMesh")
        AddOperator("Threshold")
        tatts = ThresholdAttributes()
        tatts.listedVarNames = ("selected")
        tatts.lowerBounds = (1)
        tatts.upperBounds = (1)
        tatts.zonePortions = (1)
        SetOperatorOptions(tatts)
        DrawPlots()

    def CreateSelectedExpression(self):
        DefineScalarExpression('selected', 'map(var, ' + str(range(len(self.selected))) + ', ' + str(self.selected) + ')' )

    def toggleRegion(self, regionId):
        self.selected[regionId] = int(not self.selected[regionId])
        self.CreateSelectedExpression()
        ClearWindow()
        DrawPlots()

#   def makeActive(self):
#       SetActivePlots(self.segmentationPlotId)
#
#   def performPick3D(self):
#       RegisterCallback("PickAttributes")
#       pattern = re.compile('<zonal> = \d*')
#       match = pattern.search(GetPickOutput())
#       if match != None:
#           try:
#               SetWindowMode("navigate")
#               regionId = int(match.group(0).split('=')[1]) - 1
#               self.regionToggled.emit(regionId)
#           except:
#               pass
#
#   def startPick3D(self):
#       RegisterCallback("PickAttributes", lambda pa: self.performPick3D())
#       self.makeActive()
#       SetWindowMode("zone pick")

def InitVisItSettings():
    annAtts = GetAnnotationAttributes()
    annAtts.userInfoFlag = 0
    annAtts.databaseInfoFlag = 0
    annAtts.timeInfoFlag = 0
    SetAnnotationAttributes(annAtts)

    ratts = GetRenderingAttributes()
    ratts.displayListMode = ratts.Always
    ratts.scalableActivationMode = ratts.Never
    SetRenderingAttributes(ratts)

    pickAtts = GetPickAttributes()
    pickAtts.variables = ("default")
    pickAtts.showIncidentElements = 0
    pickAtts.showNodeId = 0
    pickAtts.showNodeDomainLogicalCoords = 0
    pickAtts.showNodeBlockLogicalCoords = 0
    pickAtts.showNodePhysicalCoords = 0
    pickAtts.showZoneId = 0
    pickAtts.showZoneDomainLogicalCoords = 0
    pickAtts.showZoneBlockLogicalCoords = 1
    pickAtts.doTimeCurve = 0
    pickAtts.conciseOutput = 0
    pickAtts.showTimeStep = 0
    pickAtts.showMeshName = 0
    pickAtts.showGlobalIds = 0
    pickAtts.showPickLetter = 0
    pickAtts.reusePickLetter = 1
    pickAtts.createSpreadsheet = 0
    pickAtts.floatFormat = "%g"
    SetPickAttributes(pickAtts)

    SuppressQueryOutputOn()

def GenerateColorTable(numSegments):
    # List of distinguishable colors 
    distinguishableColors = [ (240, 163, 255), (0, 117, 220), (153, 63, 0),
        (76, 0, 92), (25, 25, 25), (0, 92, 49), (43, 206, 72), (255, 204, 153),
        (128, 128, 128), (148, 255, 181), (143, 124, 0), (157, 204, 0),
        (194, 0, 136), (0, 51, 128), (255, 164, 5), (255, 168, 187), (66, 102, 0),
        (255, 0, 16), (94, 241, 242), (0, 153, 143), (224, 255, 102),
        (116, 10, 255), (153, 0, 0), (255, 255, 128), (255, 255, 0), (255, 80, 5) ]
    # For the moment, just repeat the base color table sufficiently often to have
    # as many colors as there are segments
    numRepeats = int(math.ceil(float(numSegments) / float(len(distinguishableColors))))
    return [ (255, 255, 255) ] + (distinguishableColors * numRepeats)[:numSegments]

def magnify(a, mag_factor):
    return np.repeat(np.repeat(np.repeat(a, mag_factor, axis=0), mag_factor, axis=1), mag_factor, axis=2)
### MAIN

# PARAMETERS
segmentation_filename = '/Users/ghweber/Data/UCSF_Brain/masked_B07-243_pearson=.7-2-continuous.npy'
segmentation_data = np.load(segmentation_filename)
segmentation_data_mag_factor = 5

segmentation_data = magnify(segmentation_data, segmentation_data_mag_factor)

# Some VisIt initialization
InitVisItSettings()
# Setup ColorTable
numSegments = int(segmentation_data.max())
colorTable = GenerateColorTable(numSegments)

segmentationPlot = SegmentationPlot(segmentation_filename, colorTable)
view3D = GetView3D()
view3D.viewNormal = (0, 1, 0)
view3D.viewUp = (0, 0, 1)
SetView3D(view3D)

main = QtGui.QWidget()
main.setSizePolicy(QtGui.QSizePolicy.Policy.Expanding, QtGui.QSizePolicy.Policy.Expanding)
mainLayout = QtGui.QHBoxLayout()
main.setLayout(mainLayout)
slice_view = SliceViewer(segmentation_data, 0, colorTable)
mainLayout.addWidget(slice_view)
rwin = GetRenderWindow(1)
rwin.setMinimumSize(500, 500)
mainLayout.addWidget(rwin)

#visitControlsLayout = QtGui.QHBoxLayout()
#visitViewerLayout.addLayout(visitControlsLayout)
#toggleThreeSliceButton = QtGui.QPushButton("Show/Hide Slices")
#visitControlsLayout.addWidget(toggleThreeSliceButton)
#toggleThreeSliceButton.clicked.connect(brainTemplatePlot.toggleThreeSlice)
#toggleBrainSurfaceButton = QtGui.QPushButton("Show/Hide Brain Surface")
#visitControlsLayout.addWidget(toggleBrainSurfaceButton)
#toggleBrainSurfaceButton.clicked.connect(brainTemplatePlot.toggleBrainSurface)
#pickButton = QtGui.QPushButton("Pick Region")
#visitControlsLayout.addWidget(pickButton)
#pickButton.clicked.connect(segmentationPlot.startPick3D)
#segmentationPlot.regionToggled.connect(tw.selectRegion)
#for sv in slice_views:
    #tw.selectedRegionChanged.connect(sv.colorRelativeToRegion)
slice_view.regionToggled.connect(segmentationPlot.toggleRegion)
main.show()

### HACK to keep Pick and Information windows from popping up
pickWin = pyside_support.GetOtherWindow("Pick")
if pickWin != None:
    dummy1 = QtGui.QMainWindow()
    dummy1.setCentralWidget(pickWin)
    dummy1.hide()
infoWin = pyside_support.GetOtherWindow("Information")
if infoWin != None:
    dummy2 = QtGui.QMainWindow()
    dummy2.setCentralWidget(infoWin)
    dummy2.hide()


