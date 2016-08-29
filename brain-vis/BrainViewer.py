import csv
import math
from collections import defaultdict
import time

from sys import platform as _platform
import weakref
import cProfile
import sys
import pprint
from PySide import QtCore, QtGui , QtUiTools
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

app = QtGui.QApplication(sys.argv)

import community as cm
try:
    # ... reading NIfT
    import nibabel as nib
    import numpy as np
    # import h5py
    # ... graph drawi
    import networkx as nx

except:
    print "Couldn't import all required packages. See README.md for a list of required packages and installation instructions."
    raise


### BrainViewer packages
from CorrelationTables.correlation_table import CorrelationTable, \
CorrelationTableDisplay, CommunityCorrelationTableDisplay

from QuantData.quantTable import quantTable
from QuantData.quantData import QuantData
from VisitInterface.color_table import CreateColorTable
from VisitInterface.slice_viewer import *
from GraphInterface.Graph_interface import GraphWidget
from GraphInterface.GraphDataStructure import GraphVisualization
from General_Interface.Layout_interface import LayoutInit
from UIFiles.ProcessUi import ProcessQuantTable
from VisitInterface.CreateParcelationPlot import ParcelationPlotWindow
from PathLookup.PathFiles import *

"""
This is the main classless interface that talks to all other modules
I found this implementation to be easier to follow for others
"""

#Loading UI Files
### MAIN

# PARAMETERS
colorTableName = 'blue_lightblue_red_yellow'
selectedColor = (0, 100, 0, 255)

CorrelationTableShowFlag = True 
MainWindowShowFlag = True
GraphWindowShowFlag = True
ElectrodeWindowShowFlag = False

print "Files"
execfile('BrainViewerDataPaths.py')

print "Reading NII files."
# template_data = numpy.uint32( numpy.int16(template_data))
template_data = nib.load(template_filename).get_data().astype(np.uint32)
parcelation_data = nib.load(parcelation_filename).get_data().astype(np.uint32)

print "Setting up the correlation table display."
correlationTable = CorrelationTable(matrix_filename)

# colorTable = LinearColorTable();
colorTable = CreateColorTable(colorTableName)
colorTable.setRange(correlationTable.valueRange())

print "Setting up main GUI."
Counter = len(correlationTable.data)
DataColor = np.zeros(Counter+1)

# Hack for 2 datasets
Offset = 5

main = QtGui.QWidget()
main.setSizePolicy(QtGui.QSizePolicy.Policy.Expanding, QtGui.QSizePolicy.Policy.Expanding)
mainLayout = QtGui.QHBoxLayout()
main.setLayout(mainLayout)
main.setContentsMargins(0,0,0,0)

# initializing all thea layouts in the applicaiton 
# Layout for the tablewidget 
BoxTableWidget =QtGui.QWidget()

# Layout for the graph widget 
BoxGraphWidget =QtGui.QWidget()

# Layout for the electrode
BoxElectrodeWidget = QtGui.QWidget() 

allViewersLayout = QtGui.QVBoxLayout()
viewersLayout2 = QtGui.QHBoxLayout()

mainLayout.addLayout(allViewersLayout)
mainLayout.setContentsMargins(0,0,0,0)

viewersLayout1 = QtGui.QHBoxLayout()
allViewersLayout.addLayout(viewersLayout1)
allViewersLayout.setContentsMargins(0,0,0,0)

allViewersLayout.addLayout(viewersLayout2)
allViewersLayout.setContentsMargins(0,0,0,0)


print "Setting up Slice Views"
slice_views = [None, None, None]
slice_views[0] = SliceViewer(template_data, parcelation_data, 0, correlationTable, colorTable, selectedColor)
viewersLayout1.addWidget(slice_views[0])
viewersLayout1.setContentsMargins(0,0,0,0)

slice_views[1] = SliceViewer(template_data, parcelation_data, 1, correlationTable, colorTable, selectedColor)
viewersLayout1.addWidget(slice_views[1])
viewersLayout1.setContentsMargins(0,0,0,0)

slice_views[2] = SliceViewer(template_data, parcelation_data, 2, correlationTable, colorTable, selectedColor)
viewersLayout2.addWidget(slice_views[2])
viewersLayout2.setContentsMargins(0,0,0,0)

print "Setting up the IsoSurfaces"

ParcelationPlot = ParcelationPlotWindow(parcelation_filename, template_filename, correlationTable,selectedColor,colorTable, slice_views[0],slice_views[1],slice_views[2])

slice_views[0].sliceChanged.connect(ParcelationPlot.setThreeSliceX)
slice_views[0].regionSelected.connect(ParcelationPlot.colorRelativeToRegion)

