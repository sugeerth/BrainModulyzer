## Standard Python packages
#-*- coding: utf-8 -*-
from PySide import QtCore, QtGui
import pprint
try:
    # ... reading NIfTI 
    import numpy as np
    # ... graph drawing
    import networkx as nx

except:
    print "Couldn't import all required packages. See README.md for a list of required packages and installation instructions."
    raise

"""Provides the main data structure for the network data"""
class GraphVisualization(QtGui.QWidget):
    """This class is responsible for GraphVisualization from the data given"""
    filename = ""
    regionSelected = QtCore.Signal(int)
    def __init__(self,data):
        super(GraphVisualization, self).__init__()
        self.data = data
        self.G = nx.from_numpy_matrix(self.data)  
        self.DrawHighlightedGraph()

    def Find_HighlightedEdges(self,weight = -0.54):
        self.ThresholdData = np.copy(self.data)
        low_values_indices = self.ThresholdData < weight  # Where values are low
        self.ThresholdData[low_values_indices] = 0
        self.g = nx.from_numpy_matrix(self.ThresholdData)  

    """

    """
    def DrawHighlightedGraph(self,weight=None):
        if not(weight):
            weight = self.data.min()
	self.Find_HighlightedEdges(weight)
        return self.g
