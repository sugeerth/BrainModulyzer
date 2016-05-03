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

from VisitInterface.visit_interface import GetColor

from GraphDataStructure import GraphVisualization
from DendogramModule.dendogram import dendogram, DendoNode


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
        self.communityMultiple = defaultdict(list)
        self.colortable=colortable
        self.BoxGraphWidget = BoxGraphWidget
        self.BoxTableWidget = BoxTableWidget
        self.Ui = Ui
        self.DisplayOnlyEdges = False
        self.level = -1
        self.selectedColor = selectedColor
        self.volumeRendererColor = list()
        self.Graph_data = weakref.ref(Graph_data)
        self.Tab_2_CorrelationTable = weakref.ref(Tab_2_CorrelationTable)
        self.ColorNodesBasedOnCorrelation =True
        self.communityObject = None
        self.correlationTable = weakref.ref(correlationTable)
        self.correlationTableObject = self.correlationTable()
        self.partition =[]
        self.sortedValues = None
        self.setTransp = True
        self.communityPos = dict()
        self.Matrix = []
        self.oneLengthCommunities=[]
        self.hoverRender = True
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
        self.Check = False
        self.DataColor = np.zeros(self.counter)
        self.EdgeColor = np.zeros(self.counter * self.counter)
        self.ColorToBeSentToVisit = list() 
        self.EdgeSliderValue = self.Max - 0.01
        self.nodesize = 7
        self.grayOutNodes = True
        self.PositionPreserve = True

        self.Graph_Color(-1)
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
        self.scaleView(2.0)

        self.ColorVisit = []
        self.NodeIds = []

        self.wid = QtGui.QWidget()
        self.hbox = QtGui.QVBoxLayout()

        self.First= True
        self.node = None
        self.clut= np.zeros(self.counter)
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
        self.setLayout('spring')


    """
    A metric that we is used in the analysis
    """
    def participation_coefficient(self,G, weighted_edges=False):
        """"Compute participation coefficient for nodes.
        
        Parameters
        ----------
        G: graph
          A networkx graph
        weighted_edges : bool, optional
          If True use edge weights
        
        Returns
        -------
        node : dictionary
          Dictionary of nodes with participation coefficient as the value
        
        Notes
        -----
        The participation coefficient is calculated with respect to a community
        affiliation vector. This function uses the community affiliations as determined
        by the Louvain modularity algorithm (http://perso.crans.org/aynaud/communities/).
        """
        partition = cm.best_partition(G)
        partition_list = []
        for count in range(len(partition)):
            partition_list.append(partition[count])
        
        n = G.number_of_nodes()
        Ko = []
        for node in range(n):
            node_str = np.sum([G[node][x]['weight'] for x in G[node].keys()])
            Ko.append(node_str)
        Ko = np.array(Ko)
        G_mat_weighted = np.array(nx.to_numpy_matrix(G))
        G_mat = (G_mat_weighted != 0) * 1
        D = np.diag(partition_list)
        Gc = np.dot(G_mat, D)
        Kc2 = np.zeros(n)
        for i in range(np.max(partition_list) + 1):
            Kc2 = Kc2 + (np.sum(G_mat_weighted * (Gc == i),1) ** 2)
        

        P = np.ones(n) - (Kc2/(Ko **2))
        
        D = dict()
        for i in range(len(P)):
            D[i]=P[i]
            
        return D

    """
    ModularityBehaviour
    A function that makes it possible to analysis the various graphs such 
    number of connected components vs modularity of the louvain algorithm 
    This is a good method to see how the usability of the louvain method. 
    """
    def ModularityBehaviour(self):

        Number_of_Connected_Components = dict()
        Number_of_Communities = dict()
        modularity = dict()
        start= int(self.correlationTable().data.min()*1000)
        end = int(self.correlationTable().data.max()*1000)
        g1 = self.Graph_data().DrawHighlightedGraph(self.EdgeSliderValue)
        # counter = 0.225
        partition=cm.best_partition(g1)
        Number_of_Communitie = len(set(partition.values()))

        for i in range(0,end):
            counter = float(i)/1000
            g1 =  self.Graph_data().DrawHighlightedGraph(counter)
            try: 
                partition=cm.best_partition(g1)
                modularity[i] = cm.modularity(partition, g1)
                Number_of_Connected_Components[i] = nx.number_connected_components(g1)
                Number_of_Communities[i] = len(set(partition.values()))
            except AttributeError:
                continue

        f=open("modularity.txt", "wb")
        w = csv.writer(f)
        for key, val in modularity.items():
            w.writerow([key, val])
        f.close()


        f=open("number_connected_components.txt", "wb")
        w = csv.writer(f)
        for key, val in Number_of_Connected_Components.items():
            w.writerow([key, val])
        f.close()
        
        f=open("Number_of_Communities.txt", "wb")
        w = csv.writer(f)
        for key, val in Number_of_Communities.items():
            w.writerow([key, val])
        f.close()

        # print("Find_InterModular_Edge_correlativity CorrelationTable --- %f seconds ---" % (time.time() - start_time))

    def changeHighlightedEdges(self,state):
        if state: 
            for edge in self.edges:
                 edge().setHighlightedColorMap(False)
        else: 
            for edge in self.edges:
                 edge().setHighlightedColorMap(True)

        self.Scene_to_be_updated.update()

    def LayoutCalculation(self):

        self.setLayout('spring')

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

    def ColorForVisit(self,partition):
        self.ColorToBeSentToVisit = []
        for key,value in partition.items():
            self.ColorToBeSentToVisit.append(self.ColorVisit[value])

    def Find_InterModular_Edge_correlativity(self):

        # start_time = time.time()
        # Induced graph is the data structure responsible for the adjacency matrix of the community
        self.Matrix = nx.to_numpy_matrix(self.induced_graph)
        # Matrix Before calculating the correlation strength
        # finding out the lower half values of the matrix, can discard other values as computationally intensive
        self.Matrix = np.tril(self.Matrix,-1)
        i=0 
        j=0 
        # Sum = np.copy(Matrix)
        SumTemp = 0
        Edges = 0 
        nodes1 = [item for item in self.scene().items() if isinstance(item, Node)]
        # ite1rateing over the indices
        for community in set(self.partition.values()):
            i= i + 1
            j=0
            for community2 in set(self.partition.values()):
                j= j + 1
                # Not Calculating the communities which are communities to itself 
                if community == community2:
                    continue
                # Calculating the correlation strength only with the lower half of the adjacency matrix
                if i <= j: 
                    continue
                # list_nodes1 and list_nodes2 indicate which nodes are actually present in these communties
                list_nodes1 = [nodes for nodes in self.partition.keys() if self.partition[nodes] == community]
                list_nodes2 = [nodes for nodes in self.partition.keys() if self.partition[nodes] == community2]
                # Re-initializing the 
                SumTemp = 0
                Edges = 0
                for node1 in nodes1:
                    if node1.counter-1 in list_nodes1:
                        for node2 in nodes1:
                            if node2.counter-1 in list_nodes2:
                                if node1.counter-1 == node2.counter-1:
                                        continue
                                if self.Graph_data().ThresholdData[node1.counter-1][node2.counter-1] > 0:
                                    Edges = Edges + 1
                if Edges != 0: 
                    Sum=self.Matrix[i-1,j-1]/Edges
                    self.Matrix[i-1,j-1] = Sum

        self.induced_graph = nx.from_numpy_matrix(self.Matrix)

    def Find_Initial_Positions(self):
        self.communityPos.clear()

        count = 0
        nodes1 = [item for item in self.scene().items() if isinstance(item, Node)]

        for community in set(self.partition.values()):
            Sumx = 0
            Sumy = 0

            list_nodes = [nodes for nodes in self.partition.keys() if self.partition[nodes] == community]
            for node in nodes1:
                if node.counter-1 in list_nodes:
                    Sumx = Sumx + self.pos[node.counter-1][0] 
                    Sumy = Sumy + self.pos[node.counter-1][1]
            centroidx = Sumx/len(list_nodes)
            centroidy = Sumy/len(list_nodes)
            self.communityPos[community] = (centroidx,centroidy)
            count = count + 1
        return self.communityPos

    def changeGrayOutNodes(self,state):
        self.grayOutNodes = not(self.grayOutNodes)
        if not(self.level == -1):
            self.ChangeCommunityColor(self.level-1)
        else: 
            self.ChangeCommunityColor()

    def changeDendoGramLevel(self,level):
        self.level = level
        self.ChangeCommunityColor(self.level)

    """
    Threshold changes events are called to this function  
    """
    def ChangeCommunityColor(self, level = -1):
            self.g =  self.Graph_data().DrawHighlightedGraph(self.EdgeSliderValue)
            self.ColorNodesBasedOnCorrelation = False 
            self.partition=cm.best_partition(self.g)
            self.induced_graph = cm.induced_graph(self.partition,self.g)
    
            if not(level == -1): 
                    dendo=cm.generate_dendogram(self.g)
                    g = cm.partition_at_level(dendo,level)
                    self.induced_graph1 = cm.induced_graph(g,self.g)
                    self.partition = g
                    self.induced_graph = self.induced_graph1

            self.Find_InterModular_Edge_correlativity()
            # Triggering a new window with the same color
            # If the Gray out option is clicked then gray out the nodes without the colors 
            self.ColorForCommunities(len(set(self.partition.values())))
            self.ColorForVisit(self.partition)
            nodes1 = [item for item in self.scene().items() if isinstance(item, Node)]
            count = 0
            for community in set(self.partition.values()):
                #Ensuring the right color to the right community is delivered
                list_nodes = [nodes for nodes in self.partition.keys() if self.partition[nodes] == community]

                for node in nodes1:
                    if node.counter-1 in list_nodes:
                        node.PutColor(self.clut[count])
                count = count + 1
            for node in nodes1: 
                node.allnodesupdate()
                break

            clut=self.clut
            Max= self.Max
            Graph = self
            Matrix = self.Matrix
            ma = np.ma.masked_equal(Matrix, 0.0)
            Min1 = ma.min()
            Max1 = Matrix.max()
            Pos = self.Find_Initial_Positions()

            """
            Generates a summary graph for analysis 
            """
            class CommunityWidget(QtGui.QGraphicsView):
                def __init__(self,induced_graph,correlationTable):
                    QtGui.QGraphicsView.__init__(self)
                    self.induced_graph = induced_graph
                    self.correlationTable = weakref.ref(correlationTable)
                    self.correlationTableObject = self.correlationTable()
                    self.setMinimumSize(200, 150)
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
                    # method to add a new graph visualization                
                    i = 0
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
                    self.scaleView(math.pow(2.0, -500 / 1040.0))

                    self.nodes = [item for item in scene.items() if isinstance(item, Node)]
                    self.edges = [item for item in scene.items() if isinstance(item, Edge)]


                def wheelEvent(self, event):
                    self.scaleView(math.pow(2.0, -event.delta() / 1040.0))

                def scaleView(self, scaleFactor):
                    factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
                    if factor < 0.07 or factor > 100:
                        return
                    self.scale(scaleFactor, scaleFactor)
                    del factor

            """
            Generates a new window so that you can access the views related to community 
            analysis
            """
            def newwindow():
                for i in reversed(range(self.hbox.count())): 
                        self.hbox.itemAt(i).widget().close()

                community = CommunityWidget(self.induced_graph,self.correlationTableObject)
                Dendogram = dendogram(self,self.g)

                self.hbox.setContentsMargins(0, 0, 0, 0)

                self.hbox.addWidget(community)
                self.hbox.setContentsMargins(0, 0, 0, 0)

                self.hbox.addWidget(Dendogram)
                self.hbox.setContentsMargins(0, 0, 0, 0)

                self.communityObject = community
                self.dendogramObject = Dendogram
                self.hbox.setContentsMargins(0, 0, 0, 0)
                self.wid.setContentsMargins(0, 0, 0, 0)

                self.wid.setLayout(self.hbox)
            newwindow()
            self.CommunityColorAndDict.emit(self.ColorToBeSentToVisit,self.partition)

    def ColorForCommunities(self,counter):
        k=self.updateCommunityColors(counter)
        self.ColorVisit = []
        m = len(self.oneLengthCommunities)
        for i in range(counter):
            if i in self.oneLengthCommunities: 
                r,g,b = 0.5,0.5,0.5
                self.clut[i] = (255 << 24 | int(255*r) << 16 | int(255*g) << 8 | int(255*b))
                self.ColorVisit.append((r*255,g*255,b*255,255))
            else:
                r, g, b =  colorsys.hls_to_rgb(float(i) / float(counter-m), 0.8, 0.9)
                self.clut[i] = (255 << 24 | int(255*r) << 16 | int(255*g) << 8 | int(255*b))
                self.ColorVisit.append((r*255,g*255,b*255,255))

    """
    Function that actually assigns to the nodes based on the 
    mode of the application
    This can either be the correlation color or the community color
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
                self.ChangeCommunityColor(self.level-1)
            else: 
                self.ChangeCommunityColor()
            self.CommunityMode.emit(True)
            self.CommunityColor.emit(self.ColorToBeSentToVisit)
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
            # Entering the correlation mode initiate the window to resize to normal (Workaround not adrdressing the root problem)
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
    """
    def updateCommunityColors(self,counter):
        self.communityMultiple.clear()
        for key,value in self.partition.items():
            self.communityMultiple[value].append(key)

        k=0
        self.oneLengthCommunities =[]
        for i in range(counter):
            if len(self.communityMultiple[i]) == 1: 
                self.oneLengthCommunities.append(i)
                for j in self.communityMultiple[i]:
                    pass
                k=k+1
        return k

    """
    Very important Function: 
    Changes in the layout are calculated here 
    New data for display is displyed
    Organized into changes in the layout options
    You can add additional layouts by having 

    if (Layout == "Entry in the dropdown menu")
        code for calculating the new layout-- Make sure the new layout is scalable

    """
    def setLayout(self,Layout='sfdp'):
            Layout = (Layout.encode('ascii','ignore')).replace(' ','')
            self.g =  self.Graph_data().DrawHighlightedGraph(self.EdgeSliderValue)

            if not(self.ColorNodesBasedOnCorrelation):
                partition=cm.best_partition(self.g)
                size = float(len(set(partition.values())))
                induced_graph = cm.induced_graph(partition,self.g)
                if not(self.level == -1): 
                    dendo=cm.generate_dendogram(self.g)
                    g = cm.partition_at_level(dendo,self.level)
                    partition = g
                self.ColorForCommunities(len(set(partition.values())))
            if (Layout == "circular") or (Layout == "shell") or (Layout == "random") or (Layout == "fruchterman_reingold_layout") or (Layout == "spring") or (Layout == "spectral"):
                if (Layout == "spring"): 
                    if self.First:
                        self.First =False
                        self.neewPos=nx.spring_layout(self.g,weight = 'weight', k = 0.55, iterations = 20,scale =500)
                        self.pos=self.neewPos
                    else: 
                        self.neewPos=nx.spring_layout(self.g,pos=self.pos,weight = 'weight',scale = 500)
                        self.pos=self.neewPos
                    count = 0 
                    Factor = 1
                elif (Layout == "random") or (Layout == "shell") or (Layout == "neato"):
                    self.neewPos=eval('nx.'+Layout+'_layout(self.g)')
                    self.pos=self.neewPos
                    Factor = 1000
                else: 
                    self.neewPos=eval('nx.'+Layout+'_layout(self.g,scale=1000)')
                    self.pos=self.neewPos
                    Factor = 1
                if not(self.ColorNodesBasedOnCorrelation): 
                        self.ColorNodesBasedOnCorrelation = False 
                        if not(self.level == -1):
                            self.ChangeCommunityColor(self.level-1)
                        else: 
                            self.ChangeCommunityColor()
            else:
                if Layout != "circo":
                    self.pos=nx.graphviz_layout(self.g,prog=Layout,args='-Gsep=.25,-GK=20-Eweight=2')
                    Factor = 0.7 + self.counter/100
                    if Layout == 'sfdp':
                        Factor = 10
                else:
                    print "Before Circo" 
                    self.pos=nx.graphviz_layout(self.g,prog=Layout)
                    print "After Circo" 

                    Factor = 0.8
                if not(self.ColorNodesBasedOnCorrelation): 
                    self.ColorNodesBasedOnCorrelation = False 
                    if not(self.level == -1):
                        self.ChangeCommunityColor(self.level-1)
                    else: 
                        self.ChangeCommunityColor()

            # Degree Centrality for the the nodes involved
            self.Centrality=nx.degree_centrality(self.g)
            self.Betweeness=nx.betweenness_centrality(self.g)  
            self.LoadCentrality = nx.load_centrality(self.g)
            self.ParticipationCoefficient = self.participation_coefficient(self.g,True)
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
        self.ParticipationCoefficient = self.participation_coefficient(self.g,True)
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

    def setNodeSizeOption(self,state):
        self.nodeSizeFactor = state
        self.UpdateThresholdDegree()

    def SelectLayout(self, Layout):
        self.setLayout(Layout)
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
        for edge in self.communityObject.edges:
            edge.update()

        for node in self.communityObject.nodes:
            node.update()

        self.communityObject.Scene_to_be_updated.update()

    """
    Controls for the second functionality on changing the size of 
    the node. 
    For now we dont require it creastes additional Complexity
    def NodeSlider(self):
        self.slider2 = QtGui.QSlider(QtCore.Qt.Horizontal,self)
        self.slider2.setRange(0, 10)
        self.slider2.setValue(0)
        self.slider2.setToolTip("Node Size: %0.2f" % (self.nodesize))
        self.slider2.setTracking(False)
        self.slider2.valueChanged[int].connect(self.ChangeNodeSizeSlider)
        self.slider2.hide()

    def ChangeNodeSizeSlider(self,value):
        self.nodesize =  value
        self.slider2.setToolTip("Node Size: %0.2f" % (self.nodesize))
        nodes = [item for item in self.scene().items() if isinstance(item, Node)]
        for node in nodes:
            if node.counter == (self.HighlightedId+1):
                continue
            node.ChangeNodeSize(value)
    """
    
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

        if self.communityObject:
            nodes = [item for item in self.communityObject.scene().items() if isinstance(item, Node)]
            for node in nodes:
                node.setAcceptHoverEvents(self.hoverRender)
                node.update()

            edges = [item for item in self.communityObject.scene().items() if isinstance(item, Edge)]
            for edge in edges:
                edge.setAcceptHoverEvents(self.hoverRender)
                edge.update()

            DendoNodes = [item for item in self.dendogramObject.scene.items() if isinstance(item, DendoNode)]
            AllEdges = [item for item in self.dendogramObject.scene.items() if isinstance(item, Edge)]
            
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
            self.setLayout(self.Layout)

        for edge in self.edges:
            edge().Threshold(value_for_slider)
        
        if not(self.ColorNodesBasedOnCorrelation):
            if not(self.PositionPreserve):
                pass
            else:
                if not(self.level == -1):
                    self.ChangeCommunityColor(self.level-1)
                else: 
                    self.ChangeCommunityColor()
            self.CommunityColor.emit(self.ColorToBeSentToVisit)
        
        self.UpdateThresholdDegree()
        self.Scene_to_be_updated.update()
    """
    Controls for visualization of general purpose controls
    """
    def LineEditChanged(self):
        """Handling Line Edit changes"""
        text = (self.Lineditor.text().encode('ascii','ignore')).replace(' ','')
        value = float(text)*1000
        self.EdgeWeight.emit(int(value))

    def slider_imple(self):
        """implementation of Edge threshold sliders"""
        self.EdgeSliderForGraph = QtGui.QSlider(QtCore.Qt.Horizontal,self)
        self.EdgeSliderForGraph.setTracking(False)
        self.EdgeSliderForGraph.setRange( self.Graph_data().data.min()*1000 ,  self.Graph_data().data.max()* 1000 )
        self.EdgeSliderForGraph.setValue(self.EdgeSliderValue*1000)
        self.EdgeSliderForGraph.setToolTip("Edge Weight: %0.2f" % (self.EdgeSliderValue))
        self.interval=((0.1-5)/10)*(-1)
        self.EdgeSliderForGraph.valueChanged[int].connect(self.ChangePropertiesOfGraph)

    def changeEdgeThickness(self,value):
        NormValue = float(value)
        edgeThickness = 1 + float(NormValue)
        edges = [item for item in self.scene().items() if isinstance(item, Edge)]
        for edge in edges:
            edge.setEdgeThickness(edgeThickness)

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
        self.volumeRendererColor=[]
        for i in range(minval,maxval):
            if i != (Annote+1):
                t = self.correlationTable().value(Annote, i-1)
                self.DataColor[i] = ColorToInt(self.colortable.getColor(t))
                # self.volumeRendererColor.append(tuple(map(lambda x: x/255,self.colortable.getColor(t))))
            else:
                self.DataColor[i] = ColorToInt(self.selectedColor)
                self.volumeRendererColor.append(tuple(map(lambda x: x/255,self.selectedColor)))

    def Edge_Color(self):
        k= 0 
        # start_time2 = time.time()
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
        
    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, -event.delta() / 1040.0))

    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 5, 5)).width()
        if factor < 0.07 or factor > 100:
            return
        self.scale(scaleFactor, scaleFactor)
        del factor
