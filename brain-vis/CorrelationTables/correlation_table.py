import csv
import numpy as np
import pprint
import weakref
import tempfile
import time
import math
import copy
from PySide import QtCore, QtGui
import json
from pprint import pprint
import scipy.io
import numpy as np
import community as cm
import pprint
import os,sys
from random import randint
import networkx as nx
import pydot 
import bct
import Pycluster
import pickle 
import pyparsing
import numpy
import csv

"""
This is the data that needs to be changed based on the format of the data
"""
weight = 0
ThresholdValue = 0

width = 1280,
height = 800;

Nodes = 21 
Timestep = 205

class CommunityDataProcessing(object):
    def __init__(self):
        self.communityData = None
        self.timestepPartition = None

    def ModelGraph(self, NumpyGraphData, Timestep):
        low_values_indices = None
        ThresholdData = np.copy(NumpyGraphData[Timestep])
        ThresholdData = nx.from_numpy_matrix(ThresholdData) 
        return ThresholdData

    def get_Pos_Neg_Partition(self,Graph):
        GraphData=nx.to_numpy_matrix(Graph)
        partitionArray = bct.modularity_louvain_und(GraphData)
        partition = dict()
        for i,data in enumerate(partitionArray[0]): 
            partition[i] = data 
        return partition

    def defineCommunities(self, CommunityGraph, data):
        newdata = np.array(data)
        partitionArray = bct.modularity_louvain_und(newdata)
        partition = dict()
        for i,data in enumerate(partitionArray[0]): 
            partition[i] = data 
        
        # Method to get the associated hierarchy associated with the hierarchy 
        # partitionHierarchyArray = bct.modularity_louvain_und(newdata, hierarchy = True)

        # for i,data in enumerate(partitionArray[0]): 
        #     partition[i] = data 

        return partition

class dataProcessing(object):
    def __init__(self,filename):
        """
        Loading Static files onto the repository
        """
        self.CommunityObject = CommunityDataProcessing()
        self.filename = filename
        self.MatRenderData = self.loadSyntheticDatasets()
        self.communityHashmap = dict()

        for i in range(Timestep):
            self.communityHashmap[i] = self.GenerateCommunities(self.MatRenderData,i)

    def GenerateCommunities(self,Data, Timestep): 
        GraphForCommunity = self.CommunityObject.ModelGraph(Data, Timestep) 
        ThresholdData = nx.to_numpy_matrix(GraphForCommunity)
        CommunityHashmap = self.CommunityObject.defineCommunities(GraphForCommunity,ThresholdData) 

    def getCommunityData(self, Time):
        return self.communityHashmap[Time]

    def loadSyntheticDatasets(self): 
        """
        Loads the enron dataset into the datastructure to show 

        graphData == 0--10 timesteps with nodes, edges and changes in graphs. 
        Idea to find out how the community structure cahnges and what happens 
        to the overall topology
        """
        with open(self.filename) as f: 
            array=numpy.zeros((21,21))
            i = 0 
            counter = 0
            arraylist = numpy.zeros((205,21,21),dtype=np.float64)
            for line in f: 
                line = line.strip()
                data = np.array(map(float,line.split(' ')))
                for k,data1 in enumerate(data):
                    if counter== 0 and i == 1 and k ==0:
                        savedValue = data1
                    arraylist[counter][i][k] = np.float64(data1)
                i = i+1 
                if (i == 21):
                    counter = counter+1
                    i = 0
        return arraylist

    def returnDynamicData(self):
        return self.RenderData


"""Class responsible for transferring data from files to self.data"""
class CorrelationTable(object):
    def __init__(self, filename, dataProcess=None):
        self.header = None
        self.AbbrName = []
        self.data = []
        self.RegionName = []
        self.dataProcess = dataProcessing(filename)
                
        self.data = self.dataProcess.MatRenderData[0] 
        self.header = [str(i) for i in range(Nodes)]
        self.RegionName.append(self.header)

        # with open(filename, 'rb') as csvfile:
        #     reader = csv.reader(csvfile, delimiter=',', quotechar='\'')
        #     self.header = reader.next()
        #     self.RegionName.append((self.header))
        #     self.data=np.array([map(float, line) for line in reader])

    """
    Function for finding the absolute value of correlation values 
    """
    def FindAbsoluteValue(self):
        for i in range(len(self.data)):
            for j in range(len(self.data)):
                self.data[i,j] = abs(self.data[i,j])

    def changeTableContents(self,TimeStep):
        self.data = self.dataProcess.MatRenderData[TimeStep] 
        # self.data = self.dataProcess.ElectodeData[Syllable][TimeStep]
        """
        Correlation values here are actually mean shifted. This varies from 
        application to application
        WE can eventually make this something intelligent
        """
    def value(self, i, j):
        return self.data[i, j]

    def valueRange(self):
        return (self.data.min(), self.data.max())

