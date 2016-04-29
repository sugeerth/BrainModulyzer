import csv
import sys
import math
from collections import defaultdict
from PySide import QtCore, QtGui
from sys import platform as _platform
import weakref
import cProfile
import os

class QuantData(QtCore.QObject):
	DataChange = QtCore.Signal(bool)
	def __init__(self,widget):
		super(QuantData,self).__init__()
		data = widget.correlationTableObject
		self.widget = widget
		self.BrainRegions = data.RegionName[0]
		self.data_list = []
		self.header = ['Regions', 'Centrality','Participation','Betweenness']

		for i in range(widget.counter-1):
			self.data_list.append((self.BrainRegions[i],"{0:.2f}".format(widget.Centrality[i]),"{0:.2f}".format(widget.ParticipationCoefficient[i]),"{0:.2f}".format(widget.Betweeness[i])))
	
	def ThresholdChange(self,State):
		self.data_list = []
		for i in range(self.widget.counter-1):
			self.data_list.append((self.BrainRegions[i],"{0:.2f}".format(self.widget.Centrality[i]),"{0:.2f}".format(self.widget.ParticipationCoefficient[i]),"{0:.2f}".format(self.widget.Betweeness[i])))
		self.DataChange.emit(True)

	def getHeader(self):
		return self.header

	def getData_list(self):
		return self.data_list