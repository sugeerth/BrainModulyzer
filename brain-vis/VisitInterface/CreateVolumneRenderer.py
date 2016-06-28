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
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
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

# A simple function to be called when the user decides to quit the application.
def exitCheck(obj, event):
	if obj.GetEventPending() != 0:
		obj.SetAbortRender(1)

class VolumneRendererWindow(PySide.QtGui.QWidget):
 
	def __init__(self,parcelation_filename, template_filename,VolumneFrame, BoxLayoutView, vtkWidget):
		super(VolumneRendererWindow,self).__init__()
		print "Here is not something"

		self.parcelation_filename = parcelation_filename
		self.template_filename = template_filename
		
		print "Here is not something"

		self.frame = VolumneFrame
		self.BoxLayoutView = BoxLayoutView
		self.vtkWidget = vtkWidget
		print "Here is not something"

		self.setDataset()
		self.RenderData()

		# Create source
		source = vtk.vtkSphereSource()
		source.SetCenter(0, 0, 0)
		source.SetRadius(5.0)

		self.frame.setLayout(self.BoxLayoutView)
		self.setCentralWidget(self.frame)

		self.FinalRenderView() 
		# self.iren.Initialize()
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

		self.actor = vtk.vtkActor()
		self.actor1 = vtk.vtkActor()
		self.actor2 = vtk.vtkActor()

		self.renderer = vtk.vtkRenderer()
		self.renderWin = vtk.vtkRenderWindow()

		# self.vtkWidget = QVTKRenderWindowInteractor(self.frame)

		self.myViewer.GetRenderWindow()

		self.BoxLayoutView.addWidget(self.vtkWidget)

		self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)

		self.axesActor = vtk.vtkAnnotatedCubeActor()
		self.axes = vtk.vtkOrientationMarkerWidget()

		# self.renderInteractor = vtk.vtkRenderWindowInteractor()
		self.renderInteractor = self.vtkWidget.GetRenderWindow().GetInteractor()

		self.colorsTemplate = vtk.vtkUnsignedCharArray()
		self.colorsTemplate.SetNumberOfComponents(3)

		self.colorsParcelation = vtk.vtkUnsignedCharArray()
		self.colorsParcelation.SetNumberOfComponents(3)

		self.points = vtk.vtkPoints()
		self.triangles = vtk.vtkCellArray()

		self.picker = vtk.vtkCellPicker()

		self.lut = vtk.vtkLookupTable()
		self.luts.SetNumberOfTableValues(7)
		self.nc = vtk.vtkNamedColors()
		self.colorNames = nc.GetColorNames().split('\n')

		self.template_data = None
		self.parcelation_data = None

		# set Picker
		self.style = MouseInteractorHighLightActor()
		self.style.SetDefaultRenderer(self.renderer)
		self.renderInteractor.SetInteractorStyle(style)

	def RenderData(self):
		self.DefineTemplateDataToBeMapped()
		self.DefineParcelationDataToBeMapped()
		self.MergeTwoDatasets()
		self.SetColors()
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
		self.actor.SetMapper(self.TemplateMapper)
		self.actor1.SetMapper(self.ParcelationMapper)

		# outline
		if vtk.VTK_MAJOR_VERSION <= 5:
			self.outline.SetInputData(self.Templatedmc.GetOutput())
		else:
			self.outline.SetInputConnection(self.Templatedmc.GetOutputPort())

		if vtk.VTK_MAJOR_VERSION <= 5:
			self.mapper2.SetInput(self.outline.GetOutput())
		else:
			self.mapper2.SetInputConnection(self.outline.GetOutputPort())

		self.actor2.SetMapper(self.mapper2)

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
		self.axes.SetOrientationMarker(axesActor)
		self.axes.SetInteractor(renderInteractor)
		self.axes.EnabledOn()
		self.axes.InteractiveOn()
		self.renderer.ResetCamera()

	def SetRenderer(self):
		# With almost everything else ready, its time to 
		#initialize the renderer and window, as well as 
		#creating a method for exiting the application

		self.actor.GetProperty().SetColor(1.0, 0.4, 0.4)
		self.actor.GetProperty().SetOpacity(0.1)

		self.renderer.AddActor(actor)
		self.renderer.AddActor(actor1)
		self.renderer.AddActor(actor2)

		# self.renderer.SetBackground(1.0, 1.0, 1.0)

		self.renderWin.AddRenderer(renderer)
		self.renderInteractor.SetRenderWindow(renderWin)

		self.renderWin.SetSize(500, 500)





