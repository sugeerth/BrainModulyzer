# README #


### Required dependencies ###
 
    Visit (Based on your distribution build visit from this build scirpt--- )
        \- build script from here-- http://portal.nersc.gov/project/visit/releases/2.10.2/build_visit2_10_2
        \- and then run these commands---./build_visit2_10_2 --no-visit --silo —console
                                         ./build_visit2_10_2  --silo --console
    PySide--goto source and download-- https://pypi.python.org/pypi/PySide/1.2.4
        \- ~/<path to visit python directory>/python setup.py build
        \- ~/<path to visit python directory>/python setup.py install 
    or install using pip 
        \- pip install pyside --user --upgrade 
    networkx 
        \- pip install networkx --user --upgrade   
    nibabel -- pip install nibabel --user --upgrade 
    numpy -- pip install numpy --user --upgrade 
    pygraphviz  pip install pygraphviz --user --upgrade 
    communtiy -- pip install community --user --upgrade 
    
################################


################
 

### Installation Procedure ###
    Install the "python louvain Community" package by downloading the following package : https://bitbucket.org/taynaud/python-louvain/overview  
    then installing it using the system python/visit python. 
    
    python setup.py install (For system python)

 Install all the packages using pip install <package-name> --user --upgrade (So that all packages bind with the visit python) 
 
 For Mac, you can install the packages through source or pip REFERENCING your visit python. 
 
 Also, for running the application in your local desktop,you need to specify the 
 PYTHONPATH to the directory where this application is downloaded, the below 
  script RunMainProject.py takes care of this. You can run the script in without 
 worrying about changing pythonpath everytime: 

#### Major Files ####
BrainViewerDataPaths.py -- locations of your data is stored
RunMainProject.py -- a way to run the application with visit python backend
