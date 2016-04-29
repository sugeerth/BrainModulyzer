import operator
from PySide.QtCore import *
from PySide.QtGui import *
# Coding style idea taken from https://www.daniweb.com/software-development/python/code/447834/applying-pysides-qabstracttablemodel


class quantTable(QWidget):
    def __init__(self, quantData,widget, *args):
        QWidget.__init__(self, *args)
        self.quantData=quantData
        self.table_view = None
        self.table_model = None

        # setGeometry(x_pos, y_pos, width, height)
        self.setGeometry(0, 0, 279, 289)
        self.font = QFont("Courier New", 14)

        self.layout = QVBoxLayout(self)
        self.setWindowTitle("Click on column title to sort")
        # self.table_model = MyTableModel(self, self.quantData.data_list,self.quantData.header)
        # self.table_view = QTableView()
        self.setTableModel(True)

    def setTableModel(self,state):

        for i in reversed(range(self.layout.count())): 
                self.layout.itemAt(i).widget().close() 
                
        del self.table_model
        del self.table_view

        self.table_model = MyTableModel(self, self.quantData.data_list,self.quantData.header)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setFont(self.font)

        # set column width to fit contents (set font first!)
        self.table_view.resizeColumnsToContents()

        # enable sorting
        self.table_view.setSortingEnabled(True)
        
        for i in range(len(self.table_model.mylist)):
            self.table_view.setRowHeight(i,18) 
        # table_view.resizeColumnsToContents();


        self.layout.addWidget(self.table_view)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self.setContentsMargins(0, 0, 0, 0)

    def setData(self,list2):
        self.table_model.setData(list2)

class MyTableModel(QAbstractTableModel):
    def __init__(self, parent, mylist, header, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header
        # self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

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

