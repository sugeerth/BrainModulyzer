import csv
import sys
import math
from collections import defaultdict
from PySide import QtCore, QtGui
from sys import platform as _platform
import weakref
import cProfile
import os

class CommunityDendogram(QtGui.QGraphicsView):
    def __init__(self,induced_graph,correlationTable):
        super(CommunityDendogram,self).__init__()
        QtGui.QGraphicsView.__init__(self)
        self.induced_graph = induced_graph
        self.correlationTable = weakref.ref(correlationTable)
        self.correlationTableObject = self.correlationTable()
        self.setMinimumSize(500, 400)
        self.initUI()

    def initUI(self):
        scene = QtGui.QGraphicsScene(self)
        scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        self.setScene(scene)
        self.NodeIds = []
        self.centrality = []
        self.Scene_to_be_updated = scene
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setInteractive(True)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        self.scaleView(0.7)
        # method to add a new graph visualization                
        i = 0
        # self.CommunityPos =nx.graphviz_layout(self.induced_graph,prog='fdp',args='-Gsep=.25,-GK=20-Eweight=2')
        self.CommunityPos = nx.spring_layout(self.induced_graph,pos= Pos,weight='weight',scale=450)
        for node in self.induced_graph.nodes():
            i = i + 1
            node_value=Node(Graph,i,self.correlationTableObject,True)
            self.NodeIds.append(node_value)
            scene.addItem(node_value)
            x,y=self.CommunityPos[node]
            node_value.setPos(x,y)
            node_value.PutColor(clut[i-1])
        k =0 
        for i,j in self.induced_graph.edges():
                scene.addItem(Edge(Graph,self.NodeIds[i],self.NodeIds[j],k, i,j,Max,((Matrix[j,i]-Min1)/(Max1 - Min1))*10,True))
                k = k + 1 
     
        self.setSceneRect(self.Scene_to_be_updated.itemsBoundingRect())
        self.setScene(self.Scene_to_be_updated)
        self.fitInView(self.Scene_to_be_updated.itemsBoundingRect(),QtCore.Qt.KeepAspectRatio)
        self.scaleView(math.pow(2.0, -300 / 1040.0))

    def wheelEvent(self, event):
        # print event.delta()
        self.scaleView(math.pow(2.0, -event.delta() / 1040.0))

    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 100:
            return
        self.scale(scaleFactor, scaleFactor)
        del factor