slice_views[1].sliceChanged.connect(ParcelationPlot.setThreeSliceY)
slice_views[1].regionSelected.connect(ParcelationPlot.colorRelativeToRegion)

slice_views[2].sliceChanged.connect(ParcelationPlot.setThreeSliceZ)
slice_views[2].regionSelected.connect(ParcelationPlot.colorRelativeToRegion)


print "Setting up Graph data GraphDataStructure"
Tab_2_AdjacencyMatrix = GraphVisualization(correlationTable)

print "Setting up CorrelationTable for communities"
Tab_2_CorrelationTable = CommunityCorrelationTableDisplay(correlationTable, colorTable,Tab_2_AdjacencyMatrix)
Tab_2_CorrelationTable.selectedRegionChanged.connect(ParcelationPlot.colorRelativeToRegion)
Tab_2_CorrelationTable.setMinimumSize(390, 460)

print "Setting up CorrelationTable"

Tab_1_CorrelationTable = CorrelationTableDisplay(correlationTable, colorTable,Tab_2_AdjacencyMatrix)
Tab_1_CorrelationTable.selectedRegionChanged.connect(ParcelationPlot.colorRelativeToRegion)
Tab_1_CorrelationTable.setMinimumSize(390, 460)
Tab_2_CorrelationTable.show()


print "Setting up Graph Widget"

""" Controlling graph widgets  """
widget = GraphWidget(Tab_2_AdjacencyMatrix,Tab_2_CorrelationTable,correlationTable,colorTable,selectedColor,BoxGraphWidget,BoxTableWidget,Offset,ui)

Tab_1_CorrelationTable.selectedRegionChanged.connect(widget.NodeSelected)
Tab_1_CorrelationTable.selectedRegionChanged.connect(Tab_2_CorrelationTable.selectRegion)

Tab_2_CorrelationTable.selectedRegionChanged.connect(Tab_1_CorrelationTable.selectedRegionChanged)

""" Controlling Quant Table """
# the solvent data ...
quantData=QuantData(widget)
widget.ThresholdChange.connect(quantData.ThresholdChange)

quantTableObject = quantTable(quantData,widget)
quantData.DataChange.connect(quantTableObject.setTableModel)
quantTableObject.DataSelected.connect(ParcelationPlot.colorRelativeToRegion)
quantTableObject.DataSelected.connect(Tab_1_CorrelationTable.selectRegion)
quantTableObject.DataSelected.connect(Tab_2_CorrelationTable.selectRegion)
quantTableObject.DataSelected.connect(widget.NodeSelected)

Tab_1_CorrelationTable.selectedRegionChanged.connect(quantTableObject.setRegions)
ParcelationPlot.widget = widget

print "Setting up Graph interface"

Graph_Layout=LayoutInit(widget,quantTableObject,ui,dataSetLoader,screenshot,matrix_filename\
    ,template_filename,parcelation_filename)

widget.regionSelected.connect(ParcelationPlot.colorRelativeToRegion)
widget.regionSelected.connect(Tab_1_CorrelationTable.selectRegion)
widget.CommunityColor.connect(ParcelationPlot.setRegionColors)
widget.regionSelected.connect(Tab_2_CorrelationTable.selectRegion)
widget.regionSelected.connect(quantTableObject.setRegions)
widget.show()

visitViewerLayout = QtGui.QVBoxLayout()
viewersLayout2.addLayout(visitViewerLayout)

"""Window for correlation Table"""
window_CorrelationTable =QtGui.QWidget()
Box = QtGui.QHBoxLayout()
Box.addWidget(Tab_1_CorrelationTable)
Box.setContentsMargins(0, 0, 0, 0)

window_CorrelationTable.setLayout(Box)
window_CorrelationTable.setWindowTitle("CorrelationTable")

window_CorrelationTable.resize(Offset*(Counter)-0,Offset*(Counter)+170)

Tab_2_CorrelationTable.hide()
BoxTable = QtGui.QHBoxLayout()
BoxTable.setContentsMargins(0, 0, 0, 0)
BoxTable.addWidget(window_CorrelationTable)
BoxTable.addWidget(Tab_2_CorrelationTable)
BoxTable.addWidget(widget.wid)
BoxTable.setContentsMargins(0, 0, 0, 0)

BoxTableWidget.setLayout(BoxTable)

if CorrelationTableShowFlag:
    BoxTableWidget.show()
    # pass

print "Setting up Graph Layout_interface"

Graph = QtGui.QHBoxLayout()
Graph.setContentsMargins(0, 0, 0, 0)
Graph.addWidget(widget.wid)
Graph.addWidget(Graph_Layout)
Graph.setContentsMargins(0, 0, 0, 0)

BoxGraphWidget.setLayout(Graph)

if GraphWindowShowFlag:
    BoxGraphWidget.show()

