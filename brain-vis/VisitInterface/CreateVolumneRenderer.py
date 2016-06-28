import vtk
from vtk.util import numpy_support
import os
import numpy

import vtk
from numpy import *
import nibabel as nib
import numpy as np

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
 
 
            # Save the property of the picked TemplateActor so that we can
            # restore it next time
            self.LastPickedProperty.DeepCopy(self.NewPickedActor.GetProperty())
            # Highlight the picked TemplateActor by changing its properties
            self.NewPickedActor.GetProperty().SetColor(0.0, 1.0, 0.0)
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

	def __init__(self,parcelation_filename, template_filename):
		super(VolumneRendererWindow,self).__init__()

		self.parcelation_filename = parcelation_filename
		self.template_filename = template_filename

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

	def setFlags(self):
		self.setCentroidMode = False
		self.toggleBrainSurface = True


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
		self.renderer.SetViewport(0, 0, 1, 1)

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

		# set Picker
		self.style = MouseInteractorHighLightActor()
		self.style.SetDefaultRenderer(self.renderer)
		self.renderInteractor.SetInteractorStyle(self.style)

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

		if self.toggleBrainSurface:
			self.renderer.AddActor(self.TemplateActor)
		else:
			pass

		if self.setCentroidMode: 
			self.renderer.AddActor(self.ParcelationActor)
		else: 
			self.addSpheres()

		self.renderer.AddActor(self.OutlineActor)
		self.renderInteractor.SetRenderWindow(self.renderWin)

	def addSpheres(self):
		pass

	"""
	Interactive slots that need the help of an external caller method 
	"""
	def setCentroidMode(self):
		self.setCentroidMode = True
		self.SetRenderer()

	def setRegionMode(self):
		self.setCentroidMode = False
		self.SetRenderer()

	def	toggleBrainSurface(self):	
		self.toggleBrainSurface = not(self.toggleBrainSurface)
		self.SetRenderer()






