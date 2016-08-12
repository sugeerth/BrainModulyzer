"""
matrix_filename is a format where you will have an adjacency matrix in csv format 
with the headers indicating the brain regions of interest

template_filename provides with the outer brain atlas of the regions  

parcelation_filename provides the parcellation of the brain regions 

Make sure the parcellation files are in the nibabel format

matrix_filename = '/PATH_TO_YOUR_CORRELATION_MATRIX_FILE'
template_filename = '/PATH_TO_YOUR_TEMPLATE_FILE'
parcelation_filename = '/PATH_TO_YOUR_PARCELATION_FILE'
"""
import os.path as path
import sys

DataSetValue = 'Dataset1' # Change this to Dataset2 for other results

CURR =  path.abspath(path.join(__file__ ,"../..")) # going one directory up 
CURR = os.path.join(CURR, "SampleData/"+str(DataSetValue)+"/")

#DATASET 1
# matrix_filename = '/Users/sugeerthmurugesan/LBLProjects/TCBBDownload/TestDirectory/brain-vis-git/SampleData/Dataset2/fc_mat_mean_hc_64.csv'
# parcelation_filename = '/Users/sugeerthmurugesan/LBLProjects/TCBBDownload/TestDirectory/brain-vis-git/SampleData/Dataset2/all_parcels.nii.gz'
# template_filename = '/Users/sugeerthmurugesan/LBLProjects/TCBBDownload/TestDirectory/brain-vis-git/SampleData/Dataset2/MNI152_T1_2mm_brain.nii.gz'

#DATASET 2 
# matrix_filename = '/Users/sugeerthmurugesan/LBLProjects/TCBBDownload/TestDirectory/brain-vis-git/SampleData/Dataset1/FinalCSVData.csv'
# parcelation_filename = '/Users/sugeerthmurugesan/LBLProjects/TCBBDownload/TestDirectory/brain-vis-git/SampleData/Dataset1/allROIs.nii.gz'
# template_filename = '/Users/sugeerthmurugesan/LBLProjects/TCBBDownload/TestDirectory/brain-vis-git/SampleData/Dataset1/ch2better.nii.gz'

matrix_filename = str(os.path.join(CURR,'FinalCSVData.csv'))
parcelation_filename = str(os.path.join(CURR, "allROIs.nii.gz"))
template_filename = str(os.path.join(CURR, "ch2better.nii.gz"))

# matrix_filename1 = '/Users/sugeerthmurugesan/LBLProjects/TCBBDownload/TestDirectory/brain-vis-git/SampleData/Dataset1/ch2better.nii.gz'
# matrix_filename2 = os.path.join(CURR,'ch2better.nii.gz')

#set the flag data around here for convenience, if you want to switch on or off 
# the other windows whenever you want
GraphWindowShowFlag = True
MainWindowShowFlag = True
CorrelationTableShowFlag = False