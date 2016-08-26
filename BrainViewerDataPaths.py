"""
matrix_filename is a format where you will have an adjacency matrix in csv format 
with the headers indicating the brain regions of interest
template_filename provides with the outer brain atlas of the regions  
parcelation_filename provides the parcellation of the brain regions 
Make sure the parcellation files are in the nibabel format
"""

import os.path as path
import sys

DataSetValue = 'Dataset1' # Change this to Dataset2 for other results

CURRP =  path.abspath(path.join(__file__ ,"../..")) # going one directory up 

CURR =  os.path.join(CURRP, "SampleTimeVaryingData/"+str(DataSetValue)+"/")
CURR1 = os.path.join(CURRP, "SampleData/"+str(DataSetValue)+"/") # template data is 
#it the old one?

matrix_filename = str(os.path.join(CURR,'fc_mat_sliding_21_21_205.txt'))
parcelation_filename = str(os.path.join(CURR, "21_nodes_comb.nii.gz"))
template_filename = str(os.path.join(CURR, "21_nodes_comb.nii.gz"))
# template_filename = str(os.path.join(CURR1, "ch2better.nii.gz"))

#set the flag data around here for convenience, if you want to switch on or off 
# the other windows whenever you want
GraphWindowShowFlag = True
MainWindowShowFlag = True
CorrelationTableShowFlag = False