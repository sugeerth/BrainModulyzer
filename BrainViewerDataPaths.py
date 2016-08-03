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
# parcelation_filename = '/Users/sugeerthmurugesan/LBLProjects/TCBBDownload/TestDirectory/brain-vis-git/SampleData/MNI152_T1_2mm_brain.nii.gz'
# parcelation_filename = '/Users/sugeerthmurugesan/Desktop/nipy-templates-0.2/templates/ICBM152/2mm/T1.nii.gz'
# parcelation_filename = '/Users/sugeerthmurugesan/Desktop/nipy-templates-0.2/templates/ICBM152/1mm/T1_brain.nii.gz'


template_filename = '/Users/sugeerthmurugesan/LBLProjects/TCBBDownload/TestDirectory/brain-vis-git/SampleData/ch2better.nii.gz'
# template_filename = '/Users/sugeerthmurugesan/LBLProjects/TCBBDownload/TestDirectory/brain-vis-git/SampleData/MNI152_T1_2mm_brain.nii.gz'
# template_filename = '/Users/sugeerthmurugesan/Desktop/nipy-templates-0.2/templates/ICBM152/2mm/T1.nii.gz'
# template_filename = '/Users/sugeerthmurugesan/Desktop/nipy-templates-0.2/templates/ICBM152/1mm/T1_brain.nii.gz'

#set the flag data around here for convenience, if you want to switch on or off 
# the other windows whenever you want
GraphWindowShowFlag = True
MainWindowShowFlag = True
CorrelationTableShowFlag = True