# Python packages
import numpy as np
from PySide import QtCore, QtGui
import re
import tempfile
import time
import visit
from color_table import *

import vtk
from vtk.util import numpy_support
import os
import numpy

import vtk
from numpy import *
import nibabel as nib
import numpy as np

from PyQt4 import QtCore, QtGui
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class MouseInteractorHighLightActor(vtk.vtkInteractorStyleTrackballCamera):
 
    def __init__(self,parent=None):
        self.AddObserver("LeftButtonPressEvent",self.leftButtonPressEvent)
 
        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()
 
    def leftButtonPressEvent(self,obj,event):
        clickPos = self.GetInteractor().GetEventPosition()
 
        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
 
        # get the new
        self.NewPickedActor = picker.GetActor()
        print self.NewPickedActor
 
        # If something was selected
        if self.NewPickedActor:
            # If we picked something before, reset its property
            if self.LastPickedActor:
                self.LastPickedActor.GetProperty().DeepCopy(self.LastPickedProperty)
 
 
            # Save the property of the picked actor so that we can
            # restore it next time
            self.LastPickedProperty.DeepCopy(self.NewPickedActor.GetProperty())
            # Highlight the picked actor by changing its properties
            self.NewPickedActor.GetProperty().SetColor(0.0, 1.0, 0.0)
            self.NewPickedActor.GetProperty().SetDiffuse(1.0)
            self.NewPickedActor.GetProperty().SetSpecular(0.0)
 
            # save the last picked actor
            self.LastPickedActor = self.NewPickedActor
 
        self.OnLeftButtonDown()
        return

size = 5

template_filename = '/Users/sugeerthmurugesan/LBLProjects/ELectrode/SummerProject/JesseDataset/ch2better.nii.gz'
parcelation_filename = '/Users/sugeerthmurugesan/LBLProjects/ELectrode/SummerProject/JesseDataset/allROIs.nii.gz'

ParcelationReader = vtk.vtkNIFTIImageReader()
TemplateReader = vtk.vtkNIFTIImageReader()

Templatedmc =vtk.vtkDiscreteMarchingCubes()
dmc =vtk.vtkDiscreteMarchingCubes()

Template = vtk.vtkPolyData()
Parcelation = vtk.vtkPolyData()

#  print data 

appendFilter = vtk.vtkAppendPolyData()
cleanFilter = vtk.vtkCleanPolyData()

mapper = vtk.vtkPolyDataMapper()
TemplateMapper = vtk.vtkPolyDataMapper()
ParcelationMapper = vtk.vtkPolyDataMapper()

mapper2 = vtk.vtkPolyDataMapper()

outline = vtk.vtkOutlineFilter()

actor = vtk.vtkActor()
actor1 = vtk.vtkActor()
actor2 = vtk.vtkActor()

renderer = vtk.vtkRenderer()
renderWin = vtk.vtkRenderWindow()

axesActor = vtk.vtkAnnotatedCubeActor()
axes = vtk.vtkOrientationMarkerWidget()


renderInteractor = vtk.vtkRenderWindowInteractor()

colorsTemplate = vtk.vtkUnsignedCharArray()
colorsTemplate.SetNumberOfComponents(3)

colorsParcelation = vtk.vtkUnsignedCharArray()
colorsParcelation.SetNumberOfComponents(3)

points = vtk.vtkPoints()
triangles = vtk.vtkCellArray()

picker = vtk.vtkCellPicker()

lut = vtk.vtkLookupTable()
lut.SetNumberOfTableValues(7)
nc = vtk.vtkNamedColors()
colorNames = nc.GetColorNames().split('\n')

global template_data 
global parcelation_data

def InitiatePickerForRenderer():
    style = MouseInteractorHighLightActor()
    style.SetDefaultRenderer(renderer)
    renderInteractor.SetInteractorStyle(style)

InitiatePickerForRenderer()

