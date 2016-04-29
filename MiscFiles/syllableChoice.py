import sys
from PySide import QtGui, QtCore

""" TODO : Adding selectable boxes """


class Syllable(QtGui.QWidget):

    selectedSyllableChanged = QtCore.Signal(int)

    def __init__(self):
        super(Syllable, self).__init__()
        
        self.initUI()
        
    def initUI(self):      
        self.square = [None]*7
        self.col = QtGui.QColor(1, 0, 0)       
        syllabeSignal = self.selectedSyllableChanged 

        class syllablePic(QtGui.QFrame):

            def __init__(self, syllableNo, parent=None):
                super(syllablePic, self).__init__(parent)        
                self.syllableNo = int(syllableNo)

            def mousePressEvent(self, event):
                self.update()
                syllabeSignal.emit(self.syllableNo)

        for i in range(1,7):
            self.square[i] = syllablePic(i,self)
            self.square[i].setGeometry(30 + (i-1)*220, 25, 150, 100)
            self.square[i].setStyleSheet("QWidget { background-color: rgb(%s, 0,0); }" % (i* 24)) 
            # new = QtGui.QPushButton(self.square[i])
            # self.addLayout(self.square[i]
            Pallette = self.square[i].palette();
            Pallette.setColor(QtGui.QPalette.Window, QtCore.Qt.red);
            Pallette.setColor(QtGui.QPalette.Base, QtCore.Qt.blue);
            Pallette.setColor(QtGui.QPalette.Button, QtCore.Qt.green);
            self.square[i].setPalette(Pallette);
            self.square[i].setAutoFillBackground(True);

        self.setGeometry(400, 300, 720, 150)
        self.setMinimumSize(350, 160)
        self.setWindowTitle('Syllable selection')
