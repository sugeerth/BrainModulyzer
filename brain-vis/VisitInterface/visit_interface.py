# Python packages
import numpy as np
from PySide import QtCore, QtGui
import re
import tempfile
import time
import visit
from color_table import *

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
