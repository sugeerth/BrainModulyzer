# Interactive Visual Analysis of Functional Brain Connectivity #


Please click to watch the overview video.

[![ScreenShot](http://s32.postimg.org/mqw3ainkl/Architecture_Diag_Page_1.jpg)](https://vimeo.com/165523412)

# Brain Modulyzer #
We present *Brain Modulyzer*, an interactive visual exploration tool for functional magnetic resonance imaging (fMRI) brain scans, aimed at analyzing the correlation between different brain regions when resting or when performing mental tasks. Brain Modulyzer combines multiple coordinated views---such as heat maps, node link diagrams and anatomical views---using brushing and linking to provide an anatomical context for brain connectivity data. Integrating methods from graph theory and analysis, e.g., community detection and derived graph measures, makes it possible to explore the modular and hierarchical organization of functional brain networks. Providing immediate feedback by displaying analysis results instantaneously while changing parameters gives neuroscientists a powerful means to comprehend complex brain structure more effectively and efficiently and supports forming hypotheses that can then be validated via statistical analysis.

The following image shows the results of community detection with respect to anatomy. Each community is represented by a distinct color, and each region is colored according to its community
membership. Parcellated brain regions can be shown as outlines in Fig. A or
centroid depiction via a sphere Fig. C.

<!--![ScreenShot](http://s32.postimg.org/blbh7yllh/Anatomical_Diagram_Page_1.jpg)-->

### Required dependencies ###
 
    PySide 
    networkx 
    nibabel  
    numpy 
    pygraphviz   
    communtiy
    PyVTK
    
################################


################################
 

### Installation Procedure ###

To install all the libraries for the python script to run


1) Install all the source files from the requirements folder in the same order

	pip install numpy==1.11.0

	pip install decorator>=3.4.0

	pip install networkx==1.11

	pip install nibabel==2.0.2

	pip install pydot3==1.0.8

	pip install python-louvain==0.4

	pip install pygraphviz==1.3.1

	pip install PyVTK==0.5.18


The links might have changed be aware of it

	[Numpy](https://sourceforge.net/projects/numpy/files/NumPy/1.11.0/numpy-1.11.0.tar.gz/download)`
	[Decorator](https://pypi.python.org/packages/68/04/621a0f896544814ce6c6a0e6bc01d19fc41d245d4515a2e4cf9e07a45a12/decorator-4.0.9.tar.gz#md5=f12c5651ccd707e12a0abaa4f76cd69a)
	[Networkx](https://pypi.python.org/packages/c2/93/dbb41b03cf7c878a7409c8e92226531f840a423c9309ea534873a83c9192/networkx-1.11.tar.gz#md5=6ef584a879e9163013e9a762e1cf7cd1)
	[Nibabel](http://nipy.org/nibabel/installation.html#installation) 
	[Louvain](https://pypi.python.org/packages/5d/81/497a95ba9d79d5bf04f9318256d1c0102329dd6a77b9d1e4dd84871e1089/python-louvain-0.5.tar.gz)
	[PyDot](https://pypi.python.org/pypi/pydot3/1.0.8)
	[PyGraphViz](https://pypi.python.org/packages/98/bb/a32e33f7665b921c926209305dde66fe41003a4ad934b10efb7c1211a419/pygraphviz-1.3.1.tar.gz#md5=7f690295dfe77edaa9e552d09d98d279)
	[VTK and PyVTK](http://kazenotaiyo.blogspot.com/2010/06/installing-vtk-in-ubuntu-and-making.html)

	and then, type python and paste these commands
		import numpy
		import networkx
		import nibabel
		import pydot3
		import python-louvain 
		import pygraphviz
		import vtk
	If none of them returns an error then you are set

2)	Configure the data paths in BrainViewerDataPaths.py 
	and configure paths to run BrainViewer.py   


Happy Analysis! 

#### Major Files ####
BrainViewerDataPaths.py -- path for the dataset

RunMainProject.py -- path for running the applications with visit python backend
################################

In the following figure, 

A) the community graph highlights the subcommunities associated with the community selected in the dendrogram view. 

B) Configuration options provide various choices for interactivity, such as toggling hovering/clicking, choosing graph layout and varying the opacity of highlighted nodes. 

C) The brain region graph displays highlighted nodes associated with selected sub communities.

D) The dendrogram view displays the hierarchy of communities. The communities that do that not have any edges emanating from them are grayed out.

E) A table view lists important graph properties of the graph shown in Fig. C.

[![ScreenShot](http://s32.postimg.org/7zro1qnrp/Visual_Tool_Page_1.jpg)]()


### Citation Infomration###
@ARTICLE{7466855, 
author={S. Murugesan and K. Bouchard and J. A. Brown and B. Hamann and W. W. Seeley and A. Trujillo and G. H. Weber}, 
journal={IEEE/ACM Transactions on Computational Biology and Bioinformatics}, 
title={Brain Modulyzer: Interactive Visual Analysis of Functional Brain Connectivity}, 
year={2016}, 
volume={PP}, 
number={99}, 
pages={1-1}, 
keywords={Correlation;Data visualization;Layout;Network topology;Organizations;Three-dimensional displays;Visualization;Brain Imaging;Functional Magnetic Resonance Imaging (fMRI);Graph Visualization;Linked Views;Neuroinformatics}, 
doi={10.1109/TCBB.2016.2564970}, 
ISSN={1545-5963}, 
month={},}

<!--![ScreenShot](http://s32.postimg.org/f3a3uyms5/Teaser_CGraph_View_Page_1.jpg)-->
