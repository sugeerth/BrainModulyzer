import vtk
from vtk.util import numpy_support
import os
import numpy

import vtk
from numpy import *
import nibabel as nib
import numpy as np
import csv
import math
import sys
import tempfile
import pprint
import sys
import PySide
from PySide import QtCore, QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.qt.QVTKRenderWindowInteractor import *

class MouseInteractorHighLightActor(vtk.vtkInteractorStyleTrackballCamera):

	def __init__(self,VolumneRendererWindow, selectedColor, PixX, PixY, PixZ):
		super(MouseInteractorHighLightActor, self).__init__()

		self.selectedColor = selectedColor
		self.VolumneRendererWindow = VolumneRendererWindow

		self.AddObserver("LeftButtonPressEvent",self.leftButtonPressEvent)

		self.PixX = PixX
		self.PixY = PixY
		self.PixZ = PixZ
		self.LastPickedActor = None
		self.LastPickedProperty = vtk.vtkProperty()

	def leftButtonPressEvent(self,obj,event):
		clickPos = self.GetInteractor().GetEventPosition()
		pos = self.GetInteractor().GetPicker().GetPickPosition()
		picker = vtk.vtkPropPicker()
		picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
		# get the new
		self.NewPickedActor = picker.GetActor()
		"""
		Idea is to compare the xyz locations with the numpy parcels to get the 
		selected Id 
		"""
		# If something was selected
		if self.NewPickedActor:
			# If we picked something before, reset its property
			if self.LastPickedActor:
				self.LastPickedActor.GetProperty().DeepCopy(self.LastPickedProperty)
			# Save the property of the picked TemplateActor so that we can
			# restore it next time
			self.LastPickedProperty.DeepCopy(self.NewPickedActor.GetProperty())

			# Highlight the picked TemplateActor by changing its properties
			# self.NewPickedActor.GetProperty().SetColor(self.selectedColor)

			bounds= self.NewPickedActor.GetBounds()  
			if self.VolumneRendererWindow.setCentroidModeFlag: 
				if self.VolumneRendererWindow.SphereActors:
					index = 0
					for actor in self.VolumneRendererWindow.SphereActors:
						if actor == self.NewPickedActor:
							break
						index +=1
					self.VolumneRendererWindow.RegionSelectedIn(index)
			else:
				if self.VolumneRendererWindow.Parcel: 
					index = 0
					for actor in self.VolumneRendererWindow.Parcel:
						if actor == self.NewPickedActor:
							break
						index +=1
					self.VolumneRendererWindow.RegionSelectedIn(index-1)
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

	def __init__(self,parcelation_filename, template_filename,correlationTable,selectedColor,colorTable,SliceX,SliceY,SliceZ):
		super(VolumneRendererWindow,self).__init__()

		self.correlationTable = correlationTable

		self.nRegions = len(self.correlationTable.header)
		self.selectedColor = selectedColor

		self.widget = None
		self.SliceX = SliceX
		self.SliceY = SliceY
		self.SliceZ = SliceZ

		self.colorTable = colorTable
		self.region_data = nib.load(parcelation_filename).get_data().astype(np.uint32)
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

		self.CentrePath = sys.path[0].split(os.pathsep)
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
		self.MapMetrics = False
		self.SphereActors = []
		self.Parcel = []
		self.Slices = [None,None,None]
		self.region_colors = None

		self.SetXAxisValues = 0 
		self.SetYAxisValues = 0 
		self.SetZAxisValues = 0 
		
		#PixelDimensions Spacing
		self.PixX = 0
		self.PixY = 0
		self.PixZ = 0

	def ColorParcelationPoints(self,x,y,z):
		self.Parcelation

	def setDataset(self): 
		self.ParcelationNumpy = nib.load(self.parcelation_filename).get_data().astype(np.uint8)
		self.TemplateNumpy = nib.load(self.template_filename).get_data().astype(np.uint8)

		img1 = nib.load(self.parcelation_filename)
		img2 = nib.load(self.template_filename)
		
		hdr1 = img1.header
		hdr2 = img2.header

		a1 = hdr1['pixdim'][1:4]
		a2 = hdr2['pixdim'][1:4]

		self.ParcelationNumpy.shape

		self.PixX = 1
		self.PixY = 1
		self.PixZ = 1

		self.ParcelationReader = vtk.vtkImageImport()
		self.ParcelationReader = copy.deepcopy(self.ParcelationNumpy)
		self.StrParcelationNumpy = str(self.ParcelationNumpy)
		
		self.ParcelationReader.SetImportVoidPointer(self.StrParcelationNumpy, len(self.StrParcelationNumpy) * 32)

		self.ParcelationReader.SetDataScalarTypeToUnsignedChar()

		print np.shape(self.ParcelationNumpy)
		x,y,z = np.shape(self.ParcelationNumpy)
		self.ParcelationReader.SetDataExtent(0,x-1,0,y-1,0,z-1)
		self.ParcelationReader.SetWholeExtent(0,x-1,0,y-1,0,z-1)
		
		self.TemplateReader = vtk.vtkImageImport()
		self.StrTemplateNumpy = str(self.TemplateNumpy)
		self.TemplateReader.CopyImportVoidPointer(self.StrTemplateNumpy, len(self.StrTemplateNumpy))
		self.TemplateReader.SetDataScalarTypeToUnsignedChar()

		x,y,z = np.shape(self.TemplateNumpy)
		self.TemplateReader.SetDataExtent(0,x-1,0,y-1,0,z-1)
		self.TemplateReader.SetWholeExtent(0,x-1,0,y-1,0,z-1)


		if vtk.VTK_MAJOR_VERSION <= 5:
			self.ParcelationReader = vtk.vtkNIFTIImageReader()
		else:
			self.ParcelationReader = vtk.vtkNIFTIImageReader()

		self.ParcelationReader.SetFileName(self.parcelation_filename)
		self.ParcelationNumpy = nib.load(self.parcelation_filename).get_data().astype(np.uint8)
		self.ParcelationReader.Update()

		self.TemplateReader = vtk.vtkNIFTIImageReader()
		self.TemplateReader.SetFileName(self.template_filename)

		self.TemplateNumpy = nib.load(self.template_filename).get_data().astype(np.uint8)
		self.TemplateReader.Update()


		self.Templatedmc =vtk.vtkDiscreteMarchingCubes()
		self.dmc =vtk.vtkDiscreteMarchingCubes()

		self.TemplateMapper = vtk.vtkPolyDataMapper()
		self.mapper2 = vtk.vtkPolyDataMapper()
		self.outline = vtk.vtkOutlineFilter()

		self.TemplateActor = vtk.vtkActor()
		self.OutlineActor = vtk.vtkActor()

		self.renderer = vtk.vtkRenderer()
		self.renderer.SetBackground(1, 1, 1)

		self.renderWin = vtk.vtkRenderWindow()
		self.renderWin.AddRenderer(self.renderer)

		self.axes2 = vtk.vtkCubeAxesActor2D()
		self.axes3 = vtk.vtkCubeAxesActor2D()

		self.colorData = vtk.vtkUnsignedCharArray()
		self.colorData.SetName('colors') # Any name will work here.
		self.colorData.SetNumberOfComponents(3)

		self.TextProperty = vtk.vtkTextProperty()
		self.TextProperty.SetColor(0,0,0)
		self.TextProperty.SetFontSize(100)

		self.axesActor = vtk.vtkAnnotatedCubeActor()
		self.axes = vtk.vtkOrientationMarkerWidget()

		self.renderInteractor = QVTKRenderWindowInteractor(self,rw=self.renderWin)
		self.BoxLayoutView.addWidget(self.renderInteractor)

		self.picker = vtk.vtkCellPicker()
		self.template_data = None

	def RegionSelectedIn(self, Id):
		if not(Id == self.nRegions):
			self.colorRelativeToRegion(Id)
			self.regionSelected.emit(Id)

	def RenderData(self):
		self.DefineTemplateDataToBeMapped()
		self.DefineParcelationDataToBeMapped()
		self.AppendDatasets()
		self.SetActorsAndOutline()
		self.SetRenderer()
		self.AddAxisActor()
		self.SetAxisValues()

	def SetAxisValues(self):
		if vtk.VTK_MAJOR_VERSION <= 5:
			self.axes2.SetInput(self.Templatedmc.GetOutput())
		else:	
			self.axes2.SetInputConnection(self.Templatedmc.GetOutputPort())

		self.axes2.SetCamera(self.renderer.GetActiveCamera())
		self.axes2.SetLabelFormat("%6.4g")
		self.axes2.SetFlyModeToOuterEdges()
		self.axes2.SetAxisTitleTextProperty(self.TextProperty)
		self.axes2.SetAxisLabelTextProperty(self.TextProperty)
		self.axes2.GetProperty().SetColor(0,0,0)
		self.renderer.AddViewProp(self.axes2)

		if vtk.VTK_MAJOR_VERSION <= 5:
			self.axes3.SetInput(self.Templatedmc.GetOutput())
		else:	
			self.axes3.SetInputConnection(self.Templatedmc.GetOutputPort())
		self.axes3.SetCamera(self.renderer.GetActiveCamera())
		self.axes3.SetLabelFormat("%6.4g")
		self.axes3.SetFlyModeToClosestTriad()
		self.axes3.SetAxisTitleTextProperty(self.TextProperty)
		self.axes3.SetAxisLabelTextProperty(self.TextProperty)
		self.axes3.GetProperty().SetColor(0,0,0)
		self.renderer.AddViewProp(self.axes3)

	def FinalRenderView(self):
		# Tell the application to use the function as an exit check.
		self.renderWin.AddObserver("AbortCheckEvent", exitCheck)
		self.renderInteractor.Initialize()
		self.renderWin.Render()
		self.renderInteractor.Start()

	def DefineTemplateDataToBeMapped(self):
		if vtk.VTK_MAJOR_VERSION <= 5:
			self.Templatedmc.SetInput(self.TemplateReader.GetOutput())
		else:	
			self.Templatedmc.SetInputConnection(self.TemplateReader.GetOutputPort())


		self.Templatedmc.Update()

		self.template_data = self.Templatedmc.GetOutput()

	def DefineParcelationDataToBeMapped(self):
		self.PixX = self.ParcelationReader.GetNIFTIHeader().GetPixDim(1)
		self.PixY = self.ParcelationReader.GetNIFTIHeader().GetPixDim(2)
		self.PixZ = self.ParcelationReader.GetNIFTIHeader().GetPixDim(3)

		# Getting the style object to invoke here because we get the real Pix dimensions
		self.style = MouseInteractorHighLightActor(self,self.selectedColor[:3], self.PixX, self.PixY,self.PixZ)

	def AppendDatasets(self):
		if vtk.VTK_MAJOR_VERSION <= 5:
			self.Templatedmc.SetInput(self.Templatedmc.GetOutput())
		else:
			self.TemplateMapper.SetInputConnection(self.Templatedmc.GetOutputPort())


		self.TemplateMapper.ScalarVisibilityOff()

	def SetActorsAndOutline(self):
		self.TemplateActor.SetMapper(self.TemplateMapper)

		# outline
		if vtk.VTK_MAJOR_VERSION <= 5:
			self.outline.SetInput(self.Templatedmc.GetOutput())
		else:
			self.outline.SetInputConnection(self.Templatedmc.GetOutputPort())

		if vtk.VTK_MAJOR_VERSION <= 5:
			self.mapper2.SetInput(self.outline.GetOutput())
		else:
			self.mapper2.SetInputConnection(self.outline.GetOutputPort())

		self.OutlineActor.SetMapper(self.mapper2)
		self.OutlineActor.GetProperty().SetColor(0,0,0)

		self.TemplateActor.GetProperty().SetColor(1.0, 1.0, 1.0)
		self.TemplateActor.PickableOff()

		self.TemplateActor.GetProperty().SetOpacity(0.16)

		self.renderer.AddViewProp(self.OutlineActor)
		self.renderInteractor.SetRenderWindow(self.renderWin)

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

		if self.toggleBrainSurfaceFlag:
			self.renderer.AddViewProp(self.TemplateActor)
		else:
			self.renderer.RemoveActor(self.TemplateActor)

		self.addParcels()
		self.addSpheres()
		self.addSlices()

		self.UpdateRenderer()
		self.renderWin.GetInteractor().Render()

	def UpdateRenderer(self):
		if self.toggleBrainSurfaceFlag:
			self.renderer.AddViewProp(self.TemplateActor)
		else:
			self.renderer.RemoveActor(self.TemplateActor)

		if not(self.setCentroidModeFlag): 
			if self.SphereActors:
				self.UpdateSpheres(False)
			self.UpdateParcels(True)
		else: 
			if self.Parcel:
				self.UpdateParcels(False)
			self.UpdateSpheres(True)

		if self.toggleThreeSlicesFlag: 
			self.UpdateSlices(True)
		else: 
			self.UpdateSlices(False)

		if self.PickingFlag:
			# set Picker
			if self.style == None:
				self.style = MouseInteractorHighLightActor(self,self.selectedColor[:3], self.PixX, self.PixY,self.PixZ)
			self.style.SetDefaultRenderer(self.renderer)
			self.renderInteractor.SetInteractorStyle(self.style)	
		else:
			del self.style
			self.style = None
			self.renderInteractor.SetInteractorStyle(self.style)

		self.renderWin.GetInteractor().Render()


	def UpdateSlices(self,Visibility):
		for actor in self.Slices:
			if Visibility:
				actor.GetProperty().SetOpacity(1)
			else:
				actor.GetProperty().SetOpacity(0)

	def addSlices(self):
		self.addSliceX()
		self.addSliceY()
		self.addSliceZ()

	def setThreeSliceX(self, sliceX):
		self.SetXAxisValues = sliceX
		self.updateSliceX()

	def setThreeSliceY(self, sliceY):
		self.SetYAxisValues = sliceY
		self.updateSliceY()

	def setThreeSliceZ(self, sliceZ):
		# The value should be negative!
		x,y,z = self.TemplateNumpy.shape
		self.SetZAxisValues = sliceZ
		self.updateSliceZ()

	def addSliceX(self):
		if not(self.toggleThreeSlicesFlag): 
			return

		if not(self.Slices[0]== None):
			self.renderer.RemoveActor(self.Slices[0])
			self.Slices[0] = None

		self.vrange = self.TemplateReader.GetOutput().GetScalarRange()

		self.map1 = vtk.vtkImageSliceMapper()
		self.map1.BorderOn()
		self.map1.SliceAtFocalPointOff() 
		self.map1.SliceFacesCameraOff()
		self.map1.SetOrientationToX()

		if vtk.VTK_MAJOR_VERSION <= 5:
			self.map1.SetInput(self.TemplateReader.GetOutput())
		else: 
			self.map1.SetInputConnection(self.TemplateReader.GetOutputPort())

		self.map1.SetSliceNumber(0)
		self.map1.Update()

		slice1 = vtk.vtkImageSlice()
		slice1.SetMapper(self.map1)
		slice1.GetProperty().SetColorWindow(self.vrange[1]-self.vrange[0])
		slice1.GetProperty().SetColorLevel(0.4*(self.vrange[0]+self.vrange[1]))

		self.Slices[0] = slice1

		self.renderer.AddViewProp(slice1)
		self.renderWin.GetInteractor().Render()

	def updateSliceX(self):
		if not(self.toggleThreeSlicesFlag): 
			return

		if not(self.Slices[0]== None):
			self.renderer.RemoveActor(self.Slices[0])
			self.Slices[0] = None

		self.map1.SetSliceNumber(self.SetXAxisValues)

		slice1 = vtk.vtkImageSlice()
		slice1.SetMapper(self.map1)
		slice1.GetProperty().SetColorWindow(self.vrange[1]-self.vrange[0])
		slice1.GetProperty().SetColorLevel(0.4*(self.vrange[0]+self.vrange[1]))

		self.Slices[0] = slice1

		self.renderer.AddViewProp(slice1)
		self.renderWin.GetInteractor().Render()

	def addSliceY(self):
		if not(self.toggleThreeSlicesFlag): 
			return

		if not(self.Slices[1]== None):
			self.renderer.RemoveActor(self.Slices[1])
			self.Slices[1] = None


		self.vrange = self.TemplateReader.GetOutput().GetScalarRange()

		self.map2 = vtk.vtkImageSliceMapper()
		self.map2.BorderOn()
		self.map2.SliceAtFocalPointOff()
		self.map2.SliceFacesCameraOff()
		self.map2.SetOrientationToY()
		if vtk.VTK_MAJOR_VERSION <= 5:
			self.map2.SetInput(self.TemplateReader.GetOutput())
		else:
			self.map2.SetInputConnection(self.TemplateReader.GetOutputPort())

		self.map2.SetSliceAtFocalPoint(0)

		slice1 = vtk.vtkImageSlice()
		slice1.SetMapper(self.map2)
		slice1.GetProperty().SetColorWindow(self.vrange[1]-self.vrange[0])
		slice1.GetProperty().SetColorLevel(0.5*(self.vrange[0]+self.vrange[1]))

		self.Slices[1] = slice1
		self.renderer.AddViewProp(slice1)
		self.renderWin.GetInteractor().Render()

	def updateSliceY(self):
		if not(self.toggleThreeSlicesFlag): 
			return

		if not(self.Slices[1]== None):
			self.renderer.RemoveActor(self.Slices[1])
			self.Slices[1] = None

		self.map2.SetSliceNumber(self.SetYAxisValues)

		slice1 = vtk.vtkImageSlice()
		slice1.SetMapper(self.map2)
		slice1.GetProperty().SetColorWindow(self.vrange[1]-self.vrange[0])
		slice1.GetProperty().SetColorLevel(0.5*(self.vrange[0]+self.vrange[1]))

		self.Slices[1] = slice1

		self.renderer.AddViewProp(slice1)
		self.renderWin.GetInteractor().Render()

	def addSliceZ(self):
		if not(self.toggleThreeSlicesFlag): 
			return

		if not(self.Slices[2]== None):
			self.renderer.RemoveActor(self.Slices[2])
			self.Slices[2] = None

		self.map3 = vtk.vtkImageSliceMapper()
		self.map3.BorderOn()
		self.map3.SliceAtFocalPointOff()
		self.map3.SliceFacesCameraOff()
		self.map3.SetOrientationToZ()
		if vtk.VTK_MAJOR_VERSION <= 5:
			self.map3.SetInput(self.TemplateReader.GetOutput())
		else: 
			self.map3.SetInputConnection(self.TemplateReader.GetOutputPort())
		

		self.map3.SetSliceNumber(0)

		slice1 = vtk.vtkImageSlice()
		slice1.SetMapper(self.map3)
		slice1.GetProperty().SetColorWindow(self.vrange[1]-self.vrange[0])
		slice1.GetProperty().SetColorLevel(0.5*(self.vrange[0]+self.vrange[1]))

		self.Slices[2] = slice1
		self.renderer.AddViewProp(slice1)
		self.renderWin.GetInteractor().Render()

	def updateSliceZ(self):
		if not(self.toggleThreeSlicesFlag): 
			return

		if not(self.Slices[2]== None):
			self.renderer.RemoveActor(self.Slices[2])
			self.Slices[2] = None

		self.map3.SetSliceNumber(self.SetZAxisValues)

		slice1 = vtk.vtkImageSlice()
		slice1.SetMapper(self.map3)
		slice1.GetProperty().SetColorWindow(self.vrange[1]-self.vrange[0])
		slice1.GetProperty().SetColorLevel(0.5*(self.vrange[0]+self.vrange[1]))

		self.Slices[2] = slice1

		self.renderer.AddViewProp(slice1)
		self.renderWin.GetInteractor().Render()

	def removeParcels(self):
		if self.Parcel:
			for actor in self.Parcel:
				self.renderer.RemoveActor(actor)
			del self.Parcel
			self.Parcel = None

	def removeSpheres(self):
		if self.SphereActors:
			for actor in self.SphereActors:
				self.renderer.RemoveActor(actor)
			del self.SphereActors
			self.SphereActors = None

	def addParcels(self):
		self.removeParcels()
		self.Parcel = []
		for i in range(self.nRegions):
			dmc =vtk.vtkDiscreteMarchingCubes()
			if vtk.VTK_MAJOR_VERSION <= 5:
				dmc.SetInput(self.ParcelationReader.GetOutput())
			else:
				dmc.SetInputConnection(self.ParcelationReader.GetOutputPort())

			dmc.GenerateValues(i,i,i)
			dmc.Update()

			mapper = vtk.vtkPolyDataMapper()
			if vtk.VTK_MAJOR_VERSION <= 5:
				mapper.SetInput(dmc.GetOutput())
			else:			
				mapper.SetInputConnection(dmc.GetOutputPort())

			mapper.ScalarVisibilityOff()

			actor = vtk.vtkActor()
			actor.SetMapper(mapper)

			if self.region_colors:
				r = float(self.region_colors[i][0])/255
				g = float(self.region_colors[i][1])/255
				b = float(self.region_colors[i][2])/255
			else:
				r= 0.1
				b= 0.1
				g= 0.1

			actor.GetProperty().SetColor(r,g,b)
			# actor.GetProperty().SetDiffuse(.8)
			# actor.GetProperty().SetSpecular(.5)
			actor.GetProperty().SetSpecularColor(1.0,1.0,1.0)
			# actor.GetProperty().SetSpecularPower(30.0)
			self.Parcel.append(actor)
			self.renderer.AddViewProp(actor)

	def addSpheres(self):
		self.removeSpheres()
		self.SphereActors = []
		for i in range(self.nRegions):
			source = vtk.vtkSphereSource()
			# random position and radius
			x = float(self.Centroid[i][0])* self.PixX 
			y = float(self.Centroid[i][1])* self.PixY 
			z = float(self.Centroid[i][2])* self.PixZ 
		
			radius = 10

			if self.MapMetrics:
				Size = eval('self.widget.'+self.widget.nodeSizeFactor+'[i]')
				radius*= Size
				if radius < 5: 
					radius = 5  
				elif radius > 10: 
					radius = 10  
				else:
					radius*= Size 
			else: 
				radius = 5

			source.SetRadius(radius)
			source.SetCenter(x,y,z)

			mapper = vtk.vtkPolyDataMapper()
			if vtk.VTK_MAJOR_VERSION <= 5:
				mapper.SetInput(source.GetOutput())
			else:	
				mapper.SetInputConnection(source.GetOutputPort())

			mapper.ScalarVisibilityOff()

			actor = vtk.vtkActor()
			actor.SetMapper(mapper)

			if self.region_colors:
				r = float(self.region_colors[i][0])/255
				g = float(self.region_colors[i][1])/255
				b = float(self.region_colors[i][2])/255
			else:
				r= 0.1
				b= 0.1
				g= 0.1
			actor.GetProperty().SetColor(r, g, b)
			actor.GetProperty().SetSpecularColor(1.0,1.0,1.0)
			self.SphereActors.append(actor)
			self.renderer.AddViewProp(actor)
		self.renderWin.GetInteractor().Render()


	def UpdateSpheres(self, Visibility):
		for i in range(self.nRegions):
			if self.SphereActors:
				actor = self.SphereActors[i]
				if not(Visibility): 
					actor.GetProperty().SetOpacity(0)
					continue
			if self.region_colors:
				r = float(self.region_colors[i][0])/255
				g = float(self.region_colors[i][1])/255
				b = float(self.region_colors[i][2])/255
			else:
				r= 0.1
				b= 0.1
				g= 0.1

			actor.GetProperty().SetColor(r, g, b)
			actor.GetProperty().SetSpecularColor(1.0,1.0,1.0)
			actor.GetProperty().SetOpacity(1)
		self.renderWin.GetInteractor().Render()

	def UpdateParcels(self,Visibility):
		for i in range(self.nRegions):
			if self.Parcel:
				actor = self.Parcel[i]
				if not(Visibility): 
					actor.GetProperty().SetOpacity(0)
					continue
			if self.region_colors:
				r = float(self.region_colors[i-1][0])/255
				g = float(self.region_colors[i-1][1])/255
				b = float(self.region_colors[i-1][2])/255
			else:
				r= 0.1
				b= 0.1
				g= 0.1
			actor.GetProperty().SetColor(r, g, b)
			actor.GetProperty().SetOpacity(1)
			actor.GetProperty().SetDiffuse(.8)
			actor.GetProperty().SetSpecular(.5)
			actor.GetProperty().SetSpecularColor(1.0,1.0,1.0)
			actor.GetProperty().SetSpecularPower(30.0)

		self.renderWin.GetInteractor().Render()

	"""
	Interactive slots that need the help of an external caller method 
	"""
	def setCentroidMode(self):
		self.setCentroidModeFlag = True
		self.UpdateRenderer()

	def setRegionMode(self):
		self.setCentroidModeFlag = False
		self.UpdateRenderer()

	def	toggleBrainSurface(self):	
		self.toggleBrainSurfaceFlag = not(self.toggleBrainSurfaceFlag)
		self.UpdateRenderer()

	def	toggleThreeSlice(self):
		self.toggleThreeSlicesFlag = not(self.toggleThreeSlicesFlag)
		self.UpdateRenderer()

	def setRegionColors(self,region_colors):
		assert len(region_colors) == self.nRegions
		self.region_colors = region_colors
		self.UpdateRenderer()

	def colorRelativeToRegion(self, regionId):
		self.regionId = regionId
		if not(self.communityMode):
			region_colors = [ self.colorTable.getColor(self.correlationTable.value(regionId, i)) for i in range(self.nRegions) ]
			region_colors[regionId] = self.selectedColor
			self.setRegionColors(region_colors)	

	def MapGraphMetrics(self):
		self.MapMetrics = not(self.MapMetrics)
		self.addSpheres()
		self.UpdateRenderer()

	def Community(self, Flag):
		self.communityMode = Flag

