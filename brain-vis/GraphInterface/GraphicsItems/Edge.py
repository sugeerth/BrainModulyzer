
from PySide import QtCore, QtGui

import math
import weakref

try:
    import numpy as np


except:
    print "Couldn't import all required packages. See README.md for a list of required packages and installation instructions."
    raise

def ColorToInt(color):
    r, g, b, a = map(np.uint32, color)
    return a << 24 | r << 16 | g << 8 | b


"""
Serves as an edge in the graph view 
A future proposal to implement a hierarchical edge bundling on top of the graph 
view 
this should be fairly easy 
You can look at existing algorithms by Danny Holten at TVCG 

The tooltips may not be perfect as the enclosing bounding rectangle overlaps for each line 
You can reduce this by changing the bounding rectangle dynamically
"""
class Edge(QtGui.QGraphicsItem):

    Pi = math.pi
    TwoPi = 2.0 * Pi

    Type = QtGui.QGraphicsItem.UserType + 2

    def __init__(self, graphWidget, sourceNode, destNode, counter, sourceId, destId, MaxValue,weight=100,ForCommunities=False,):
        QtGui.QGraphicsItem.__init__(self)
        self.setAcceptHoverEvents(True)

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
        if math.isnan(weight):
            weight = 1
        self.weight = weight
        if ForCommunities:
            self.communtiyColor = ColorToInt((0,0,0,255))
            self.communtiyColor1 = QtGui.QColor(self.communtiyColor)
            self.setToolTip(str("InterModular Correlation Strength:  "+str(weight)+"\n"+"Source Community:  "+str(sourceId)+"\nDestination Community:  "+str(destId)))
        self.sourcePoint = QtCore.QPointF()
        self.destPoint = QtCore.QPointF()
        self.graph = weakref.ref(graphWidget)
        self.source = weakref.ref(sourceNode)
        self.dest = weakref.ref(destNode)
        self.EdgeColor = QtGui.QColor(self.graph().EdgeColor[self.index])
        self.source().addEdge(self)

    def type(self):
        return Edge.Type

    def sourceNode(self):
        return self.source()

    def getNodes(self,community):
        return self.graph().communityMultiple[community]

    def hoverEnterEvent(self, event):
        if self.ForCommunities:
            self.selectEdges()
            self.update()
            return
        QtGui.QGraphicsItem.hoverEnterEvent(self, event)

    def allnodesupdate(self):
        # Nodes = [item for item in self.scene().items() if isinstance(item, Node)]
        Nodes = self.graph().nodes
        for node in Nodes:
            node().setSelected(False)
            node().unsetOpaqueNodes()
            node().WhitePaint = False
            node().update()

    def selectInterModularEdges(self,communtiy1,community2):
        edges = self.graph().edges
        
        self.allnodesupdate()
        self.alledgesupdate()


        for i in communtiy1:
                self.graph().NodeIds[i].setOpaqueNodes()

        for j in community2: 
                self.graph().NodeIds[j].setOpaqueNodes()

        for edge in edges: 
            sourceBool = edge().sourceNode().counter-1 in communtiy1
            destBool = edge().destNode().counter-1 in community2
            if (sourceBool and destBool): 
                edge().ColorEdges()

        for edge in edges: 
            sourceBool = edge().sourceNode().counter-1 in community2
            destBool = edge().destNode().counter-1 in communtiy1

            if (sourceBool and destBool): 
                edge().ColorEdges()

        self.graph().Refresh()


    def selectEdges(self):
        communtiy1 = self.getNodes(self.sourceId)
        community2 = self.getNodes(self.destId)
        self.selectInterModularEdges(communtiy1,community2)

    def alledgesupdate(self):
        edges = self.graph().edges
        for edge in edges:
            edge().ColorEdgesFlag = False

    def setSourceNode(self, node):
        self.source = weakref.ref(node)
        self.adjust()

    def destNode(self):
        return self.dest()

    def setHighlightedColorMap(self,state):
        self.HighlightedColorMap = state


    def ColorOnlySelectedNode(self,state):
        self.ColorOnlySelectedNodesFlag = state

    def setDestNode(self, node):
        self.dest = weakref.ref(node)
        self.adjust()
    
    def setColorMap(self,state):
        self.ColorMap = state

    def ColorEdges(self):
        self.ColorEdgesFlag = True
        self.update()
 
    def setEdgeThickness(self,value):
        self.edgeThickness = float(value)
        self.update()

    def Threshold(self,value):
        # print "Threshold in Edge"
        self.EdgeThreshold = value
        self.update()

    def adjust(self):
        if not self.source() or not self.dest():
            return
        line = QtCore.QLineF(self.mapFromItem(self.source(), 0, 0), self.mapFromItem(self.dest(), 0, 0))

        self.sourcePoint = line.p1() #+ edgeOffset
        self.destPoint = line.p2() #- edgeOffset

    def boundingRect(self):
        """
        Computes the bounding recatangle for every edge 
        """
        if not self.source() or not self.dest():
            return QtCore.QRectF()

        return QtCore.QRectF(self.sourcePoint,
                             QtCore.QSizeF(self.destPoint.x() - self.sourcePoint.x(),
                                           self.destPoint.y() - self.sourcePoint.y()))

    def communityAlpha(self,boolValue,value=-1):
        if boolValue:
            self.communtiyColor1.setAlpha(255)
        else:
            self.communtiyColor1.setAlpha(55)
        self.update()

    def paint(self, painter, option, widget):
        if not self.source() or not self.dest():
            return

        # Draw the line itself.
        if self.ColorOnlySelectedNodesFlag: 
            if not(self.ColorEdgesFlag):
                return

        line = QtCore.QLineF(self.sourcePoint, self.destPoint)
        # Should FIX the thickness values!!! fix me
        painter.save()
        """
        Painting the edge colors based on various factors
        Not painting the edges if they are below certain threshold 
        Painting the edges to be black or just based on their colors 
        Painting highlighted colormaps 
        edge Thickness is a function of  the weight of the edges 
        drawing z values so that they do not overalpp with others
        """


        if self.ForCommunities:
                painter.setPen(QtGui.QPen(self.communtiyColor1 ,self.communityWeight , QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
                painter.drawLine(line)
        else:
            if self.ColorMap:
                if self.EdgeThreshold < self.weight:
                    if not(self.ColorEdgesFlag):
                        self.setZValue(1)
                        self.EdgeColor.setAlpha(25)
                        painter.setPen(QtGui.QPen(self.EdgeColor ,self.edgeThickness , QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
                        painter.drawLine(line)
                    else: 
                        self.setZValue(2)
                        if not(self.HighlightedColorMap):
                            # pointer to green
                            painter.setPen(QtGui.QPen(QtCore.Qt.darkGreen, self.edgeThickness , QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
                        else:
                            self.EdgeColor.setAlpha(255)
                            painter.setPen(QtGui.QPen(self.EdgeColor, self.thickHighlightedEdges , QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
                        painter.drawLine(line)
            else: 
                if self.EdgeThreshold < self.weight:
                    if not(self.ColorEdgesFlag):
                        self.setZValue(1)
                        painter.setPen(QtGui.QPen(QtCore.Qt.black ,self.edgeThickness , QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
                        painter.drawLine(line)
                    else: 
                        self.setZValue(2)
                        if not(self.HighlightedColorMap):
                            painter.setPen(QtGui.QPen(QtCore.Qt.darkGreen, self.edgeThickness , QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
                        else:
                            painter.setPen(QtGui.QPen(self.EdgeColor, self.thickHighlightedEdges , QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
                        painter.drawLine(line)
        painter.restore()
