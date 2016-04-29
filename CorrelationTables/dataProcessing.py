
from PySide import QtCore, QtGui
import math
import weakref
from PIL import Image
import numpy as np

class dataProcessing(object):
	    def __init__(self, Brain_image_filename,Electrode_Ids_filename,SelectedElectrodes_filename,Electrode_data_filename,Electrode_mat_filename):
			self.im = Image.open(Brain_image_filename)
			self.syllableUnit = 1 
			self.timestep =1 
			self.mat = np.zeros((54,54))
			self.ElectrodeIds = np.zeros((54,54))
			self.ElectodeData = np.zeros((54,54))

