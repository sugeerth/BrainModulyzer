import operator
from PySide.QtCore import *
import PySide
from PySide.QtGui import *
# Coding style idea taken from https://www.daniweb.com/software-development/python/code/447834/applying-pysides-qabstracttablemodel


"""
Class that Implements the UI for the Network Measure table 
You can sort things based on the alphabhetical order 
and make the classes more eaily available 
"""
class quantTable(QWidget):
    DataSelected = PySide.QtCore.Signal(int)

    def __init__(self, quantData,widget, *args):
        QWidget.__init__(self, *args)
        self.quantData=quantData
        self.table_view = None
        self.table_model = None
        self.Brain_Regions = widget.correlationTable().RegionName[0]

        self.setGeometry(0, 0, 279, 289)
        self.font = QFont("Courier New", 14)

        self.layout = QVBoxLayout(self)
        self.setWindowTitle("Click on column title to sort")
        self.setTableModel(True)

    def setTableModel(self,state):

        for i in reversed(range(self.layout.count())): 
                self.layout.itemAt(i).widget().close() 
                
        del self.table_model
        del self.table_view

        self.table_model = MyTableModel(self, self.quantData.data_list,self.quantData.header)

        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(PySide.QtGui.QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(PySide.QtGui.QAbstractItemView.SingleSelection)

        self.table_view.clicked.connect(self.onClicked)
        # self.model =  QtGui.QStandardItemModel(rows, columns, self.table_view)

        self.table_view.setModel(self.table_model)
        self.table_view.setFont(self.font)

        # set column width to fit contents (set font first!)
        self.table_view.resizeColumnsToContents()

        # enable sorting
        self.table_view.setSortingEnabled(True)
        
        for i in range(len(self.table_model.mylist)):
            self.table_view.setRowHeight(i,18) 

        self.layout.addWidget(self.table_view)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self.setContentsMargins(0, 0, 0, 0)

    def onClicked(self,index):
        item = self.table_model.mylist[index.row()]
        ID = item[0]
        for i, data  in enumerate(self.Brain_Regions): 
            if data == ID: 
                self.DataSelected.emit(i)
                return

    def setRegions(self, id): 
        name = self.Brain_Regions[id]
        counter = 0
        for i in self.table_model.mylist:
            if i[0] == name:
                break 
            counter = counter+1
        self.table_view.selectRow(counter)

    def setCommunityRegions(self, community): 
        print community

    def cell_was_clicked(self, row, column):
        print("Row %d and Column %d was clicked" % (row, column))
        item = self.table_view.itemAt(row, column)
        self.ID = item.text()

    def setData(self,list2):
        self.table_model.setData(list2)

class MyTableModel(QAbstractTableModel):
    def __init__(self, parent, mylist, header, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header

    def rowCount(self, parent):
        return len(self.mylist)
    def columnCount(self, parent):
        return len(self.mylist[0])
    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.mylist[index.row()][index.column()]
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def sort(self, col, order):
        """sort table by given column number col"""
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.mylist = sorted(self.mylist,
            key=operator.itemgetter(col))
        if order == Qt.DescendingOrder:
            self.mylist.reverse()
        self.emit(SIGNAL("layoutChanged()"))

