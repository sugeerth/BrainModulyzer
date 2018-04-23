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

matrix_filename = str(os.path.join(CURR,'27NodeMatrix.csv')) # "fc_mat_mean_hc_64.csv" for Dataset2
parcelation_filename = str(os.path.join(CURR, "allROIs.nii.gz")) # "MNI152_T1_2mm_brain.nii.gz" for Dataset2
template_filename = str(os.path.join(CURR, "ch2better.nii.gz")) # "all_parcels.nii.gz" for Dataset2, it maynot work first time, but you run the tool agin it will

#set the flag data around here for convenience, if you want to switch on or off 
# the other windows whenever you want
GraphWindowShowFlag = True
MainWindowShowFlag = True
CorrelationTableShowFlag = True
