import csv
import math
import time
import colorsys
from collections import defaultdict
from PySide import QtCore, QtGui
from PySide.QtCore import *
import bct
import warnings
warnings.filterwarnings("ignore")

from itertools import combinations as comb

import weakref

import community as cm
import numpy as np
import networkx as nx

from GraphInterface.DendogramModule.dendogram import dendogram, DendoNode
from GraphInterface.GraphicsItems.Edge import Edge
from GraphInterface.GraphicsItems.Node import Node

"""
Generates a summary graph for analysis 
"""
class CommunityWidget(QtGui.QGraphicsView):
    def __init__(self,Graph,induced_graph,correlationTable,clut,Max, Matrix, ma, Min1, Max1, Pos):
        QtGui.QGraphicsView.__init__(self)
        self.induced_graph = induced_graph
        self.correlationTable = weakref.ref(correlationTable)
        self.correlationTableObject = self.correlationTable()
        self.setMinimumSize(200, 150)
      
        self.Max = Max
        self.Min1 = Min1
        self.Max1 = Max1
        self.Pos = Pos
        self.ma = ma
        self.Graph = Graph
        self.Matrix = Matrix
        self.clut = clut
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
        self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)

        i = 0

        self.communityPos = nx.nx_pydot.graphviz_layout(self.induced_graph,prog='fdp',args='-Gsep=.25,-GK=20-Eweight=2')
        # self.communityPos = nx.spring_layout(self.induced_graph,pos=self.Pos,weight='weight',scale=450)
        for node in self.induced_graph.nodes():
            i = i + 1
            node_value=Node(self.Graph,i,self.correlationTableObject,True)
            self.NodeIds.append(node_value)
            scene.addItem(node_value)
            x,y=self.communityPos[node]
            node_value.setPos(x,y)
            node_value.PutColor(self.clut[i-1])
        k =0
        for i,j in self.induced_graph.edges():
                Weight = self.induced_graph[i][j]['weight'] 
                Edge_Value = 1+(float(Weight-self.Min1)/(self.Max1 - self.Min1))*5
                scene.addItem(Edge(self.Graph,self.NodeIds[i],self.NodeIds[j],k, i,j,self.Max,((self.Matrix[j,i]-self.Min1)/(self.Max1 - self.Min1))*5,True))
                k = k + 1 

        self.setSceneRect(self.Scene_to_be_updated.itemsBoundingRect())
        self.setScene(self.Scene_to_be_updated)
        self.fitInView(self.Scene_to_be_updated.itemsBoundingRect(),QtCore.Qt.KeepAspectRatio)
        self.scaleView(math.pow(2.5, -900 / 1040.0))

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

