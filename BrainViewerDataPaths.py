"""
matrix_filename is a format where you will have an adjacency matrix in csv format 
with the headers indicating the brain regions of interest

centre_filename are coordinate positions of the brain regions for the spheres in the 
anatomical layout 

centres_abbreviation is the abbreviation of the brain regions in the header 

template_filename provides with the outer brain atlas of the regions  

parcelation_filename provides the parcellation of the brain regions 

e.g. path
matrix_filename = '/PATH_TO_YOUR_DATA/27nodeMatrix.csv'

Make sure the parcellation files are in the nibabel format
"""
matrix_filename = '/PATH_TO_YOUR_MATRIX_FILE/27nodeMatrix.csv'
centre_filename = '/PATH_TO_YOUR_CENTRE_COORDINATE_FILE/27nodeCentres.csv'
centres_abbreviation = '/PATH_TO_THE_ABBREVIATION_OF_THE_DATASET/regions_199.txt'
template_filename = '/PATH_TO_YOUR_TEMPLATE_FILE/ch2better.nii.gz'
parcelation_filename = '/PATH_TO_YOUR_PARCELATION_FILE/allROIs.nii.gz'

#set the flag data around here for convenience, if you want to switch on or off 
# the other windows
GraphWindowShowFlag = True
MainWindowShowFlag = True
ElectrodeWindowShowFlag = False
CorrelationTableShowFlag = True





