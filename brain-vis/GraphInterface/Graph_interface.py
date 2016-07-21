### Standard Python packages
#-*- coding: utf-8 -*-
import csv
import colorsys
import math
import colorsys
import time
from collections import defaultdict
from PySide import QtCore, QtGui
from sys import platform as _platform
import weakref
import cProfile
import pprint

import warnings
warnings.filterwarnings("ignore")

# import time
import community as cm
try:
    # ... reading NIfTI 
    import nibabel as nib
    import numpy as np
    # ... graph drawing
    import networkx as nx

except:
    print "Couldn't import all required packages. See README.m for a list of required packages and installation instructions."
    raise

# from VisitInterface.visit_interface import GetColor

from GraphDataStructure import GraphVisualization
from DendogramModule.dendogram import dendogram, DendoNode
from CommunityFiles.communityDetectionEngine import communityDetectionEngine 


#from pycallgraph import PyCallGraph
#from pycallgraph.output import GraphvizOutput
from GraphicsItems.Edge import Edge 
from GraphicsItems.Node import Node

def ColorToInt(color):
    r, g, b, a = map(np.uint32, color)
    return a << 24 | r << 16 | g << 8 | b


"""
Have tried my best to explain the modules, if you still have trouble finding the meaning 
of the function, feel free to email at: sugeerth@gmail.com

There are many avenues for extending the tool for new visual analysis methods 
such as: new layout calculation, etc 

If everthing works then well and good other wise contact me. 

The class is self contained with many self variables 
"""

