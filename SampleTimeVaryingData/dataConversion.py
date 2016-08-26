import json
from pprint import pprint
import scipy.io
import numpy as np
import community as cm
import pprint
import os,sys
from random import randint
import networkx as nx
import pydot 
import bct
import Pycluster
import pickle 
import pyparsing
import numpy
import csv

"""
This is the data that needs to be changed based on the format of the data
"""
weight = 0
ThresholdValue = 0

width = 1280,
height = 800;

SampleTimeVaryingGraphs = 'fc_mat_sliding_21_21_205.txt'

class CommunityDataProcessing(object):
	def __init__(self):
		self.communityData = None
		self.timestepPartition = None

	def ModelGraph(self, NumpyGraphData, Timestep):
		low_values_indices = None
		ThresholdData = np.copy(NumpyGraphData[Timestep])
		ThresholdData = nx.from_numpy_matrix(ThresholdData) 
		return ThresholdData

	def ModelNegativeGraph(self, NumpyGraphData, Timestep):
		ThresholdData = np.copy(NumpyGraphData[Timestep])
		ThresholdData = self.ThresholdMatrix(ThresholdData)
		ThresholdData = nx.from_numpy_matrix(ThresholdData) 
		return ThresholdData

	def NetworkXKarateGraph(self,JsonData):
		G = nx.DiGraph()
		G.add_nodes_from(JsonData['nodes'])
		G.add_edges_from(JsonData['edges'])
		return G

	def ThresholdMatrix(self, data):
		for i in range(len(data)):
			for j in range(len(data)):
				if data[i,j] <= 0:
					pass
					# data[i,j] = 0
		return data

	"""
	Computing the layout from the algorithm in python
	"""
	def definePositions(self, CommunityGraph, prog):
		return nx.spring_layout(CommunityGraph)

	def defineConsensusCommunities(self, EpilepsyName, Timestep):
		self.timestepPartition = pickle.load(open(EpilepsyName))
		return self.timestepPartition[Timestep]

	def defineCommunities(self, CommunityGraph, data):
		newdata = np.array(data)
		partition = bct.modularity_louvain_und(newdata)
		print partition, "---------------"
		return partition

class dataProcessing(object):
	def __init__(self):
		"""
		Loading Static files onto the repository
		"""
		self.CommunityObject = CommunityDataProcessing()
		self.MatRenderData = self.loadSyntheticDatasets(SampleTimeVaryingGraphs)
		
		for i in range(205):
			self.GenerateCommunities(self.MatRenderData,i)

	def loadSyntheticDatasets(self, EnronDatasets):	
		"""
		Loads the enron dataset into the datastructure to show 

		graphData == 0--10 timesteps with nodes, edges and changes in graphs. 
		Idea to find out how the community structure cahnges and what happens 
		to the overall topology
		"""
		with open(SampleTimeVaryingGraphs) as f: 
			array=numpy.zeros((21,21))
			i = 0 
			counter = 0
			arraylist = numpy.zeros((205,21,21),dtype=np.float64)
			for line in f: 
				line = line.strip()
				data = np.array(map(float,line.split(' ')))
				for k,data1 in enumerate(data):
					if counter== 0 and i == 1 and k ==0:
						savedValue = data1
					arraylist[counter][i][k] = np.float64(data1)
				i = i+1 
				if (i == 21):
					counter = counter+1
					i = 0
		return arraylist

	def GenerateCommunities(self,Data, Timestep): 
		self.nodelist = [] 
		self.edgelist = []

		width =600
		height=600

		GraphForCommunity = self.CommunityObject.ModelNegativeGraph(Data, Timestep) 
		ThresholdData = nx.to_numpy_matrix(GraphForCommunity)
		CommunityHashmap = self.CommunityObject.defineCommunities(GraphForCommunity,ThresholdData) 

		print CommunityHashmap

	def returnDynamicData(self):
		return self.RenderData

dataProcessing()
