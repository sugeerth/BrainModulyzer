
from PySide import QtCore, QtGui

import math
import weakref

try:
    import numpy as np


except:
    print "Couldn't import all required packages. See README.md for a list of required packages and installation instructions."
    raise
from visit_interface import GetColor

class dendogramLine(QtGui.QGraphicsItem):

	Pi = math.pi
    TwoPi = 2.0 * Pi

    Type = QtGui.QGraphicsItem.UserType + 2    
    def __init__(self, graphWidget, sourceNode, destNode, counter, sourceId, destId, MaxValue,weight=100,ForCommunities=False,):
        QtGui.QGraphicsItem.__init__(self)
        self.weight = weight
        self.EdgeThreshold = MaxValue - 0.01
        self.ColorEdgesFlag = False
        self.index = counter
        self.Alpha = 0.2
        self.sourceId = sourceId 
        self.destId = destId
        self.ColorMap = True
        self.ForCommunities= ForCommunities
        self.HighlightedColorMap = False
        self.communityWeight = weight
        self.edgeThickness = 1
        self.thickHighlightedEdges = 3 
        self.ColorOnlySelectedNodesFlag =False



    def type(self):
        return Edge.Type

    def sourceNode(self):
        return self.source()

    def setSourceNode(self, node):
        self.source = weakref.ref(node)
        self.adjust()

    def destNode(self):
        return self.dest()
    def boundingRect(self):
        """
        Computes the bounding recatangle for every edge 
        """
        if not self.source() or not self.dest():
            return QtCore.QRectF()

        return QtCore.QRectF(self.sourcePoint,
                             QtCore.QSizeF(self.destPoint.x() - self.sourcePoint.x(),
                                           self.destPoint.y() - self.sourcePoint.y()))

    def paint(self, painter, option, widget):
        if not self.source() or not self.dest():
            return
        # Draw the line itselfself.