template_data = None
parcelation_data = None

def DefineTemplateDataToBeMapped():
    global template_data
    TemplateReader.SetFileName(template_filename)

    Templatedmc.SetInputConnection(TemplateReader.GetOutputPort())
    # dmc.GenerateValues(1, 1, 1)`
    Templatedmc.Update()
    template_data = Templatedmc.GetOutput()

def DefineParcelationDataToBeMapped():
    global parcelation_data
    ParcelationReader.SetFileName(parcelation_filename)
    dmc.SetInputConnection(ParcelationReader.GetOutputPort())
    # dmc.GenerateValues(1, 1, 1)
    dmc.Update()
    parcelation_data = dmc.GetOutput()

def MergeTwoDatasets():
    Template.ShallowCopy(template_data)
    Parcelation.ShallowCopy(parcelation_data)

def SetColors():
    rgba = list(nc.GetColor4d("Red"))
    rgba[3] = 0.5
    nc.SetColor("My Red",rgba)
    rgba = nc.GetColor4d("My Red")
    lut.SetTableValue(0,rgba)
    rgba = nc.GetColor4d("DarkGreen")
    rgba[3] = 0.3
    lut.SetTableValue(1,rgba)
    lut.SetTableValue(2,nc.GetColor4d("Blue"))
    lut.SetTableValue(3,nc.GetColor4d("Cyan"))
    lut.SetTableValue(4,nc.GetColor4d("Magenta"))
    lut.SetTableValue(5,nc.GetColor4d("Yellow"))
    # lut.SetTableRange(elevation.GetScalarRange())
    lut.Build()


def AppendDatasets():
    TemplateMapper.SetInputConnection(Templatedmc.GetOutputPort())
    ParcelationMapper.SetInputConnection(dmc.GetOutputPort())
    
    ParcelationMapper.SetLookupTable(lut)
    ParcelationMapper.SetScalarModeToUseCellData()

def SetActorsAndOutline():
    actor.SetMapper(TemplateMapper)
    actor1.SetMapper(ParcelationMapper)

    # outline
    if vtk.VTK_MAJOR_VERSION <= 5:
        outline.SetInputData(Templatedmc.GetOutput())
    else:
        outline.SetInputConnection(Templatedmc.GetOutputPort())

    if vtk.VTK_MAJOR_VERSION <= 5:
        mapper2.SetInput(outline.GetOutput())
    else:
        mapper2.SetInputConnection(outline.GetOutputPort())

    actor2.SetMapper(mapper2)

def AddAxisActor():
    axesActor.SetXPlusFaceText('X')
    axesActor.SetXMinusFaceText('X-')
    axesActor.SetYMinusFaceText('Y')
    axesActor.SetYPlusFaceText('Y-')
    axesActor.SetZMinusFaceText('Z')
    axesActor.SetZPlusFaceText('Z-')
    axesActor.GetTextEdgesProperty().SetColor(1,1,0)
    axesActor.GetTextEdgesProperty().SetLineWidth(2)
    axesActor.GetCubeProperty().SetColor(0,0,1)
    axes.SetOrientationMarker(axesActor)
    axes.SetInteractor(renderInteractor)
    axes.EnabledOn()
    axes.InteractiveOn()
    renderer.ResetCamera()

def SetRenderer():
    # With almost everything else ready, its time to initialize the renderer and window, as well as creating a method for exiting the application
    actor.GetProperty().SetColor(1.0, 0.4, 0.4)
    actor.GetProperty().SetOpacity(0.1)

    renderer.AddActor(actor)
    renderer.AddActor(actor1)
    renderer.AddActor(actor2)

    # renderer.SetBackground(1.0, 1.0, 1.0)

    renderWin.AddRenderer(renderer)
    renderInteractor.SetRenderWindow(renderWin)

    renderWin.SetSize(500, 500)

