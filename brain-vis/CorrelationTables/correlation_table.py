import csv
import numpy as np
import pprint
import weakref
import tempfile
import time
import math
import copy
from PySide import QtCore, QtGui


"""Class responsible for transferring data from files to self.data"""
class CorrelationTable(object):
    def __init__(self, filename,dataProcess=None):
        self.header = None
        self.AbbrName = []
        self.data = []
        self.RegionName = []
        
        with open(filename, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='\'')
            self.header = reader.next()
            self.header = self.header[0:103]
            self.RegionName.append((self.header))
            self.data=np.array([map(float, line) for line in reader])

            NewData = self.data[0:103,0:103]
            pprint.pprint(NewData)
            self.data = copy.deepcopy(NewData)

        i = 0

        print len(self.header), "Value"
    """
    Function for finding the absolute value of correlation values 
    """
    def FindAbsoluteValue(self):
        for i in range(len(self.data)):
            for j in range(len(self.data)):
                self.data[i,j] = abs(self.data[i,j])

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
        # print "asd"
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
        # print "receiving correlationtabledisplay end",self.sender() 

        self.isElementSorted = not(isinstance(self.sender(),CorrelationTableDisplay))
        
        """ Logic only when the system is in communtiy mode """
        if self.CommunityMode:
            # If the region is selected from the correlation tab and is propagated to pseudocolor
            """ Logic responsible for clicking regions when the sender of the Qt signals are from CorrelationTable"""

            self.selectRow(self.sortedOrder.index(regionId))
        else:
            self.selectRow(regionId)
            
            # print "\nPutting the values in buffer\n"

            # self.queue.put(str(regionId))



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
        # print "asd"
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


