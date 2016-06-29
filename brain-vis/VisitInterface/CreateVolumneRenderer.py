import vtk
from vtk.util import numpy_support
import os
import numpy

import vtk
from numpy import *
import nibabel as nib
import numpy as np
import csv

import sys
import PySide
from PySide import QtCore, QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.qt.QVTKRenderWindowInteractor import *

class MouseInteractorHighLightActor(vtk.vtkInteractorStyleTrackballCamera):
 
    def __init__(self,parent=None):
        self.AddObserver("LeftButtonPressEvent",self.leftButtonPressEvent)
 
        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()
 
    def leftButtonPressEvent(self,obj,event):
        clickPos = self.GetInteractor().GetEventPosition()
        pos = self.GetInteractor().GetPicker().GetPickPosition()
 
        picker = vtk.vtkPropPicker()
        WorldPicker = vtk.vtkWorldPointPicker()

        picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
        WorldPicker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
        
        self.PickedActor = picker.GetActor()

        # get the new
        self.NewPickedActor = picker.GetActor()
        print self.NewPickedActor
 
 	
        # If something was selected
        if self.NewPickedActor:
            # If we picked something before, reset its property
            if self.LastPickedActor:
                self.LastPickedActor.GetProperty().DeepCopy(self.LastPickedProperty)
 
 
            # Save the property of the picked TemplateActor so that we can
            # restore it next time
            self.LastPickedProperty.DeepCopy(self.NewPickedActor.GetProperty())
            # Highlight the picked TemplateActor by changing its properties
            self.NewPickedActor.GetProperty().SetDiffuseColor(0.0, 1.0, 0.0)
            self.NewPickedActor.GetProperty().SetDiffuse(1.0)
            self.NewPickedActor.GetProperty().SetSpecular(0.0)
            # save the last picked TemplateActor
            self.LastPickedActor = self.NewPickedActor
 
        self.OnLeftButtonDown()
        return

# A simple function to be called when the user decides to quit the application.
def exitCheck(obj, event):
	if obj.GetEventPending() != 0:
		obj.SetAbortRender(1)