class GraphWidget(QtGui.QGraphicsView):
    
    regionSelected = QtCore.Signal(int)
    EdgeWeight = QtCore.Signal(int)
    CommunityColor = QtCore.Signal(list)
    CommunityColorAndDict = QtCore.Signal(list,dict)
    CommunityMode = QtCore.Signal(bool)
    ThresholdChange = QtCore.Signal(bool)
    DendoGramDepth = QtCore.Signal(int)

    def __init__(self,Graph_data,Tab_2_CorrelationTable,correlationTable,colortable,selectedColor,BoxGraphWidget,BoxTableWidget,Offset,Ui):
        QtGui.QGraphicsView.__init__(self)
        self.colortable=colortable
        self.BoxGraphWidget = BoxGraphWidget
        self.BoxTableWidget = BoxTableWidget

        self.Ui = Ui
        self.DisplayOnlyEdges = False
        self.level = -1
        self.selectedColor = selectedColor
        self.Graph_data = weakref.ref(Graph_data)

        self.Tab_2_CorrelationTable = weakref.ref(Tab_2_CorrelationTable)

        self.ColorNodesBasedOnCorrelation =True
        self.setTransp = True
        self.hoverRender = True
        self.Check = False
        self.grayOutNodes = True
        self.PositionPreserve = True

        self.communityobject = None
        self.correlationTable = weakref.ref(correlationTable)
        self.correlationTableObject = self.correlationTable()
        self.partition =[]
        self.sortedValues = None
        self.communityPos = dict()
        self.Matrix = []
        self.oneLengthCommunities=[]
        self.Centrality = []
        self.Betweeness = []
        self.dendogramObject = None
        self.dendogram = dict()
        self.LoadCentrality = [] 
        self.EigenvectorCentralityNumpy = []
        self.ClosenessCentrality = []
        self.EigenvectorCentrality = []
        self.nodeSizeFactor = "Centrality"
        self.counter = len(correlationTable.data)+1
        self.width =  Offset*(self.counter-1)+45
        self.Max=correlationTable.data.max()
        self.DataColor = np.zeros(self.counter)
        self.EdgeColor = np.zeros(self.counter * self.counter)

        self.communityDetectionEngine = communityDetectionEngine(self, self.counter)


        self.ColorToBeSentToVisit = list() 
        self.EdgeSliderValue = self.Max - 0.01
        self.nodesize = 7

        self.Graph_Color(-1)
        self.Edge_Color()
        # initializing with an arbitrary layout option 
        self.Layout = 'fdp'

        # initializing the scene
        scene = QtGui.QGraphicsScene(self)

        scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)

        self.setScene(scene)

        self.Scene_to_be_updated = scene
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setInteractive(True)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.NoAnchor)
        self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        self.scaleView(2.0)

        self.NodeIds = []

        self.wid = QtGui.QWidget()
        self.hbox = QtGui.QVBoxLayout()

        self.First= True
        self.node = None
        self.HighlightedId = None
        self.EdgeIds = []

        # Setting the posiitons of the node for the different graphs              
        self.scale(0.8, 0.8)
        self.setMinimumSize(250, 250)
        self.setWindowTitle(self.tr("Node Visualization"))
        i = 0

        for node in  self.Graph_data().g.nodes():
            i = i + 1
            node_value=Node(self,i,correlationTable)
            self.NodeIds.append(node_value)
            scene.addItem(node_value)

        k = 0 

        for i in range(1, self.counter):
            for j in range(1, self.counter):
                if (i-1 >= j-1): 
                    continue
                try:
                    t = self.correlationTable().value(i-1,j-1)
                    scene.addItem(Edge(self,self.NodeIds[i-1],self.NodeIds[j-1],k,i,j,self.Max, self.Graph_data().data[i-1][j-1]))
                except KeyError:
                    continue
                k = k + 1 

        self.edges = [weakref.ref(item) for item in self.scene().items() if isinstance(item, Edge)]
        self.nodes = [weakref.ref(item) for item in self.scene().items() if isinstance(item, Node)]
        
        # setting a sample layout to show 
        self.changeLayout('fdp')

    """
    Highlight edges for visualization
    """
    def changeHighlightedEdges(self,state):
        if state: 
            for edge in self.edges:
                 edge().setHighlightedColorMap(False)
        else: 
            for edge in self.edges:
                 edge().setHighlightedColorMap(True)

        self.Scene_to_be_updated.update()

    def LayoutCalculation(self):
        self.changeLayout('fdp')

    def NewNodeSelected(self,idx):
        self.HighlightedId = idx 

    def changeSpringLayout(self,state):
        if state: 
            self.PositionPreserve = True
        else: 
            self.PositionPreserve = False

    def changeTitle(self, state):
        self.DisplayOnlyEdges = not(self.DisplayOnlyEdges)
        self.NodeSelected(self.HighlightedId) 
        self.Scene_to_be_updated.update()

    def changeGrayOutNodes(self,state):
        self.grayOutNodes = not(self.grayOutNodes)
        if not(self.level == -1):
            self.communityDetectionEngine.ChangeCommunityColor(self.level-1)
        else: 
            self.communityDetectionEngine.ChangeCommunityColor()

    def changeDendoGramLevel(self,level):
        self.level = level-1
        self.Ui.communityLevelLineEdit.setText(str(self.level))
        self.communityDetectionEngine.ChangeCommunityColor(self.level)

    """
    Changes in Line Edit for Community Level Slider
    """
    def LevelLineEditChanged(self):
        """Handling Line Edit changes"""
        text = (self.Lineditor.text().encode('ascii','ignore')).replace(' ','')
        value = int(text)
        self.Ui.communityLevel.setTickPosition(value)
        self.DendoGramDepth.emit(value)

    """
    Function that actually assigns to the nodes based on the 
    mode of the application
    This can either be the correlation color or the community color

    Changes the color in the Graph view and then when it calls the 
    community color, changes colors of all other views
    """
    def SelectNodeColor(self,state):
        nodes1 = [item for item in self.scene().items() if isinstance(item, Node)]
        if state == "Correlation Strength": 
            self.ColorNodesBasedOnCorrelation = True 
            for node in nodes1:
                node.NodeColor()
            self.Tab_2_CorrelationTable().hide()
            self.CommunityMode.emit(False)
            self.wid.hide()
            if self.HighlightedId:
                self.regionSelected.emit(self.HighlightedId)
            else:
                self.regionSelected.emit(3)
            self.resizeTheWholeGraphWidget(True)
        else: 
            self.Tab_2_CorrelationTable().show()
            self.wid.show()
            self.ColorNodesBasedOnCorrelation = False 
            if not(self.level == -1):
                self.communityDetectionEngine.ChangeCommunityColor(self.level-1)
            else: 
                self.communityDetectionEngine.ChangeCommunityColor()
            self.CommunityMode.emit(True)
            self.CommunityColor.emit(self.communityDetectionEngine.ColorToBeSentToVisit)
            self.resizeTheWholeGraphWidget(False) 
        self.Scene_to_be_updated.update()

        del nodes1

    def changeTitleSetColorMap(self, state):

        if state: 
            for edge in self.edges:
                edge().setColorMap(True)
        self.Scene_to_be_updated.update()

    def resizeTheWholeGraphWidget(self,state):
        if state: 
            # Entering the correlation mode initiate the window to \
            #resize to normal (Workaround not adrdressing the root problem)
            self.BoxGraphWidget.resize(550,550)
            self.BoxTableWidget.resize(self.width,self.width) 
        else: 
            # Entering the community mode initiate the window to have an earlier version
            newwidth = self.width+self.width
            self.BoxTableWidget.resize(newwidth,self.width)

    """
    Functions related to community detection and community manipulation 
    This might be a bit tricky to understand 
    but the gist is change community colors, compute new ones 

    Very important Function: 
    Changes in the layout are calculated here 
    New data for display is displyed
    Organized into changes in the layout options
    You can add additional layouts by having 

    if (Layout == "Entry in the dropdown menu")
        code for calculating the new layout-- Make sure the new layout is scalable

    """
    def changeLayout(self,Layout='sfdp'):
        Layout = (Layout.encode('ascii','ignore')).replace(' ','')
        self.g =  self.Graph_data().DrawHighlightedGraph(self.EdgeSliderValue)

        # asking community detection Engine to compute the Layout
        self.pos,Factor = self.communityDetectionEngine.communityLayoutCalculation(Layout,self.g)

        # Degree Centrality for the the nodes involved
        self.Centrality=nx.degree_centrality(self.g)
        self.Betweeness=nx.betweenness_centrality(self.g)  
        self.LoadCentrality = nx.load_centrality(self.g)
        self.ParticipationCoefficient = self.communityDetectionEngine.participation_coefficient(self.g,True)
        self.ClosenessCentrality = nx.closeness_centrality(self.g)

        for i in range(len(self.ParticipationCoefficient)):
            if (str(float(self.ParticipationCoefficient[i])).lower() == 'nan'):
                   self.ParticipationCoefficient[i] = 0
        i = 0 
        
        """ Calculate rank and Zscore """
        MetrixDataStructure=eval('self.'+self.nodeSizeFactor)
        from collections import OrderedDict
        
        self.sortedValues = OrderedDict(sorted(MetrixDataStructure.items(), key=lambda x:x[1]))
        self.average = np.average(self.sortedValues.values())
        self.std = np.std(self.sortedValues.values())

        for item in self.scene().items():
            if isinstance(item, Node):
                x,y=self.pos[i]
                item.setPos(QtCore.QPointF(x,y)*Factor)
                Size = eval('self.'+self.nodeSizeFactor+'[i]')
                rank, Zscore = self.calculateRankAndZscore(i)
                item.setNodeSize(Size,self.nodeSizeFactor,rank,Zscore)
                i = i + 1

        for edge in self.edges:
            edge().adjust()

        self.Refresh()

        if not(self.PositionPreserve):
            self.Scene_to_be_updated.setSceneRect(self.Scene_to_be_updated.itemsBoundingRect())
            self.setScene(self.Scene_to_be_updated)

        self.fitInView(self.Scene_to_be_updated.itemsBoundingRect(),QtCore.Qt.KeepAspectRatio)
        self.Scene_to_be_updated.update()

    """
    Controls computing new data for display on the data
    """
    def UpdateThresholdDegree(self):
        self.g =  self.Graph_data().DrawHighlightedGraph(self.EdgeSliderValue)

        # Degree Centrality for the the nodes involved
        self.Centrality=nx.degree_centrality(self.g)
        self.Betweeness=nx.betweenness_centrality(self.g)  
        self.ParticipationCoefficient = self.communityDetectionEngine.participation_coefficient(self.g,True)
        self.LoadCentrality = nx.load_centrality(self.g)
        self.ClosenessCentrality = nx.closeness_centrality(self.g)

        for i in range(len(self.ParticipationCoefficient)):
            if (str(float(self.ParticipationCoefficient[i])).lower() == 'nan'):
                   self.ParticipationCoefficient[i] = 0

        i = 0
        """ Calculate rank and Zscore """
        MetrixDataStructure=eval('self.'+self.nodeSizeFactor)

        from collections import OrderedDict
        self.sortedValues = OrderedDict(sorted(MetrixDataStructure.items(), key=lambda x:x[1]))
        
        self.average = np.average(self.sortedValues.values())
        self.std = np.std(self.sortedValues.values())
        
        for item in self.scene().items():
            if isinstance(item, Node):
                Size = eval('self.'+self.nodeSizeFactor+'[i]')
                rank, Zscore = self.calculateRankAndZscore(i)
                item.setNodeSize(Size,self.nodeSizeFactor,rank,Zscore)    
                i = i + 1

        self.ThresholdChange.emit(True)
        if not(self.ColorNodesBasedOnCorrelation): 
            self.Ui.communityLevelLineEdit.setText(str(self.level))
            self.DendoGramDepth.emit(self.level)
        
        self.Refresh()

    """
    Controls computing new data for display on the data
    """
    def calculateRankAndZscore(self,counter):
        """Zscore and Rank"""
        Rank =  abs(self.sortedValues.keys().index(counter)-(self.counter-1))
        Zscore = (self.sortedValues[counter] - self.average)/(self.std)
        return (Rank,Zscore)

    """
    Size of the nodes
    """
    def setNodeSizeOption(self,state):
        self.nodeSizeFactor = state
        self.UpdateThresholdDegree()

    """
    Selection of layouts
    """
    def SelectLayout(self, Layout):
        self.changeLayout(Layout)
        self.Layout = Layout

    """
    Controls related to updating stuff on the graph view
    """
    def NodeSelected(self,NodeId):
        if isinstance(self.sender(),Node) or isinstance(self.sender(),GraphWidget):
            return

        if not(isinstance(self.sender(),GraphWidget)):
            for node in self.nodes:
                if node().counter-1 == NodeId:
                    node().SelectedNode(NodeId,True)
                    node().setSelected(True)
                    node().update()

        if self.DisplayOnlyEdges:
            for edge in self.edges:
                edge().ColorOnlySelectedNode(True)
        else:
           for edge in self.edges:
                edge().ColorOnlySelectedNode(False) 
        self.HighlightedId = NodeId
        self.Scene_to_be_updated.update()

    def Refresh(self):
        for edge in self.edges:
            edge().update()

        for node in self.nodes:
            node().update()

        self.Scene_to_be_updated.update()

    def communityGraphUpdate(self):
        for edge in self.communityDetectionEngine.communityObject.edges:
            edge.update()

        for node in self.communityDetectionEngine.communityObject.nodes:
            node.update()

        self.communityDetectionEngine.communityObject.Scene_to_be_updated.update()

    """
    Controls for hovering over the mouse
    """
    def hoverChanged(self,state):
        self.hoverRender = not(self.hoverRender)
        # Enable/Disable hover events for the entire tool
        nodes = [item for item in self.scene().items() if isinstance(item, Node)]
        for node in nodes:
            node.setAcceptHoverEvents(self.hoverRender)
            node.update()

        if self.communityDetectionEngine.communityObject:
            nodes = [item for item in self.communityDetectionEngine.communityObject.scene().items() if isinstance(item, Node)]
            for node in nodes:
                node.setAcceptHoverEvents(self.hoverRender)
                node.update()

            edges = [item for item in self.communityDetectionEngine.communityObject.scene().items() if isinstance(item, Edge)]
            for edge in edges:
                edge.setAcceptHoverEvents(self.hoverRender)
                edge.update()

            DendoNodes = [item for item in self.communityDetectionEngine.dendogramObject.scene.items() if isinstance(item, DendoNode)]
            AllEdges = [item for item in self.communityDetectionEngine.dendogramObject.scene.items() if isinstance(item, Edge)]
            
            for node in DendoNodes:
                node.setAcceptHoverEvents(self.hoverRender)
                node.update()

            for edge in AllEdges:
                edge.setAcceptHoverEvents(self.hoverRender)
                edge.update()

    """
    Changes transparency in the graph
    """
    def changeTransparency(self,state):
        self.setTransp = not(self.setTransp)
        nodes = [item for item in self.scene().items() if isinstance(item, Node)]
        for node in nodes:
            node.setTransp = self.setTransp
            node.unsetOpaqueNodes()
            node.update()   
        self.Refresh()

    """
    Changes in properties of the graph and the visual interface
    """
    def ChangePropertiesOfGraph(self,value):
        """Changing the value of the communities"""
        value_for_slider = float(value) / 1000 
        self.EdgeSliderValue = value_for_slider
        self.EdgeSliderForGraph.setValue = self.EdgeSliderValue
        self.Lineditor.setText(str(self.EdgeSliderValue))
        self.EdgeSliderForGraph.setToolTip("Edge Weight: %0.2f" % (self.EdgeSliderValue))

        if not(self.PositionPreserve):
            self.changeLayout(self.Layout)

        for edge in self.edges:
            edge().Threshold(value_for_slider)
        
        if not(self.ColorNodesBasedOnCorrelation):
            if not(self.PositionPreserve):
                pass
            else:
                if not(self.level == -1):
                    self.communityDetectionEngine.ChangeCommunityColor(self.level-1)
                else: 
                    self.communityDetectionEngine.ChangeCommunityColor()
            self.CommunityColor.emit(self.communityDetectionEngine.ColorToBeSentToVisit)
        
        self.UpdateThresholdDegree()
        self.Scene_to_be_updated.update()

    """
    slider for changing the threshold values 
    """
    def slider_imple(self):
        """implementation of Edge threshold sliders"""
        self.EdgeSliderForGraph = QtGui.QSlider(QtCore.Qt.Horizontal,self)
        self.EdgeSliderForGraph.setTracking(False)
        self.EdgeSliderForGraph.setRange( self.Graph_data().data.min()*1000 ,  self.Graph_data().data.max()* 1000 )
        self.EdgeSliderForGraph.setValue(self.EdgeSliderValue*1000)
        self.EdgeSliderForGraph.setToolTip("Edge Weight: %0.2f" % (self.EdgeSliderValue))
        self.interval=((0.1-5)/10)*(-1)
        self.EdgeSliderForGraph.valueChanged[int].connect(self.ChangePropertiesOfGraph)

    """
    Slots for changing the thickness of the edges , (Can then be extended into other forms)
    """
    def changeEdgeThickness(self,value):
        NormValue = float(value)
        edgeThickness = 1 + float(NormValue)
        edges = [item for item in self.scene().items() if isinstance(item, Edge)]
        for edge in edges:
            edge.setEdgeThickness(edgeThickness)
    """
    Controls for visualization of general purpose controls
    """
    def LineEditChanged(self):
        """Handling Line Edit changes"""
        text = (self.Lineditor.text().encode('ascii','ignore')).replace(' ','')
        value = float(text)*1000
        self.EdgeWeight.emit(int(value))
    """
    Lineedit for the threshold values
    """
    def lineEdit(self):
        """Drawing the Line editor for the purpose of manualling entering the edge threshold"""
        self.Lineditor = QtGui.QLineEdit()
        self.Lineditor.setText(str(self.EdgeSliderValue))
        self.Lineditor.returnPressed.connect(self.LineEditChanged)
        self.EdgeWeight.connect(self.EdgeSliderForGraph.setValue)

    """
    Colors for the Graph and Edges 
    Defining the colors of edges and nodes
    """
    def Graph_Color(self,Annote, maxval = -1,minval = 1):
        if Annote != 0: 
            Annote = Annote -1
        if maxval == -1: 
            maxval = self.counter
        for i in range(minval,maxval):
            if i != (Annote+1):
                t = self.correlationTable().value(Annote, i-1)
                self.DataColor[i] = ColorToInt(self.colortable.getColor(t))
            else:
                self.DataColor[i] = ColorToInt(self.selectedColor)

    def Edge_Color(self):
        k= 0 
        for i in range(1,self.counter):
            for j in range(1,self.counter):
                if (i-1 >= j-1): 
                    continue
                try:
                    t = self.correlationTable().value(i-1,j-1)
                    self.EdgeColor[k] = ColorToInt(self.colortable.getColor(t))
                    k = k + 1 
                except KeyError:
                    continue

    """
    Functionality for having various key strokes during the graph interface view
    Events in the application
    """
    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_D:
            self.DisplayOnlyEdges = not(self.DisplayOnlyEdges)
            self.NodeSelected(self.HighlightedId) 
            self.Scene_to_be_updated.update()
        elif key == QtCore.Qt.Key_M:
            self.ModularityBehaviour()
        else:
            QtGui.QGraphicsView.keyPressEvent(self, event)
        self.Refresh()
    
    """
    wheel Events Changes   
    """    
    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, -event.delta() / 1040.0))
    """
    Scale things based on wheel events
    """
    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 5, 5)).width()
        if factor < 0.07 or factor > 100:
            return
        self.scale(scaleFactor, scaleFactor)
        del factor
