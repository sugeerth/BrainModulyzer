# README #

This README would normally document whatever steps are necessary to get your application up and running.
Our new version of the prototype requires: 

### Required dependencies ###

    PySide
      \-QtCore (BrainViewer)
      \-QtGui (BrainViewer)
    networkx (BrainViewer)
    nibabel (BrainViewer)
    numpy (BrainViewer)
    pygraphviz (BrainViewer)
    communtiy (BrainViewer)
    Visit (BrainViewer)
################################
Install the "python louvain Community" package by downloading the following package : https://bitbucket.org/taynaud/python-louvain/overview  
then installing it using the system python/visit python. 

python setup.py install (For system python)
 
You can also check if the installation was successful by : 

################
import community

in the interactive python that visit uses. 

### Installation Procedure ###
 Install all the packages using pip install <package-name> --user --upgrade (So that all packages bind with the visit python) 
 
 For Mac, you can install the packages through source or pip . 
 
 Also, for running the application in your local desktop,you need to specify the PYTHONPATH to the directory where this application is downloaded, the below given script takes care of this. 
 You can run the script in without worrying about changing pythonpath everytime: 
 
Type "python" in the terminal to launch interactive python and copy paste(after editing) the below given commands   
 
import os,sys

os.environ["PYTHONPATH"] = "/<edit your path directory here>/brain-vis"

os.system("~/<edit the path to visit binary>/visit2.7.3/src/bin/visit -cli -uifile /<edit your path directory here>/brain-vis/BrainViewer.py")

You can also copy the above commands to another python file and launch the application by running "python <script_name>.py" 

For letting the application know about the datafiles, create a file called BrainViewerDataPaths.py, editing the path of your data files to 
the following variables


#### Major Files ####
Major files BrainViewerDataPaths.py 
***********************************************************************
matrix_filename = /<edit your path to these files>/27nodeMatrix.csv \n

template_filename = /<edit your path to these files>/ch2better.nii.gz \n 

parcelation_filename = /<edit your path to these files>/allROIs.nii.gz \n 
************************************************************************