class communityDetectionEngine(QtCore.QObject):
    CalculateColors = QtCore.Signal(int)
    CalculateFormulae = QtCore.Signal(bool)

    def __init__(self,Graphwidget, counter):
        super(communityDetectionEngine, self).__init__()
        self.Graphwidget= Graphwidget
        self.communityMultiple = defaultdict(list)
        self.clut= np.zeros(counter)
        self.communityPos = dict()
        self.pos = None
        self.ColorVisit = []
        self.counter = counter

    """
    Colors to send to communities
    """
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
    Send the comuted communtiy Colors to Visit 
    """
    def ColorForVisit(self,partition):
        self.ColorToBeSentToVisit = []
        for key,value in partition.items():
            self.ColorToBeSentToVisit.append(self.ColorVisit[value])

    """
    Class called to calculate the graph Layout during community detection
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

    def get_Pos_Neg_Partition(self,Graph):
        GraphData=np.array(nx.to_numpy_matrix(Graph))
        partitionArray = bct.modularity_louvain_und(GraphData)
        partition = dict()
        for i,data in enumerate(partitionArray[0]):
            print i,data 
            partition[i] = int(data-1) 

        return partition

    """
    Class called to calculate the graph Layout during community detection
    """
    def communityLayoutCalculation(self, Layout, g):
        self.g = g 

        if not(self.Graphwidget.ColorNodesBasedOnCorrelation):
            partition=self.get_Pos_Neg_Partition(self.g)
            size = float(len(set(partition.values())))
            induced_graph = cm.induced_graph(partition,self.g)
            if not(self.Graphwidget.level == -1): 
                dendo=cm.generate_dendrogram(self.g)
                g = cm.partition_at_level(dendo,self.Graphwidget.level)
                partition = g
            self.ColorForCommunities(len(set(partition.values())))
        if (Layout == "circular") or (Layout == "shell") or (Layout == "random") \
        or (Layout == "fruchterman_reingold_layout") or (Layout == "spring") or (Layout == "spectral"):
            if (Layout == "spring"): 
                if self.Graphwidget.First:
                    self.Graphwidget.First =False
                    neewPos=nx.spring_layout(self.g,weight = 'weight', k = 0.55, iterations = 20,scale =500)
                    pos=neewPos
                else: 
                    neewPos=nx.spring_layout(self.g,pos=self.pos,weight = 'weight',scale = 500)
                    pos=neewPos
                count = 0 
                Factor = 1
            elif (Layout == "random") or (Layout == "shell") or (Layout == "neato"):
                neewPos=eval('nx.'+Layout+'_layout(self.g)')
                pos=neewPos
                Factor = 2000
            else: 
                neewPos=eval('nx.'+Layout+'_layout(self.g,scale=1000)')
                pos=neewPos
                Factor = 1
            if not(self.Graphwidget.ColorNodesBasedOnCorrelation): 
                    self.Graphwidget.ColorNodesBasedOnCorrelation = False 
                    if not(self.Graphwidget.level == -1):
                        self.ChangeCommunityColorAndInstantiateHierarchy(self.Graphwidget.level-1)
                    else: 
                        self.ChangeCommunityColorAndInstantiateHierarchy()
        else:
            if Layout != "circo":
                pos=nx.nx_pydot.graphviz_layout(self.g,prog=Layout,args='-Gsep=.25,-GK=20-Eweight=2')
                Factor = 0.7 + self.counter/100
                if Layout == 'sfdp':
                    Factor = 1
            else:
                pos=nx.nx_pydot.graphviz_layout(self.g,prog=Layout)
                Factor = 0.7

            if not(self.Graphwidget.ColorNodesBasedOnCorrelation): 
                self.Graphwidget.ColorNodesBasedOnCorrelation = False 
                if not(self.Graphwidget.level == -1):
                    self.ChangeCommunityColorAndInstantiateHierarchy(self.Graphwidget.level-1)
                else: 
                    self.ChangeCommunityColorAndInstantiateHierarchy()
        self.pos = pos
        return pos,Factor

    """
    Threshold changes events are called to this function  
    """
    def ChangeCommunityColorAndInstantiateHierarchy(self, level = -1):
        self.g =  self.Graphwidget.Graph_data().DrawHighlightedGraph(self.Graphwidget.EdgeSliderValue)
        self.ColorNodesBasedOnCorrelation = False 
        self.partition=self.get_Pos_Neg_Partition(self.g)
        self.induced_graph = cm.induced_graph(self.partition,self.g)

        if not(level == -1): 
                dendo=cm.generate_dendrogram(self.g)
                g = cm.partition_at_level(dendo,level)
                self.induced_graph1 = cm.induced_graph(g,self.g)
                self.partition = g
                self.induced_graph = self.induced_graph1

        # Induced graph is the data structure responsible for the adjacency matrix of the community
        # Matrix Before calculating the correlation strength
        # finding out the lower half values of the matrix, can discard other values as computationally intensive

        # self.Find_InterModular_Edge_correlativity()
        self.Matrix = nx.to_numpy_matrix(self.induced_graph)
        
        # Triggering a new window with the same color
        # If the Gray out option is clicked then gray out the nodes without the colors 
        self.ColorForCommunities(len(set(self.partition.values())))
        self.ColorForVisit(self.partition)

        nodes1 = [item for item in self.Graphwidget.scene().items() if isinstance(item, Node)]
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
        Max= self.Graphwidget.Max
        Graph = self.Graphwidget
        Matrix = self.Matrix
        ma = np.ma.masked_equal(Matrix, 0.0)
        Min1 = ma.min()
        Max1 = Matrix.max()
        Pos = self.Find_Initial_Positions()

        """
        Generates a new window so that you can access the views related to community 
        analysis
        """
        def newwindow():
            for i in reversed(range(self.Graphwidget.hbox.count())): 
                    self.Graphwidget.hbox.itemAt(i).widget().close()

            community = CommunityWidget(self.Graphwidget,self.induced_graph,self.Graphwidget.correlationTableObject, clut,Max, Matrix, ma, Min1, Max1, Pos)
            Dendogram = dendogram(self.Graphwidget,self.g,clut)

            self.Graphwidget.hbox.setContentsMargins(0, 0, 0, 0)

            self.Graphwidget.hbox.addWidget(community)
            self.Graphwidget.hbox.setContentsMargins(0, 0, 0, 0)

            self.Graphwidget.hbox.addWidget(Dendogram)
            self.Graphwidget.hbox.setContentsMargins(0, 0, 0, 0)

            self.communityObject = community
            self.dendogramObject = Dendogram

            self.Graphwidget.hbox.setContentsMargins(0, 0, 0, 0)
            self.Graphwidget.wid.setContentsMargins(0, 0, 0, 0)

            self.Graphwidget.wid.setLayout(self.Graphwidget.hbox)

        newwindow()
        self.Graphwidget.CommunityColorAndDict.emit(self.ColorToBeSentToVisit,self.partition)

    """
    Start with initial positions for the community overview 
    graph 
    """
    def Find_Initial_Positions(self):
        self.communityPos.clear()

        count = 0
        nodes1 = [item for item in self.Graphwidget.scene().items() if isinstance(item, Node)]

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

    """
    Finds the inter-modular edges in the community graph
    Algorithm portrayed below
    """
    def Find_InterModular_Edge_correlativity(self):
        # Induced graph is the data structure responsible for the adjacency matrix of the community
        self.Matrix = nx.to_numpy_matrix(self.induced_graph)
        # Matrix Before calculating the correlation strength
        # finding out the lower half values of the matrix, can discard other values as computationally intensive
        self.Matrix = np.tril(self.Matrix,-1)
        i=0
        Sum = 0 
        j=0 
        SumTemp = 0
        Edges = 0 
        nodes1 = [item for item in self.Graphwidget.scene().items() if isinstance(item, Node)]
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
                                if self.Graphwidget.Graph_data().ThresholdData[node1.counter-1][node2.counter-1] > 0:
                                    Edges = Edges + 1
                if Edges != 0: 
                    Sum=float("{0:.2f}".format(self.Matrix[i-1,j-1]/Edges))
                self.Matrix[i-1,j-1] = Sum

        self.induced_graph = nx.from_numpy_matrix(self.Matrix)

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
        g1 = self.Graphwidget.Graph_data().DrawHighlightedGraph(self.Graphwidget.EdgeSliderValue)
        # counter = 0.225
        partition=self.get_Pos_Neg_Partition(g1)
        Number_of_Communitie = len(set(partition.values()))

        for i in range(0,end):
            counter = float(i)/1000
            g1 =  self.Graphwidget.Graph_data().DrawHighlightedGraph(counter)
            try: 
                partition=self.get_Pos_Neg_Partition(g1)
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

    """
    Custom Made--Metric for visualization 
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
        partition = self.get_Pos_Neg_Partition(G)
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
       