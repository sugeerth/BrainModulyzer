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

CURR =  path.abspath(path.join(__file__ ,"../..")) # going one directory up 
CURR = os.path.join(CURR, "SampleData/"+str(DataSetValue)+"/")

matrix_filename = str(os.path.join(CURR,'27NodeMatrix.csv'))
parcelation_filename = str(os.path.join(CURR, "allROIs.nii.gz"))
template_filename = str(os.path.join(CURR, "ch2better.nii.gz"))

#set the flag data around here for convenience, if you want to switch on or off 
# the other windows whenever you want
GraphWindowShowFlag = True
MainWindowShowFlag = True
CorrelationTableShowFlag = True