"""Class acting as a parent class for CorrelationTableDisplay and CommunityCorrelationTableDisplay 
Common Functions are implemented in these classes
 Pseudo Code
detect communities using the louvain algorithm 
For every brain region a community is assigned 
sort the brain regions based on community number 
Initialize colors using maximum perceptive distance with the number of communities as an upper bound 
assign these colors to every brain region
assign brain region labels using the sorted order for both row and column 

initialize entries of the matrix as 
 empty when no edges are in between row i and column j and brain region i and regions j does not belong to the same community
 the community color provided that the brain region i and brain region j belong to the same community and have edges between them 
 if the threshold is changed perform this again  
deference every community to their respective 
Set the labels of the matrix"""



class ParentCommunityDisplay(QtGui.QTableWidget): 

    def sortDataStructure(self,Order,Brain_Regions):

        self.ClusteredOrder = None
        self.sortedValues =  []
        self.sortedOrder = []

        """ Sorting the Data structure for both the data structure"""
        self.ClusteredOrder = [Brain_Regions[key] for key,value in Order.iteritems()]
        self.sortedOrder = [key for key,value in Order.iteritems()]
        self.sortedValues = [value for key,value in Order.iteritems()]


    def Singleselection(self):

        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.itemSelectionChanged.disconnect(self.handleSelection)
        self.itemSelectionChanged.connect(self.handleSelectionChange) 

    """Logic for selection of multiple cells and displaying selected cells into a new window"""
    def MultiSelection(self):

        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.itemSelectionChanged.disconnect(self.handleSelectionChange)
        self.itemSelectionChanged.connect(self.handleSelection)

    """ Selecting cells by toggling Key T"""
    def keyPressEvent(self, event):

        key = event.key()
        if key == QtCore.Qt.Key_T:
            self.ToggleSelection()

    """ Toggling the selection of cells in the adjacency matrix """
    def ToggleSelection(self):
        #Switching between different selection modes 
        self.Selectionmode = not(self.Selectionmode)

        if self.Selectionmode:
            self.Singleselection()
        else: 
            self.MultiSelection()

    def handleSelection(self):
        regionIDS = self.selectedItems()


    """ Toggling the selection of cells in the adjacency matrix """
    def ToggleSelection(self):
        #Switching between different selection modes 
        self.Selectionmode = not(self.Selectionmode)

        if self.Selectionmode:
            self.Singleselection()
        else: 
            self.MultiSelection()



    """ Function for setting the region colors of the adjacency matrix"""
    def setRegionColors(self,colors,partition):
        """
        The function is called when communities are detected and colors are passed   
        """
        self.CommunityMode = True
        n = len(self.correlationTable.header)
        # Fix me hardcoded values for values of N 
        if n < 50:
                CellSize= 40
        else: 
                CellSize = 4

        self.colors = colors
        for key, value in sorted(partition.iteritems(), key=lambda (k,v): (v,k)):
            self.sortedDict[value].append(key)

        from collections import OrderedDict
        self.Order = OrderedDict(sorted(partition.items(), key=lambda t: t[1]))
        self.ChangeColors()