"""Window for correlation Table"""
print "Setting up Signals and Slots" 

widget.CommunityColorAndDict.connect(Tab_1_CorrelationTable.setRegionColors)
widget.CommunityColorAndDict.connect(Tab_2_CorrelationTable.setRegionColors)
widget.CommunityMode.connect(ParcelationPlot.Community)

# Code clicking the group button in the slide
def buttonGroupClicked(number):
    buttons = buttonGroup.buttons()
    for button in buttons:
        if buttonGroup.button(number) != button:
            button.setChecked(False)
        else:
            if button.isChecked() == False: 
                button.setChecked(True)
                return
    if number == -2: 
        ParcelationPlot.setCentroidMode()
    else:
        ParcelationPlot.setRegionMode()

# Laying out the group buttons in visit plot
box = QtGui.QHBoxLayout()
buttonGroup = QtGui.QButtonGroup()
buttonGroup.setExclusive(True)
buttonGroup.buttonClicked[int].connect(buttonGroupClicked)

# Another Feature Online 
MapMetrics = QtGui.QCheckBox("Map Graph Metrics")
MapMetrics.toggle()
MapMetrics.hide()
MapMetrics.stateChanged.connect(ParcelationPlot.MapGraphMetrics)

def setCentroidOn():
    MapMetrics.show()

def setCentroidOff():
    MapMetrics.hide()

r0=QtGui.QRadioButton("Centroids")
r1=QtGui.QRadioButton("Regions")
r1.setChecked(True)
# Define regions 
r0.clicked.connect(ParcelationPlot.setCentroidMode)
r0.clicked.connect(setCentroidOn)
r1.clicked.connect(ParcelationPlot.setRegionMode)
r1.clicked.connect(setCentroidOff)

buttonGroup.addButton(r0)
buttonGroup.addButton(r1)
box.addWidget(r0)
box.addWidget(r1)

for sv in slice_views:
    widget.regionSelected.connect(sv.colorRelativeToRegion)
    Tab_1_CorrelationTable.selectedRegionChanged.connect(sv.colorRelativeToRegion)
    sv.regionSelected.connect(Tab_1_CorrelationTable.selectRegion)
    sv.regionSelected.connect(Tab_2_CorrelationTable.selectRegion)
    sv.regionSelected.connect(widget.NodeSelected)
    sv.regionSelected.connect(quantTableObject.setRegions)

    for sv_other in slice_views:
        if sv == sv_other:
            continue 
        sv.regionSelected.connect(sv_other.colorRelativeToRegion)
        
    widget.CommunityColor.connect(sv.setRegionColors)
    widget.CommunityMode.connect(sv.Community)
    quantTableObject.DataSelected.connect(sv.colorRelativeToRegion)


visitViewerLayout.addWidget(ParcelationPlot)
visitViewerLayout.setContentsMargins(0,0,0,0)
visitViewerLayout.addLayout(box)
visitViewerLayout.setContentsMargins(0,0,0,0)

visitControlsLayout = QtGui.QHBoxLayout()
visitViewerLayout.addLayout(visitControlsLayout)
visitViewerLayout.setContentsMargins(0,0,0,0)

toggleThreeSliceButton = QtGui.QCheckBox("Show Slices")
toggleThreeSliceButton.toggle()
visitControlsLayout.addWidget(toggleThreeSliceButton)

toggleThreeSliceButton.stateChanged.connect(ParcelationPlot.toggleThreeSlice)
toggleBrainSurfaceButton = QtGui.QCheckBox("Show Brain Surface")
toggleBrainSurfaceButton.toggle()

visitControlsLayout.addWidget(MapMetrics)
visitControlsLayout.setContentsMargins(0,0,0,0)

visitControlsLayout.addWidget(toggleBrainSurfaceButton)
visitControlsLayout.setContentsMargins(0,0,0,0)

toggleBrainSurfaceButton.stateChanged.connect(ParcelationPlot.toggleBrainSurface)
# pickButton = QtGui.QPushButton("Pick Region")

# visitControlsLayout.addWidget(pickButton)
visitControlsLayout.setContentsMargins(0,0,0,0)

# pickButton.clicked.connect(ParcelationPlot.EnablePicking)
ParcelationPlot.regionSelected.connect(Tab_1_CorrelationTable.selectRegion)
ParcelationPlot.regionSelected.connect(widget.NodeSelected)
ParcelationPlot.regionSelected.connect(Tab_2_CorrelationTable.selectRegion)
ParcelationPlot.regionSelected.connect(quantTableObject.setRegions)

for sv in slice_views:
    ParcelationPlot.regionSelected.connect(sv.regionSelected)

if MainWindowShowFlag:
    main.show()

sys.exit(app.exec_())