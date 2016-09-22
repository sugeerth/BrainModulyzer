# Interactive Visual Analysis of Functional Brain Connectivity #

Wiki: https://github.com/sugeerth/BrainModulyzer/wiki

Please click to watch the overview video.

[![ScreenShot](http://s32.postimg.org/mqw3ainkl/Architecture_Diag_Page_1.jpg)](https://vimeo.com/165523412)

# Brain Modulyzer #
We present *Brain Modulyzer*, an interactive visual exploration tool for functional magnetic resonance imaging (fMRI) brain scans, aimed at analyzing the correlation between different brain regions when resting or when performing mental tasks. Brain Modulyzer combines multiple coordinated views---such as heat maps, node link diagrams and anatomical views---using brushing and linking to provide an anatomical context for brain connectivity data. Integrating methods from graph theory and analysis, e.g., community detection and derived graph measures, makes it possible to explore the modular and hierarchical organization of functional brain networks. Providing immediate feedback by displaying analysis results instantaneously while changing parameters gives neuroscientists a powerful means to comprehend complex brain structure more effectively and efficiently and supports forming hypotheses that can then be validated via statistical analysis.

<!--The following image shows the results of community detection with respect to anatomy. Each community is represented by a distinct color, and each region is colored according to its community-->
<!--membership. Parcellated brain regions can be shown as outlines in Fig. A or-->
<!--centroid depiction via a sphere Fig. C.-->

<!--![ScreenShot](http://s32.postimg.org/blbh7yllh/Anatomical_Diagram_Page_1.jpg)-->

### Required Dependencies ###
    numpy
    networkx
    nibabel
    pydot
    community
    pygraphviz
    vtk
    PySide
    decorator


### Getting Started  ###
Note: Tested on OS X 10.11.6 and Ubuntu 14.04

	# Conda installation, if you dont have conda, then install via (http://conda.pydata.org/docs/install/quick.html)
	conda install python=2.7
	conda install anaconda-client
	conda config --add channels anaconda
	conda config --add channels pdrops  
	conda config --add channels allank
	conda config --add channels asmeurer 
	conda config --add channels menpo
	conda config --add channels conda-forge
	
	conda install -c sugeerth brainm=1.0.1
	
	#Download Brain Modulyzer repository and then goto src folder 
	
	modulyzerdir/src> RunProjectMain.py 
		
	
Happy Analysis! 

####Major Files
**BrainViewerDataPaths.py** -- path for the dataset
**RunMainProject.py** -- path for running the application

##Running the Tool 
        modulyzerdir> export PYTHONPATH=${PYTHONPATH}:modulyzerdir
        modulyzerdir> python RunMainProject.py

In the following figure, 

        A) the community graph highlights the subcommunities associated with the community selected in the dendrogram view.
        B) Configuration options provide various choices for interactivity, such as toggling hovering/clicking, choosing graph layout and varying the opacity of highlighted nodes. 
        C) The brain region graph displays highlighted nodes associated with selected sub communities.
        D) The dendrogram view displays the hierarchy of communities. The communities that do that not have any edges emanating from them are grayed out.
        E) A table view lists important graph properties of the graph shown in Fig. C.

[![ScreenShot](http://s32.postimg.org/7zro1qnrp/Visual_Tool_Page_1.jpg)]()


### Citation Information###
@ARTICLE{7466855, 

author={S. Murugesan and K. Bouchard and J. A. Brown and B. Hamann and W. W. Seeley and A. Trujillo and G. H. Weber}, 

journal={IEEE/ACM Transactions on Computational Biology and Bioinformatics}, 

title={Brain Modulyzer: Interactive Visual Analysis of Functional Brain Connectivity}, 

year={2016}, 

volume={PP}, 

number={99}, 

pages={1-1}, 

doi={10.1109/TCBB.2016.2564970}, 

ISSN={1545-5963}, 

}

### License Information ###

Brain Modulyzer Copyright (c) 2016, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All rights reserved.
 
If you have questions about your rights to use or distribute this software, please contact Berkeley Lab's Innovation and Partnerships department at IPO@lbl.gov referring to " Brain Modulyzer (2016-149),."
 
NOTICE.  This software was developed under funding from the U.S. Department of Energy.  As such, the U.S. Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, prepare derivative works, and perform publicly and display publicly.  Beginning five (5) years after the date permission to assert copyright is obtained from the U.S. Department of Energy, and subject to any subsequent five (5) year renewals, the U.S. Government is granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, prepare derivative works, distribute copies to the public, perform publicly and display publicly, and to permit others to do so.
<!--![ScreenShot](http://s32.postimg.org/f3a3uyms5/Teaser_CGraph_View_Page_1.jpg)-->