DefineTemplateDataToBeMapped()
DefineParcelationDataToBeMapped()
MergeTwoDatasets()
SetColors()
AppendDatasets()
SetActorsAndOutline()
SetRenderer()
AddAxisActor()

# A simple function to be called when the user decides to quit the application.
def exitCheck(obj, event):
    if obj.GetEventPending() != 0:
        obj.SetAbortRender(1)

# Tell the application to use the function as an exit check.
renderWin.AddObserver("AbortCheckEvent", exitCheck)
# picker.AddObserver("EndPickEvent", annotatePick)

renderInteractor.Initialize()

# picker.Pick(85, 126, 100,renderer)
# Because nothing will be rendered without any input, we order the first render manually before control is handed over to the main-loop.
renderWin.Render()

renderInteractor.Start()






























# Helper functions
def GetColor(colortable, value):
    ct = visit.GetColorTable(colortable)
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

# Save a numpy array as BOV for input in VisIt
def SaveAsBOV(data, varname):
    dataFile = tempfile.NamedTemporaryFile(suffix='.raw', delete=False)
    data.astype(np.uint8).transpose().tofile(dataFile.file)
    dataFile.close()
    headerFile = tempfile.NamedTemporaryFile(suffix='.bov', delete=False)
    headerFile.write("DATA_FILE: %s\n" % dataFile.name)
    headerFile.write("DATA_SIZE: %d %d %d\n" % data.shape)
    headerFile.write("BRICK_SIZE: %d %d %d\n" % data.shape)
    headerFile.write("DATA_FORMAT: BYTE\n")
    headerFile.write("CENTERING: zonal\n")
    headerFile.write("VARIABLE: %s\n" % varname)
    headerFile.close()
    return headerFile.name, dataFile.name

# Open a file with xyz coordinates using the PlainText reader
def OpenXYZCoordinateFile(filename):
    ### Set options to parse the file correctly ...
    opts = visit.GetDefaultFileOpenOptions("PlainText")
    opts['Data layout'] = 0
    opts['Column for X coordinate (or -1 for none)'] = 0
    opts['Column for Y coordinate (or -1 for none)'] = 1
    opts['Column for Z coordinate (or -1 for none)'] = 2
    opts['First row has variable names'] = 0
    opts['Lines to skip at beginning of file'] = 0
    visit.SetDefaultFileOpenOptions("PlainText", opts)
    ### ... and open the file
    visit.OpenDatabase(filename)

class BrainTemplatePlot(object):
    def __init__(self, template_data):
        print template_data, "This is the template data"
        self.template_headername, self.template_dataname = SaveAsBOV(template_data, 'var')
        visit.OpenDatabase(self.template_headername)
        self.contour_id = visit.GetNumPlots()
        visit.AddPlot("Contour", "var")
        catts = visit.ContourAttributes()
        catts.colorType = catts.ColorBySingleColor
        catts.legendFlag = 0
        catts.singleColor = (192, 192, 192, 64)
        catts.contourPercent = (42)
        catts.contourMethod = catts.Percent  # Level, Value, Percent
        visit.SetPlotOptions(catts)
        visit.HideActivePlots()
        self.threeslice_id = visit.GetNumPlots()
        visit.AddPlot("Pseudocolor", "var")
        patts = visit.PseudocolorAttributes()
        patts.colorTableName = "gray"
        patts.legendFlag = 0
        visit.SetPlotOptions(patts)
        visit.AddOperator("ThreeSlice")
        visit.DrawPlots()

    def __del__(self):
        # pass
        os.remove(self.template_headername)
        os.remove(self.template_dataname)

    def toggleBrainSurface(self):
        visit.SetActivePlots(self.contour_id)
        visit.HideActivePlots()

    def toggleThreeSlice(self):
        visit.SetActivePlots(self.threeslice_id)
        visit.HideActivePlots()

    def setThreeSliceX(self, sliceX):
        visit.SetActivePlots(self.threeslice_id)
        tsatts = visit.GetOperatorOptions(0)
        tsatts.x = sliceX
        visit.SetOperatorOptions(tsatts)
        visit.DrawPlots()

    def setThreeSliceY(self, sliceY):
        visit.SetActivePlots(self.threeslice_id)
        tsatts = visit.GetOperatorOptions(0)
        tsatts.y = sliceY
        visit.SetOperatorOptions(tsatts)
        visit.DrawPlots()

    def setThreeSliceZ(self, sliceZ):
        visit.SetActivePlots(self.threeslice_id)
        tsatts = visit.GetOperatorOptions(0)
        tsatts.z = sliceZ
        visit.SetOperatorOptions(tsatts)
        visit.DrawPlots()


