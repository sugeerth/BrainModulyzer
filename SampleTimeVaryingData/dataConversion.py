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
					data[i,j] = 0
		return data

	"""
	Computing the layout from the algorithm in python
	"""
	def definePositions(self, CommunityGraph, prog):
		return nx.spring_layout(CommunityGraph)

	def defineConsensusCommunities(self, EpilepsyName, Timestep):
		self.timestepPartition = pickle.load(open(EpilepsyName))
		return self.timestepPartition[Timestep]

	def defineCommunities(self, CommunityGraph):
		partition=cm.best_partition(CommunityGraph)
		return partition

	def computeKmeans(self,Number_of_clusters,data, iterations = 100):
		partition = dict()
		nb_clusters = Number_of_clusters # this is the number of cluster the dataset is supposed to be partitioned into
		distances = nx.to_numpy_matrix(data)

		clusterid, error, nfound = Pycluster.kcluster(distances, nclusters= nb_clusters, npass=300)

		uniq_ids = list(set(clusterid))
		new_ids = [ uniq_ids.index(val) for val in clusterid]

		for i,value in enumerate(new_ids):
			partition[i] = value
		return partition

class dataProcessing(object):
	def __init__(self):
		"""
		Loading Static files onto the repository
		"""
		self.CommunityObject = CommunityDataProcessing()
		self.MatRenderData = self.loadSyntheticDatasets(SampleTimeVaryingGraphs)

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

	def loadMatFiles(self, SeizureGraph):
		graphData=scipy.io.loadmat(SeizureGraph)
		graphData = graphData['conData']
		return graphData

	def loadJSONFiles(self,KarateGraph):
		with open(KarateGraph) as data_file:    
			graphData = json.load(data_file)
		return graphData

	def NetworkXFileForAnalysis(self,Data):
		GraphData = cm.best_partition(Data)
		print GraphData

	def formatEarlierConsensusMatrix(self,Data, Timestep): 
		self.nodelist = [] 
		self.edgelist = []
		
		width =600
		height=600

		GraphForCommunity = self.CommunityObject.ModelGraph(Data, Timestep) 
		CommunityHashmap = self.CommunityObject.defineConsensusCommunities(EpilepsyName1, Timestep) 

		ThresholdData = nx.to_numpy_matrix(GraphForCommunity)

	def returnDynamicData(self):
		return self.RenderData

dataProcessing()