""""Defining class for Magnified correlationTable"""
class NewWindowCorrelationTableDisplay(ParentCommunityDisplay):

    class BackgroundDelegate(QtGui.QStyledItemDelegate):
        def paint(self, painter, option, index):
            painter.fillRect(option.rect, index.data(QtCore.Qt.BackgroundRole))
            super(NewWindowCorrelationTableDisplay.BackgroundDelegate, self).paint(painter, option, index)

            if option.state & QtGui.QStyle.State_Selected:
                painter.save()
                # Changed to Green
                pen = QtGui.QPen(QtCore.Qt.darkGreen, 2, QtCore.Qt.SolidLine, QtCore.Qt.SquareCap, QtCore.Qt.MiterJoin)
                myrect = option.rect.adjusted(0, 1, 0, 0)
                painter.setPen(pen)
                painter.setPen(pen)
                painter.drawLine(myrect.topLeft(), myrect.topRight())
                painter.drawLine(option.rect.bottomRight() , option.rect.bottomLeft())
                painter.drawLine(myrect.topLeft(), myrect.bottomLeft())
                painter.drawLine(option.rect.topRight() + QtCore.QPoint(0, 2), option.rect.bottomRight()+ QtCore.QPoint(0, -2))
                painter.restore()

    def __init__(self,m,n,LowVerticalHeader,HighVerticalHeader,LowHoizontalHeader,HighHorizontalHeader,CorrelationTable,regionIDS):
        super(NewWindowCorrelationTableDisplay, self).__init__(m, n)

        CellSize = 18

        if CorrelationTable.CommunityMode:
            self.setVerticalHeaderLabels([''.join(CorrelationTable.ClusteredOrder[key]) for key in range(LowVerticalHeader ,HighVerticalHeader+1)])
            self.setHorizontalHeaderLabels(['\n'.join(CorrelationTable.ClusteredOrder[key]) for key in range(LowHoizontalHeader,HighHorizontalHeader+1)])

        else: 
            self.setVerticalHeaderLabels([''.join(CorrelationTable.Brain_Regions[key]) for key in range(LowVerticalHeader ,HighVerticalHeader+1)])
            self.setHorizontalHeaderLabels(['\n'.join(CorrelationTable.Brain_Regions[key]) for key in range(LowHoizontalHeader,HighHorizontalHeader+1)])

        for i in range(n+1):
            self.setColumnWidth(i,CellSize)

        for i in range(m+1):
            self.setRowHeight(i,CellSize) 

        for column in range(n):
            for row in range(m):
                table_item = CorrelationTable.item(regionIDS[column*m + row][0],regionIDS[column*m + row][1])
                table_item_new = QtGui.QTableWidgetItem()
                table_item_new.setBackground(table_item.background())
                table_item_new.setToolTip(table_item.toolTip())
                self.setItem(row, column, table_item_new)
        self.setSizePolicy(QtGui.QSizePolicy.Policy.Expanding, QtGui.QSizePolicy.Policy.Expanding)
        self.setShowGrid(False)
        self.setStyleSheet("selection-background-color: transparent;")
        self.setItemDelegate(self.BackgroundDelegate())