"""
Class that Implements the parcelation plot in the anatomical view
Talks to python interface of the Visit to run easy visualizations 
"""
class ParcelationPlot(QtCore.QObject):
    regionSelected = QtCore.Signal(int)

    def __init__(self, region_data, centroidFilename, correlationTable, colorTable, selectedColor):
        super(ParcelationPlot, self).__init__()
        self.correlationTable = correlationTable
        self.communityMode = False
        self.colorTable = colorTable
        self.selectedColor = selectedColor
        self.nRegions = len(self.correlationTable.header)

        self.regionPlotId = -1
        self.centroidPlotId = -1
        self.activePlotId = -1

        self.setupColorTable()
        self.setupRegionPlot(region_data)
        self.setupCentroidPlot(centroidFilename)
        visit.SetActivePlots(self.centroidPlotId)
        visit.HideActivePlots()
        self.centroidMode = False
        self.activePlotId = self.regionPlotId
        visit.DrawPlots()

    def __del__(self):
        # pass
        os.remove(region_headername)
        os.remove(region_dataname)

    def setupColorTable(self):
        # Create empty color table
        ccpl = visit.ColorControlPointList()
        visit.AddColorTable("parcel_color_table", ccpl)
        # Set to meaningful initial colors (everything unselected)
        self.unselectAll()

    def setCentroidMode(self):
        if not self.centroidMode:
            # Invert plot visibility
            visit.SetActivePlots((self.regionPlotId, self.centroidPlotId))
            visit.HideActivePlots()
            self.activePlotId = self.centroidPlotId
            self.centroidMode = True

    def setRegionMode(self):
        if self.centroidMode:
            # Invert plot visibility
            visit.SetActivePlots((self.regionPlotId, self.centroidPlotId))
            visit.HideActivePlots()
            self.activePlotId = self.regionPlotId
            self.centroidMode = False

    def setupRegionPlot(self, region_data):
        self.region_headername, self.region_dataname = SaveAsBOV(region_data, 'roi_id')
        visit.OpenDatabase(self.region_headername)
        self.regionPlotId = visit.GetNumPlots()
        visit.AddPlot('Pseudocolor', 'roi_id')
        patts = visit.PseudocolorAttributes()
        patts.colorTableName = "parcel_color_table"
        patts.legendFlag = 0
        patts.minFlag = 1
        patts.min = 0
        patts.maxFlag = 1
        patts.max = 255
        visit.SetPlotOptions(patts)
        visit.AddOperator("Threshold")
        tatts = visit.ThresholdAttributes()
        tatts.listedVarNames = ("roi_id")
        tatts.lowerBounds = (1)
        tatts.upperBounds = (50000)
        tatts.zonePortions = (1)
        visit.SetOperatorOptions(tatts)

    def setupCentroidPlot(self, centroidFilename):
        OpenXYZCoordinateFile(centroidFilename)
        ### Define expression for obtaining node id
        visit.DefineScalarExpression("node_id" , "zoneid(mesh)+1")
        ## The +1 is so that counting region ids starts with one like in the region plot.

        ### Create a color table based on the community ids like on the Parcelatio
        self.centroidPlotId = visit.GetNumPlots()
        visit.AddPlot("Pseudocolor", "node_id")
        patts = visit.PseudocolorAttributes()
        patts.colorTableName = "parcel_color_table"  ## Change this to the color table name from the parcellation plot
        patts.pointType = patts.Sphere
        patts.pointSizePixels = 20
        patts.legendFlag = 0
        patts.minFlag = 1
        patts.min = 0
        patts.maxFlag = 1
        patts.max = 255
        visit.SetPlotOptions(patts)
        visit.AddOperator("Threshold")
        tatts = visit.ThresholdAttributes()
        tatts.listedVarNames = ("node_id")
        tatts.lowerBounds = (1)
        tatts.upperBounds = (50000)
        tatts.zonePortions = (1)
        visit.SetOperatorOptions(tatts)

    def setRegionColors(self,region_colors):
        assert len(region_colors) == self.nRegions


        # Always use 256 colors since otherwise VisIt's color mapping does
        # not always match expected results
        # Colors: Background: black, region colors as passed by caller,
        #         fill up remaining colors with black
        colors = [ (0, 0, 0, 255) ]  + region_colors + [ (0, 0, 0, 255) ] * ( 256 - self.nRegions - 1)

        # Construct VisIt color control point list and set it as color table
        ccpl = visit.ColorControlPointList()
        ccpl.smoothing = ccpl.None
        for i, color in enumerate(colors):
            cp = visit.ColorControlPoint()
            cp.position = float(i) / 255.
            cp.colors = color
            ccpl.AddControlPoints(cp)
        visit.SetColorTable("parcel_color_table", ccpl)

    def unselectAll(self):
        # Set color of all regions to gray
        self.setRegionColors([(128, 128, 128, 255)] * self.nRegions)

    def colorRelativeToRegion(self, regionId):
        self.regionId = regionId
        # print self.CommunityMode, regionId
        if not(self.communityMode):
            region_colors = [ self.colorTable.getColor(self.correlationTable.value(regionId, i)) for i in range(self.nRegions) ]
            region_colors[regionId] = self.selectedColor
            self.setRegionColors(region_colors)

    def Community(self, Flag):
        self.communityMode = Flag
            # self.colorRelativeToRegion(self.regionId)

    def makeActive(self):
        visit.SetActivePlots(self.activePlotId)

    def performPick3D(self):
        visit.RegisterCallback("PickAttributes")
        pattern = re.compile('<zonal> = \d*')
        match = pattern.search(visit.GetPickOutput())
        if match != None:
            try:
                regionId = int(match.group(0).split('=')[1]) - 1
                self.regionSelected.emit(regionId)
                visit.SetWindowMode("navigate")
            except:
                pass

    def startPick3D(self):
        visit.RegisterCallback("PickAttributes", lambda pa: self.performPick3D())
        self.makeActive()
        visit.SetWindowMode("zone pick")

### Set up VisIt settings for plots
# Turn off annotations
annAtts = visit.GetAnnotationAttributes()
annAtts.userInfoFlag = 0
annAtts.databaseInfoFlag = 0
annAtts.timeInfoFlag = 0
annAtts.axes3D.visible = 0
annAtts.axes3D.triadFlag = 0
visit.SetAnnotationAttributes(annAtts)

# Never use scalable rendering, always use display lists for speed up
ratts = visit.GetRenderingAttributes()
ratts.displayListMode = ratts.Always
ratts.scalableActivationMode = ratts.Never
visit.SetRenderingAttributes(ratts)

# Disable output for picking
pickAtts = visit.GetPickAttributes()
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
visit.SetPickAttributes(pickAtts)
visit.SuppressQueryOutputOn()

# Initial view
view3D = visit.GetView3D()
view3D.viewNormal = (0, 1, 0)
view3D.viewUp = (0, 0, 1)

visit.SetView3D(view3D)
