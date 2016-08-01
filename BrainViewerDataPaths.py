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

matrix_filename = '/Users/sugeerthmurugesan/LBLProjects/TCBBDownload/TestDirectory/brain-vis-git/SampleData/FinalCSVData.csv'
parcelation_filename = '/Users/sugeerthmurugesan/LBLProjects/TCBBDownload/TestDirectory/brain-vis-git/SampleData/allROIs.nii.gz'
template_filename = '/Users/sugeerthmurugesan/LBLProjects/TCBBDownload/TestDirectory/brain-vis-git/SampleData/ch2better.nii.gz'

#set the flag data around here for convenience, if you want to switch on or off 
# the other windows whenever you want
GraphWindowShowFlag = True
MainWindowShowFlag = True
CorrelationTableShowFlag = True