# Counter 2 is community correlation table 
# Counter 1 is Correlation Table 
""" Classes responsible for creaitng the Matrix """
class CorrelationTableDisplay(ParentCommunityDisplay):
    selectedRegionChanged = QtCore.Signal(int)

    class BackgroundDelegate(QtGui.QStyledItemDelegate):
        def paint(self, painter, option, index):
            painter.fillRect(option.rect, index.data(QtCore.Qt.BackgroundRole))
            super(CorrelationTableDisplay.BackgroundDelegate, self).paint(painter, option, index)
            if option.state & QtGui.QStyle.State_Selected:
                painter.save()
                # Pointer to green
                pen = QtGui.QPen(QtCore.Qt.darkGreen, 2, QtCore.Qt.SolidLine, QtCore.Qt.SquareCap, QtCore.Qt.MiterJoin)
                myrect = option.rect.adjusted(0, 1, 0, 0)
                painter.setPen(pen)
                painter.drawLine(myrect.topLeft(), myrect.topRight())
                painter.drawLine(myrect.bottomLeft(), myrect.bottomRight())
                if index.column() == 0:
                    painter.drawLine(myrect.topLeft(), myrect.bottomLeft())
                if index.column() == index.model().columnCount()-1:
                    painter.drawLine(option.rect.topRight() + QtCore.QPoint(0, -1), option.rect.bottomRight()+ QtCore.QPoint(0, -1))
                painter.restore()

    """ Initialize variables"""
    def __init__(self, correlationTable, colorTable, GraphDataStructure):
        n = len(correlationTable.header)
        super(CorrelationTableDisplay, self).__init__(n, n)
        from collections import defaultdict
        start_time = time.time()
        self.CommunityMode = False 
        self.MouseReleased = True
        self.colorTable = colorTable
        self.sortedDict= defaultdict(list)
        self.newWindowWidget = []
        self.Selectionmode = True
        self.GraphDataStructure = weakref.ref(GraphDataStructure)
        self.data = self.GraphDataStructure().ThresholdData
        self.Order = []
        self.i = 0 
        self.setContentsMargins(0, 0, 0, 0)
        self.newwidget = None
        self.Brain_Regions = correlationTable.RegionName[0]
        self.First = True
        self.g= []
        self.isElementSorted = False
        # self.queue =queue

        ## If "counter" value is 1 it represents adjacency matrix "counter" value is 0 represents correlation
        self.ColorNumpyArray = np.empty([len(self.GraphDataStructure().ThresholdData),len(self.GraphDataStructure().ThresholdData),3])

        self.correlationTable = correlationTable
        self.setVerticalHeaderLabels(self.correlationTable.header)
        self.setHorizontalHeaderLabels(['\n'.join(name) for name in self.correlationTable.header])

        self.setMinimumSize(800,400)
        
        font = QtGui.QFont()
        font.setPointSize(8)
        self.horizontalHeader().setFont(font)
        self.verticalHeader().setFont(font)

        if n < 50:
                CellSize= 40
        else: 
                CellSize = 4

        for i in range(n):
            self.setColumnWidth(i,CellSize) 
            self.setRowHeight(i, CellSize)
            self.resizeRowToContents(i);
            self.horizontalHeaderItem(i).setToolTip(self.correlationTable.header[i])
            self.verticalHeaderItem(i).setToolTip(self.correlationTable.header[i])

        # self.verticalHeader().hide()
        # self.horizontalHeader().hide()

        self.resizeColumnsToContents();
        
        for i in range(len(self.correlationTable.header)):
            for j in range(len(self.correlationTable.header)):
                table_item = QtGui.QTableWidgetItem()
                # if self.counter == 1: 
                t = self.correlationTable.value(i, j)
                self.ColorNumpyArray[i,j] = self.colorTable.getColor(t)[0:3]
                table_item.setBackground(QtGui.QColor(self.ColorNumpyArray[i,j][0],self.ColorNumpyArray[i,j][1],self.ColorNumpyArray[i,j][2]))
                table_item.setToolTip("%s, %s, %g" % (self.Brain_Regions[i] ,self.Brain_Regions[j],self.correlationTable.data[i, j]))

                self.setItem(i, j, table_item)

        # self.setSizePolicy(QtGui.QSizePolicy.Policy.Expanding, QtGui.QSizePolicy.Policy.Expanding)
        self.setShowGrid(False)
        self.setStyleSheet("selection-background-color: transparent;")
        self.setItemDelegate(self.BackgroundDelegate())
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.itemSelectionChanged.connect(self.handleSelectionChange)

    """ Logic for multiple selection of cells in the adjacency matrix"""
    def mouseReleaseEvent(self, e):
        super(CorrelationTableDisplay, self).mouseReleaseEvent(e)
        if not(self.Selectionmode):
            regionIDS =  []
            for i in self.selectedItems():
                 regionIDS.append((i.row(), i.column()))
            regionIDS = np.asarray(regionIDS)
            CorrelationTable = self

            def newwindow(BoxWidget):
                i,j = np.amin(regionIDS, axis=0)
                k,l = np.amax(regionIDS, axis=0)

                np.reshape(regionIDS,(k-i+1,l-j+1,2))
                self.bbox = QtGui.QVBoxLayout()
                # Number of region ids selected and transfered to teh new window
                NewTable = NewWindowCorrelationTableDisplay(k-i+1,l-j+1,i,k,j,l,CorrelationTable,regionIDS)
                self.bbox.addWidget(NewTable)
                BoxWidget.setLayout(self.bbox)

                # FIX me resizing table contents with hardcoded values 
                BoxWidget.resize(18*(l-j)+120,18*(k-i+1)+140)                
                # BoxWidget.resize(18*(l-j)+120,18*(k-i+1)+140)

            if self.First:
                self.newWindowWidget.append(QtGui.QWidget()) 
                newwindow(self.newWindowWidget[0])
                self.newWindowWidget[0].show()
                self.First = False
            else: 
                self.i = self.i + 1 
                self.newWindowWidget.append(QtGui.QWidget())
                newwindow(self.newWindowWidget[self.i])
                self.newWindowWidget[self.i].show()

    """ Handling changes"""
    def handleSelectionChange(self):

        regionId = self.selectedItems()[0].row()

        if self.CommunityMode: 
            if not(self.isElementSorted):
                self.selectedRegionChanged.emit(self.sortedOrder[regionId])
        else:
            if not(self.isElementSorted):
                self.selectedRegionChanged.emit(regionId)
        
        self.isElementSorted=False

    """ Color changes in the cell of the matrix"""
    def ChangeColors(self):
        """
        Clustered Order is the sorted order of different brain regions based on the communities detected   

        """
        self.sortDataStructure(self.Order,self.Brain_Regions)


        self.setVerticalHeaderLabels(self.ClusteredOrder)
        self.setHorizontalHeaderLabels(['\n'.join(name) for name in self.ClusteredOrder])


        for i in range(len(self.correlationTable.header)):
                for j in range(len(self.correlationTable.header)):
                    
                    table_item = self.item(i,j)

                    t = self.ColorNumpyArray[self.sortedOrder[i],self.sortedOrder[j]]
                    table_item.setBackground(QtGui.QColor(*t))
                    table_item.setToolTip("%s,%s,%g" % (self.Brain_Regions[self.sortedOrder[i]] ,self.Brain_Regions[self.sortedOrder[j]],self.correlationTable.data[self.sortedOrder[i], self.sortedOrder[j]]))

        self.verticalHeader()
        self.horizontalHeader()

    """ Selecting cells in the adjacency matrix"""
    def selectRegion(self, regionId):

        # should be able to differentiate between the events that is being clicked on and the events the this class generates 
        self.isElementSorted = not(isinstance(self.sender(),CorrelationTableDisplay))
        
        """ Logic only when the system is in communtiy mode """
        if self.CommunityMode:
            # If the region is selected from the correlation tab and is propagated to pseudocolor
            """ Logic responsible for clicking regions when the sender of the Qt signals are from CorrelationTable"""

            self.selectRow(self.sortedOrder.index(regionId))
        else:
            self.selectRow(regionId)
            