class VolumneRendererWindow(PySide.QtGui.QWidget):
	regionSelected = QtCore.Signal(int)

	def __init__(self,parcelation_filename, template_filename,correlationTable,selectedColor,colorTable):
		super(VolumneRendererWindow,self).__init__()

		self.correlationTable = correlationTable

		self.nRegions = len(self.correlationTable.header)
		self.selectedColor = selectedColor

		self.colorTable = colorTable
		self.region_data = nib.load(parcelation_filename).get_data().astype(np.uint8)
		self.Centroid = dict()

		self.regionPlotId = -1
		self.centroidPlotId = -1
		self.activePlotId = -1

		self.activePlotId = self.regionPlotId

		self.parcelation_filename = parcelation_filename
		self.template_filename = template_filename

		self.setCentreFilename()

		self.frame = QtGui.QFrame()
		self.BoxLayoutView = QtGui.QVBoxLayout()

		self.BoxLayoutView.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.BoxLayoutView)
		self.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)

		self.setDataset()
		self.setFlags()
		self.RenderData()

		# Create source
		source = vtk.vtkSphereSource()
		source.SetCenter(0, 0, 0)
		source.SetRadius(5.0)

		self.FinalRenderView() 
		self.show()

	def setCentreFilename(self):
		"""
		Logic to check whether there is a filename, if there is 
		just load the file otherwise make sure that a new file is generated 
		which is very much dataset specific 
		"""

		self.CentrePath = os.environ['PYTHONPATH'].split(os.pathsep)
		head, tail = os.path.split(self.parcelation_filename)
		tail = tail.replace(".","") 
		CenterFile = '%s%s'% (str(tail),str('CentreFile.csv'))
		self.CentrePath[0]+='/CentreData/'+CenterFile

		if os.path.isfile(self.CentrePath[0]):
			self.centroidFilename = self.CentrePath[0]
			with open(self.CentrePath[0],'rb') as f:
				r = csv.reader(f, delimiter=' ')
				for index,row in enumerate(r):
					self.Centroid[index] = row
		else:
			print "No Centre File Detected,\nComputing Centres for the Parcelation Plot\nPlease Wait"
			i,j,k = np.shape(self.region_data)
			Centroid = dict()
			counter = 0
			cx=0
			cy=0
			cz=0
			for q in range(i):
				for w in range(j):
					for e in range(k):
						value = self.region_data[q,w,e]
						try:
							if value>0:
								Centroid[value]
							else:
								continue
						except KeyError:
							Centroid[value] = ((0,0,0),0)
						Centroid[value] = ((Centroid[value][0][0]+q,Centroid[value][0][1]+w,Centroid[value][0][2]+e),Centroid[value][1]+1)

			NewChanges = dict()

			# Warning the parcel centres are converted to integer values, this might \
			#affect the uncertaininty associated with the visualization
			for i,j in Centroid.iteritems():
				Centroid[i] = (int(j[0][0]/j[1]), int(j[0][1]/j[1]), int(j[0][2]/j[1]), 1)

			with open(self.CentrePath[0],'wb') as f:
				w = csv.writer(f, delimiter=' ')
				for i,j in Centroid.iteritems():
					w.writerow([int(j[0]),int(j[1]),int(j[2])])
			self.Centroid = Centroid
			self.centroidFilename = self.CentrePath[0]

	def setFlags(self):
		self.setCentroidModeFlag = False
		self.toggleBrainSurfaceFlag = True
		self.toggleThreeSlicesFlag = True
		self.communityMode = False
		self.PickingFlag = True

	def setDataset(self): 
		self.ParcelationReader = vtk.vtkNIFTIImageReader()
		self.TemplateReader = vtk.vtkNIFTIImageReader()

		self.Templatedmc =vtk.vtkDiscreteMarchingCubes()
		self.dmc =vtk.vtkDiscreteMarchingCubes()

		self.Template = vtk.vtkPolyData()
		self.Parcelation = vtk.vtkPolyData()

		self.appendFilter = vtk.vtkAppendPolyData()
		self.cleanFilter = vtk.vtkCleanPolyData()

		self.mapper = vtk.vtkPolyDataMapper()
		self.TemplateMapper = vtk.vtkPolyDataMapper()
		self.ParcelationMapper = vtk.vtkPolyDataMapper()

		self.mapper2 = vtk.vtkPolyDataMapper()

		self.outline = vtk.vtkOutlineFilter()

		self.TemplateActor = vtk.vtkActor()
		self.ParcelationActor = vtk.vtkActor()
		self.OutlineActor = vtk.vtkActor()

		self.renderer = vtk.vtkRenderer()

		self.renderer.SetBackground(1, 1, 1)
		# self.renderer.SetViewport(0, 0, 1, 1)

		self.renderWin = vtk.vtkRenderWindow()
		self.renderWin.AddRenderer(self.renderer)

		self.axesActor = vtk.vtkAnnotatedCubeActor()
		self.axes = vtk.vtkOrientationMarkerWidget()

		self.renderInteractor = QVTKRenderWindowInteractor(self,rw=self.renderWin)
		self.BoxLayoutView.addWidget(self.renderInteractor)

		self.colorsTemplate = vtk.vtkUnsignedCharArray()
		self.colorsTemplate.SetNumberOfComponents(3)

		self.colorsParcelation = vtk.vtkUnsignedCharArray()
		self.colorsParcelation.SetNumberOfComponents(3)

		self.points = vtk.vtkPoints()
		self.triangles = vtk.vtkCellArray()

		self.picker = vtk.vtkCellPicker()

		self.lut = vtk.vtkLookupTable()
		self.lut.SetNumberOfTableValues(7)

		self.template_data = None
		self.parcelation_data = None



	def RenderData(self):
		self.DefineTemplateDataToBeMapped()
		self.DefineParcelationDataToBeMapped()
		self.MergeTwoDatasets()
		# self.SetColors()
		self.AppendDatasets()
		self.SetActorsAndOutline()
		self.SetRenderer()
		self.AddAxisActor()

	def FinalRenderView(self):
		# Tell the application to use the function as an exit check.
		self.renderWin.AddObserver("AbortCheckEvent", exitCheck)
		self.renderInteractor.Initialize()
		self.renderWin.Render()
		self.renderInteractor.Start()

	def DefineTemplateDataToBeMapped(self):
		self.TemplateReader.SetFileName(self.template_filename)
		self.Templatedmc.SetInputConnection(self.TemplateReader.GetOutputPort())
		self.Templatedmc.Update()
		self.template_data = self.Templatedmc.GetOutput()

	def DefineParcelationDataToBeMapped(self):
		self.ParcelationReader.SetFileName(self.parcelation_filename)
		self.dmc.SetInputConnection(self.ParcelationReader.GetOutputPort())
		self.dmc.Update()
		self.parcelation_data = self.dmc.GetOutput()

	def MergeTwoDatasets(self):
		self.Template.ShallowCopy(self.template_data)
		self.Parcelation.ShallowCopy(self.parcelation_data)

	def AppendDatasets(self):
		self.TemplateMapper.SetInputConnection(self.Templatedmc.GetOutputPort())
		self.ParcelationMapper.SetInputConnection(self.dmc.GetOutputPort())
		
		self.ParcelationMapper.SetLookupTable(self.lut)
		self.ParcelationMapper.SetScalarModeToUseCellData()

	def SetActorsAndOutline(self):
		self.TemplateActor.SetMapper(self.TemplateMapper)
		self.ParcelationActor.SetMapper(self.ParcelationMapper)

		# outline
		if vtk.VTK_MAJOR_VERSION <= 5:
			self.outline.SetInputData(self.Templatedmc.GetOutput())
		else:
			self.outline.SetInputConnection(self.Templatedmc.GetOutputPort())

		if vtk.VTK_MAJOR_VERSION <= 5:
			self.mapper2.SetInput(self.outline.GetOutput())
		else:
			self.mapper2.SetInputConnection(self.outline.GetOutputPort())

		self.OutlineActor.SetMapper(self.mapper2)
		self.OutlineActor.GetProperty().SetColor(0,0,0)

	def SetColors(self):
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
		lut.Build()


	def AddAxisActor(self):
		self.axesActor.SetXPlusFaceText('X')
		self.axesActor.SetXMinusFaceText('X-')
		self.axesActor.SetYMinusFaceText('Y')
		self.axesActor.SetYPlusFaceText('Y-')
		self.axesActor.SetZMinusFaceText('Z')
		self.axesActor.SetZPlusFaceText('Z-')
		self.axesActor.GetTextEdgesProperty().SetColor(1,1,0)
		self.axesActor.GetTextEdgesProperty().SetLineWidth(2)
		self.axesActor.GetCubeProperty().SetColor(0,0,1)
		self.axes.SetOrientationMarker(self.axesActor)
		self.axes.SetInteractor(self.renderInteractor)
		self.axes.EnabledOn()
		self.axes.InteractiveOn()
		self.renderer.ResetCamera()

	def SetRenderer(self):
		# With almost everything else ready, its time to 
		#initialize the renderer and window, as well as 
		#creating a method for exiting the application

		self.TemplateActor.GetProperty().SetColor(1.0, 0.4, 0.4)
		self.TemplateActor.GetProperty().SetOpacity(0.1)

		if self.toggleBrainSurfaceFlag:
			self.renderer.AddViewProp(self.TemplateActor)
		else:
			self.renderer.RemoveActor(self.TemplateActor)

		if not(self.setCentroidModeFlag): 
			self.renderer.AddViewProp(self.ParcelationActor)
		else: 
			self.addSpheres()

		if self.toggleThreeSlicesFlag: 
			pass
		else: 
			pass

		if self.PickingFlag:
			# set Picker
			self.style = MouseInteractorHighLightActor()
			self.style.SetDefaultRenderer(self.renderer)
			self.renderInteractor.SetInteractorStyle(self.style)	
		else:
			self.style = None
			self.renderInteractor.SetInteractorStyle(self.style)

		self.renderer.AddViewProp(self.OutlineActor)
		self.renderInteractor.SetRenderWindow(self.renderWin)

	def addSpheres(self):
		point = vtk.vtkPoints()
		for i in range(self.nRegions):
			# random position and radius
			x = float(self.Centroid[i][0]) 
			y = float(self.Centroid[i][1]) 
			z = float(self.Centroid[i][2]) 
			radius = 5
			point.InsertNextPoint(x,y,z)

		implicitPolyDataDistance = vtk.vtkImplicitPolyDataDistance()
		implicitPolyDataDistance.SetInput(self.Templatedmc.GetOutput())

		# Add distances to each point
		signedDistances = vtk.vtkFloatArray()
		signedDistances.SetNumberOfComponents(1)
		signedDistances.SetName("SignedDistances")

		# Evaluate the signed distance function at all of the grid points
		for pointId in range(point.GetNumberOfPoints()):
			p = point.GetPoint(pointId)
			signedDistance = implicitPolyDataDistance.EvaluateFunction(p)
			signedDistances.InsertNextValue(signedDistance)

		PolyData = vtk.vtkPolyData()
		PolyData.SetPoints(point)
		PolyData.GetPointData().SetScalars(signedDistances)

		GlyphFilter = vtk.vtkVertexGlyphFilter()

		if vtk.VTK_MAJOR_VERSION <= 5:
			GlyphFilter.AddInput(PolyData)
		else:
			GlyphFilter.AddInputData(PolyData)
		
		GlyphFilter.Update()

		PointsMapper = vtk.vtkPolyDataMapper()
		PointsMapper.SetInputConnection(GlyphFilter.GetOutputPort())
		PointsMapper.ScalarVisibilityOn()

		PointsActor = vtk.vtkActor()
		PointsActor.SetMapper(PointsMapper)

		# PointsActor.GetProperty().setPointSize(5)
		self.renderer.AddViewProp(PointsActor)
		# source.SetRadius(radius)
		# source.SetCenter(x,y,z)
		# # source.SetPhiResolution(11)
		# # source.SetThetaResolution(21)

		# mapper = vtk.vtkPolyDataMapper()
		# mapper.SetInputConnection(source.GetOutputPort())
		# actor = vtk.vtkActor()
		# actor.SetMapper(mapper)

		# r = vtk.vtkMath.Random(.4, 1.0)
		# g = vtk.vtkMath.Random(.4, 1.0)
		# b = vtk.vtkMath.Random(.4, 1.0)
		# actor.GetProperty().SetDiffuseColor(r, g, b)
		# actor.GetProperty().SetDiffuse(.8)
		# actor.GetProperty().SetSpecular(.5)
		# actor.GetProperty().SetSpecularColor(1.0,1.0,1.0)
		# actor.GetProperty().SetSpecularPower(30.0)

		# self.renderer.AddActor(actor)

	"""
	Interactive slots that need the help of an external caller method 
	"""
	def setCentroidMode(self):
		self.setCentroidModeFlag = True
		self.SetRenderer()

	def setRegionMode(self):
		self.setCentroidModeFlag = False
		self.SetRenderer()

	def	toggleBrainSurface(self):	
		self.toggleBrainSurfaceFlag = not(self.toggleBrainSurfaceFlag)
		self.SetRenderer()

	def	toggleThreeSlice(self):
		self.toggleThreeSlicesFlag = not(self.toggleThreeSlicesFlag)
		self.SetRenderer()

	def	EnablePicking(self):
		self.PickingFlag = not(self.PickingFlag)
		self.SetRenderer()

	def setRegionColors(self,region_colors):
		assert len(region_colors) == self.nRegions
		# Always use 256 colors since otherwise VisIt's color mapping does
		# not always match expected results
		# Colors: Background: black, region colors as passed by caller,
		#         fill up remaining colors with black
		colors = [ (0, 0, 0, 255) ]  + region_colors + [ (0, 0, 0, 255) ] * ( 256 - self.nRegions - 1)

	def colorRelativeToRegion(self, regionId):
		self.regionId = regionId
		if not(self.communityMode):
			region_colors = [ self.colorTable.getColor(self.correlationTable.value(regionId, i)) for i in range(self.nRegions) ]
			region_colors[regionId] = self.selectedColor
			self.setRegionColors(region_colors)

	def Community(self, Flag):
		self.communityMode = Flag
		# self.colorRelativeToRegion(self.regionId)

	def setThreeSliceX(self, sliceX):
		pass
		# visit.SetActivePlots(self.threeslice_id)
		# tsatts = visit.GetOperatorOptions(0)
		# tsatts.x = sliceX
		# visit.SetOperatorOptions(tsatts)
		# visit.DrawPlots()

	def setThreeSliceY(self, sliceY):
		pass
		# visit.SetActivePlots(self.threeslice_id)
		# tsatts = visit.GetOperatorOptions(0)
		# tsatts.y = sliceY
		# visit.SetOperatorOptions(tsatts)
		# visit.DrawPlots()

	def setThreeSliceZ(self, sliceZ):
		pass
		# visit.SetActivePlots(self.threeslice_id)
		# tsatts = visit.GetOperatorOptions(0)
		# tsatts.z = sliceZ
		# visit.SetOperatorOptions(tsatts)
		# visit.DrawPlots()		




