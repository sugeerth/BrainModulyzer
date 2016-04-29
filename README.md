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
################################
Install the "python louvain Community" package by downloading the following package : https://bitbucket.org/taynaud/python-louvain/overview . and then installing it using the system python/visit python. 

python setup.py install (For system python)
 
You can also check if the installation was successful by : 

################
import community

in the interactive python that visit uses. 


The older version of the prototype requires: 
### Required dependencies ###

    PySide
      \-QtCore (BrainViewer)
      \-QtGui (BrainViewer)
    matplotlib (BrainViewer)
      \-backends
      | \-backend_qt4agg
      |   \-FigureCanvasQTAgg (BrainViewer)
      \-pyplot (BrainViewer)
    networkx (BrainViewer)
    nibabel (BrainViewer)
    numpy (BrainViewer)
    pylab (BrainViewer)
    sci-py (BrainViewer)
    pygraphviz (BrainViewer)
    
##############################

 Install all the packages using pip install <package-name> if you use linux, the backend for matplotlib is Qt4Agg with rcParameters as PySide. 
 
 For Mac, you can install the above mentioned packages using macports. 
 
 Also, for running the application in your local desktop,you need to specify the PYTHONPATH to the directory where this application is downloaded, the below given script takes care of this. 
 You can run the script in without worrying about changing pythonpath everytime: 
 
Type "python" in the terminal to launch interactive python and copy paste(after editing) the below given commands   
 
import os,sys

os.environ["PYTHONPATH"] = "/<edit your path directory here>/brain-vis"

os.system("~/<edit the path to visit binary>/visit2.7.3/src/bin/visit -cli -uifile /<edit your path directory here>/brain-vis/BrainViewer.py")

You can also copy the above commands to another python file and launch the application by running "python <script_name>.py" 

For letting the application know about the datafiles, create a file called BrainViewerDataPaths.py, editing the path of your data files to 
the following variables

[Example]

BrainViewerDataPaths.py 
***********************************************************************
matrix_filename = '/<edit your path to these files>/27nodeMatrix.csv'
template_filename = '/<edit your path to these files>/ch2better.nii.gz'
parcelation_filename = '/<edit your path to these files>/allROIs.nii.gz'
************************************************************************


## Modules in progress ## 
Slice-Viewer
Visit Viewer
Graph Viewer