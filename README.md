# README #
We present Brain Modulyzer, an interactive visual exploration tool for functional magnetic resonance imaging (fMRI) brain scans, aimed at analyzing the correlation between different brain regions when resting or when performing mental tasks. Brain Modulyzer combines multiple coordinated views---such as heat maps, node link diagrams and anatomical views---using brushing and linking to provide an anatomical context for brain connectivity data. Integrating methods from graph theory and analysis, e.g., community detection and derived graph measures, makes it possible to explore the modular and hierarchical organization of functional brain networks. Providing immediate feedback by displaying analysis results instantaneously while changing parameters gives neuroscientists a powerful means to comprehend complex brain structure more effectively and efficiently and supports forming hypotheses that can then be validated via statistical analysis. To demonstrate the utility of our tool, we present two case studies---exploring progressive supranuclear palsy, as well as memory encoding and retrieval.

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
