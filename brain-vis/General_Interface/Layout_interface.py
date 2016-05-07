import csv
import sys
import math
from collections import defaultdict
from PySide import QtCore, QtGui
from sys import platform as _platform
import weakref
import cProfile
import os

"""A central interface that links all the UIs in the widgets to their respective
functionalities in the classes """
class LayoutInit(QtGui.QWidget):
    def __init__(self,widget,quantTable,Ui,dataSetLoader,screenshot,matrix_filename,centre_filename,centres_abbreviation,template_filename,parcelation_filename, Brain_image_filename=None,Electrode_Ids_filename=None,SelectedElectrodes_filename=None,Electrode_data_filename=None,Electrode_mat_filename=None):
        super(LayoutInit,self).__init__()

        self.matrix_filename=matrix_filename
        self.centre_filename=centre_filename
        self.centres_abbreviation =centres_abbreviation
        self.template_filename=template_filename
        self.parcelation_filename=parcelation_filename
        self.Ui = Ui
        self.classVariable(widget, Ui, dataSetLoader,screenshot)
        self.widgetChanges()
        self.dialogueConnect()

        Node_Label= QtGui.QLabel('Edge Weight Threshold')
        
        Ui.highlightEdges.stateChanged.connect(widget.changeHighlightedEdges)
        Ui.colorEdges.stateChanged.connect(widget.changeTitle)
        Ui.preservePositions.stateChanged.connect(widget.changeSpringLayout)
        Ui.springLayout.clicked.connect(widget.LayoutCalculation)
        Ui.Layout.activated[str].connect(widget.SelectLayout)
        Ui.correlation.activated[str].connect(widget.SelectNodeColor)
        Ui.hover.stateChanged.connect(widget.hoverChanged)
        Ui.transparent.stateChanged.connect(widget.changeTransparency)
        Ui.NodeSize.activated[str].connect(widget.setNodeSizeOption)
        Ui.Thickness.valueChanged[int].connect(widget.changeEdgeThickness)
        Ui.communityLevel.valueChanged[int].connect(widget.changeDendoGramLevel)
        Ui.dataSet.clicked.connect(self.openFileDialog)
        Ui.getSnapshots.clicked.connect(self.getSnapshots)
        Ui.snapshot.clicked.connect(self.captureSnapshot)
        Ui.quantTable.addWidget(quantTable)

        Ui.communityLevelLineEdit.returnPressed.connect(widget.LevelLineEditChanged)
        Ui.communityLevelLineEdit.setText('1')
        
        self.horizontalLayout = QtGui.QGridLayout()
        self.horizontalLayout.setSpacing(1)
        self.horizontalLayout.addWidget(Node_Label,0,0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.addWidget(widget.EdgeSliderForGraph,0,1)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.addWidget(widget.Lineditor,0,101,0,102)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        hbox = QtGui.QVBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(widget)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addLayout(self.horizontalLayout)
        hbox.setContentsMargins(0, 0, 0, 0)

        bbbox = QtGui.QHBoxLayout()
        bbbox.setContentsMargins(0, 0, 0, 0)

        Ui.setMinimumSize(271,431)
        bbbox.addWidget(Ui)
        bbbox.setContentsMargins(0, 0, 0, 0)

        bbbox.addLayout(hbox)
        hbox.setContentsMargins(0, 0, 0, 0)
        bbbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(bbbox)

    def classVariable(self,widget,Ui,dataSetLoader,screenshot):
        self.widget = widget
        self.Ui = Ui 
        self.dataSetLoader = dataSetLoader
        self.screenshot= screenshot

    def widgetChanges(self):
        self.widget.setMinimumSize(400, 400)
        self.widget.slider_imple()
        # Enabling node slider for analysis 
        # self.widget.NodeSlider()
        self.widget.lineEdit()

    def captureSnapshot(self):
        """ Logic to capture all the parameters for the data visualization """
        
        # Code graciously taken from the Qt website 
        msgBox = QtGui.QMessageBox()
        msgBox.setText("Capturing the snapshot.")
        msgBox.setInformativeText("Do you want to capture the parameters of the visualization?")
        msgBox.setStandardButtons(QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel)
        msgBox.setDefaultButton(QtGui.QMessageBox.Save)
        ret = msgBox.exec_()

        if ret == QtGui.QMessageBox.Save:
            pass

    def getSnapshots(self):
        """ Logic to retrieve the snapshots from the output file """
        self.screenshot.show()

    """ Dataset specific functions """
    def openFileDialog(self):
        """
        Opens a file dialog and sets the label to the chosen path
        """
        self.dataSetLoader.show()
        self.setPathForData()

    def clickLineEdit(self,Flag):
        path, _ = QtGui.QFileDialog.getOpenFileName(self, "Open File", os.getcwd())
        if Flag == "centres_abbreviation": 
            self.centres_abbreviation = path
        else: 
            exec("%s='%s'" % (('self.'+Flag+'_filename'), path))

        print path, "Dataset that is already there"
        self.setPathForData()

    def dialogueConnect(self):
        self.dataSetLoader.matrix.clicked.connect(lambda: self.clickLineEdit("matrix"))
        self.dataSetLoader.center.clicked.connect(lambda: self.clickLineEdit("centre"))
        self.dataSetLoader.abbrev.clicked.connect(lambda: self.clickLineEdit("centres_abbreviation"))
        self.dataSetLoader.parcel.clicked.connect(lambda: self.clickLineEdit("parcelation"))
        self.dataSetLoader.template1.clicked.connect(lambda: self.clickLineEdit("template"))

    def SliderValueChanged(self,MaxDendoGramDepth):
        self.Ui.communityLevel.setMaximum(MaxDendoGramDepth+1)

    def setPathForData(self):
        self.dataSetLoader.matrixPath.setText(self.matrix_filename)
        self.dataSetLoader.centerPath.setText(self.centre_filename)
        self.dataSetLoader.abbrevPath.setText(self.centres_abbreviation)
        self.dataSetLoader.parcelPath.setText(self.parcelation_filename)
        self.dataSetLoader.templatePath.setText(self.template_filename)
        """Logic to send the new files to the start of the applicaiton """