""" Classes responsible for creating a new window in the community mode"""
class CommunityCorrelationTableDisplay(ParentCommunityDisplay):
    selectedRegionChanged = QtCore.Signal(int)

    """ Painting the individual cells of the matrix"""
    class BackgroundDelegate(QtGui.QStyledItemDelegate):
        def paint(self, painter, option, index):
            painter.fillRect(option.rect, index.data(QtCore.Qt.BackgroundRole))
            super(CommunityCorrelationTableDisplay.BackgroundDelegate, self).paint(painter, option, index)
            if option.state & QtGui.QStyle.State_Selected:
                painter.save()
                # pointer to gree
                pen = QtGui.QPen(QtCore.Qt.darkGreen, 2, QtCore.Qt.SolidLine, QtCore.Qt.SquareCap, QtCore.Qt.MiterJoin)
                myrect = option.rect.adjusted(0, 1, 0, 0)
                painter.setPen(pen)
                painter.drawLine(myrect.topLeft(), myrect.topRight())
                painter.drawLine(myrect.bottomLeft(), myrect.bottomRight())
                if index.column() == 0:
                    painter.drawLine(myrect.topLeft(), myrect.bottomLeft())
                if index.column() == index.model().columnCount()-1:
                    painter.drawLine(option.rect.topRight() + QtCore.QPoint(0, -1), option.rect.bottomRight()+ QtCore.QPoint(0, -1))
                painter.restore()

    """ Initialize variables"""
    def __init__(self, correlationTable, colorTable,GraphDataStructure): 
        n = len(correlationTable.header)
        super(CommunityCorrelationTableDisplay, self).__init__(n, n)
        from collections import defaultdict
        self.CommunityMode = False 
        self.MouseReleased = True
        self.colorTable = colorTable
        self.sortedDict= defaultdict(list)
        self.newWindowWidget = []
        self.Selectionmode = True
        self.GraphDataStructure = weakref.ref(GraphDataStructure)
        self.data = self.GraphDataStructure().ThresholdData
        self.Order = []
        self.i = 0 
        self.newwidget = None
        self.Brain_Regions = correlationTable.RegionName[0]
        self.First = True
        self.g= []
        self.isElementsSorted = False
        self.setMinimumSize(800,400)
        self.setContentsMargins(0, 0, 0, 0)
        self.correlationTable = correlationTable
        self.setVerticalHeaderLabels(self.correlationTable.header)
        self.setHorizontalHeaderLabels(['\n'.join(name) for name in self.correlationTable.header])
        font = QtGui.QFont()
        font.setPointSize(8)
        self.horizontalHeader().setFont(font)
        self.verticalHeader().setFont(font)

        if n < 50:
                CellSize=  40
        else: 
                CellSize = 4
        
        for i in range(n):
            self.setColumnWidth(i,CellSize) 
            self.setRowHeight(i, CellSize)
            self.resizeRowToContents(i)
            self.horizontalHeaderItem(i).setToolTip(self.correlationTable.header[i])
            self.verticalHeaderItem(i).setToolTip(self.correlationTable.header[i])

        for i in range(len(self.correlationTable.header)):
            for j in range(len(self.correlationTable.header)):
                table_item = QtGui.QTableWidgetItem()
                self.setItem(i, j, table_item)

        self.resizeColumnsToContents()
        self.setSizePolicy(QtGui.QSizePolicy.Policy.Expanding, QtGui.QSizePolicy.Policy.Expanding)
        self.setShowGrid(False)
        self.setStyleSheet("selection-background-color: transparent;")
        self.setItemDelegate(self.BackgroundDelegate())
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.itemSelectionChanged.connect(self.handleSelectionChange)

    """Logic for selection of multiple cells and displaying selected cells into a new window"""
    def mouseReleaseEvent(self, e):
        super(CorrelationTableDisplay, self).mouseReleaseEvent(e)
        if not(self.Selectionmode):
            regionIDS =  []
            for i in self.selectedItems():
                 regionIDS.append((i.row(), i.column()))
            regionIDS = np.asarray(regionIDS)
            CorrelationTable = self

            def newwindow(BoxWidget):
                i,j = np.amin(regionIDS, axis=0)
                k,l = np.amax(regionIDS, axis=0)

                np.reshape(regionIDS,(k-i+1,l-j+1,2))
                self.bbox = QtGui.QVBoxLayout()
                NewTable = NewWindowCorrelationTableDisplay(k-i+1,l-j+1,i,k,j,l,CorrelationTable,regionIDS)
                self.bbox.addWidget(NewTable)
                BoxWidget.setLayout(self.bbox)

                # FIX me resizing table contents with hardcoded values 
                BoxWidget.resize(18*(l-j)+120,18*(k-i+1)+140)
            
            if self.First:
                self.newWindowWidget.append(QtGui.QWidget()) 
                newwindow(self.newWindowWidget[0])
                self.newWindowWidget[0].show()
                self.First = False
            else: 
                self.i = self.i + 1 
                self.newWindowWidget.append(QtGui.QWidget())
                newwindow(self.newWindowWidget[self.i])
                self.newWindowWidget[self.i].show()

    """ Handling changes"""
    def handleSelectionChange(self):

        regionId = self.selectedItems()[0].row()
        
        if self.CommunityMode: 
            if not(self.isElementsSorted):
                self.selectedRegionChanged.emit(self.sortedOrder[regionId])
        else:
            if not(self.isElementsSorted):
                self.selectedRegionChanged.emit(regionId)
        
        self.isElementsSorted=False

    """ Logic for calculating the sorted order of the adjacency matrix"""
    def ChangeColors(self):
        """
        Clustered Order is the sorted order of different brain regions based on the communities detected   

        """

        """Calling the Parent Method for Sorting the cells"""
        self.sortDataStructure(self.Order,self.Brain_Regions)

        """Sorting the header labels vertical and horizontalHeader"""
        self.setVerticalHeaderLabels(self.ClusteredOrder)
        self.setHorizontalHeaderLabels(['\n'.join(name) for name in self.ClusteredOrder])

        for i in range(len(self.correlationTable.header)):
            for j in range(len(self.correlationTable.header)):
                
                table_item = self.item(i,j)
                
                if (self.GraphDataStructure().ThresholdData[self.sortedOrder[i]][self.sortedOrder[j]] != 0) and self.sortedValues[i] == self.sortedValues[j]:
                    table_item.setBackground(QtGui.QColor(*self.colors[self.sortedOrder[i]]))
                else:
                    table_item.setBackground(QtGui.QColor(QtCore.Qt.white))
                table_item.setToolTip("%s,%s,%g" % (self.Brain_Regions[self.sortedOrder[i]] ,self.Brain_Regions[self.sortedOrder[j]],self.correlationTable.data[self.sortedOrder[i], self.sortedOrder[j]]))

        self.verticalHeader()
        self.horizontalHeader()

    """ Selecting cells in the adjacency matrix"""
    def selectRegion(self, regionId):

        # should be able to differentiate between the events that is being clicked on and the events the this class generates 

        if not(self.CommunityMode):
            return

        """ Logic only when the system is in communtiy mode """
        self.isElementsSorted = not(isinstance(self.sender(),CorrelationTableDisplay))

        # If the region is selected from the correlation tab and is propagated to pseudocolor
        """ Logic responsible for clicking regions when the sender of the Qt signals are from CorrelationTable"""
        if isinstance(self.sender(),CorrelationTableDisplay): 
            self.selectRow(self.sortedOrder.index(regionId))
        else:
            self.selectRow(self.sortedOrder.index(regionId))


