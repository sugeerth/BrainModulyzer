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
		
		
For Non-conda users you can install the libraries manually 

	#For mac switch to macports python for installation (as installation libraries are in macports):
	sudo port install python27
	port select --list python
	sudo port select --set python python27
		
	#For mac set the pip for macports: 
	sudo port install py27-pip
	sudo port select --list pip 
	sudo port select --set pip pip27

	sudo pip install numpy==1.11.0
	sudo pip install networkx==1.11
	sudo pip install nibabel==2.0.2
	sudo pip install pydotplus
	sudo pip install python-louvain
	
	To install Graphviz:
		**Install latest Graphviz** version through the graphviz website--(http://www.graphviz.org/Download_macos.php)
		
		for linux
			sudo apt-get install graphviz
			sudo pip install pygraphviz==1.3.1 --install-option="--include-path=/usr/include/graphviz" --install-option="--library-path=/usr/lib/graphviz/"
		for mac
			sudo pip install pygraphviz==1.3.1
	
	To install QT:
		for linux
			sudo apt-get install libqt4-dev
			sudo easy_install -U PySide
		for mac
			sudo port install qt4-mac
			sudo port install py27-pyside
	
	To install VTK (vtk version > 5):
		for linux
			#This is a bit tricky, follow this step by step, in the future this will become easier
			#Download from source VTK-7.0.0
			[VTK7](http://www.vtk.org/files/release/7.0/VTK-7.0.0.zip)
			unzip VTK-7.0.0.zip
			cd VTK-7.0.0
			mkdir Build
			cd Build 
			ccmake .. (in GUI turn two flags BUILD_SHARED_LIBS ON and PYTHON_WRAPPING, press 'c' twice and when the config completes press 'g')
			make -j 8
			sudo make install
			#Now all you have to do add paths in PYTHONPATHS
			export PYTHONPATH=/PATH_TO_VTK-7.0.0/Build/lib/
			export PYTHONPATH=$PYTHONPATH:/PATH_TO_VTK-7.0.0/Build/Wrapping/Python/
		for mac
			#port			
			sudo port install vtk

####Major Files
In case any of the pre-existing library installation does not work, please download and install the affected libraries from source:

	[Numpy](https://sourceforge.net/projects/numpy/files/NumPy/1.11.0/numpy-1.11.0.tar.gz/download )
	[Networkx](https://pypi.python.org/packages/c2/93/dbb41b03cf7c878a7409c8e92226531f840a423c9309ea534873a83c9192/networkx-1.11.tar.gz#md5=6ef584a879e9163013e9a762e1cf7cd1 )
	[Nibabel](http://nipy.org/nibabel/installation.html#installation ) 
	[Louvain](https://pypi.python.org/packages/5d/81/497a95ba9d79d5bf04f9318256d1c0102329dd6a77b9d1e4dd84871e1089/python-louvain-0.5.tar.gz )
	[PyDot](https://pypi.python.org/pypi/pydot3/1.0.8 )
	[PySide](https://pypi.python.org/pypi/PySide/1.2.4)
	[PyGraphViz](https://pypi.python.org/packages/98/bb/a32e33f7665b921c926209305dde66fe41003a4ad934b10efb7c1211a419/pygraphviz-1.3.1.tar.gz#md5=7f690295dfe77edaa9e552d09d98d279 )
	
	Note: If after installing, "import pygraphviz" returns an error, then uninstall and reinstall using: 	
	pip install pygraphviz --install-option="--include-path=/usr/local/include/graphviz" --install-option="--library-path=/usr/local/lib/graphviz/" (https://github.com/pygraphviz/pygraphviz/issues/72)

	[VTK and PyVTK](http://www.it.uu.se/edu/course/homepage/vetvis/ht10/vtk/instructions_vtk_OSX.pdf) 
	
Happy Analysis! 

####Major Files
**BrainViewerDataPaths.py** -- path for the dataset
**RunMainProject.py** -- path for running the application

##Running the Tool 
        modulyzerdir/src> RunMainProject.py

In the following figure, 

        A) the community graph highlights the subcommunities associated with the community selected in the dendrogram view.
        B) Configuration options provide various choices for interactivity, such as toggling hovering/clicking, choosing graph layout and varying the opacity of highlighted nodes. 
        C) The brain region graph displays highlighted nodes associated with selected sub communities.
        D) The dendrogram view displays the hierarchy of communities. The communities that do that not have any edges emanating from them are grayed out.
        E) A table view lists important graph properties of the graph shown in Fig. C.

[![ScreenShot](http://s32.postimg.org/7zro1qnrp/Visual_Tool_Page_1.jpg)]()

Contributing
------------

See [Contributing](CONTRIBUTING.md)

### Citation Information###
Please cite Brain Modulyzer in your publications if it helps your research:

    @article{muru2016modulyzer,
      Author = {S. Murugesan and K. Bouchard and J. A. Brown and B. Hamann and W. W. Seeley and A. Trujillo and G. H. Weber},
      Journal = {IEEE/ACM transactions on computational biology and bioinformatics/IEEE, ACM},
      Title = {Brain Modulyzer: Interactive Visual Analysis of Functional Brain Connectivity},
      Year = {2016},
      doi={10.1109/TCBB.2016.2564970}, 
    }

### License Information ###

Brain Modulyzer is released under the [BSD license](https://github.com/sugeerth/BrainModulyzer/blob/master/LICENSE).

Brain Modulyzer Copyright (c) 2016, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All rights reserved.
 
If you have questions about your rights to use or distribute this software, please contact Berkeley Lab's Innovation and Partnerships department at IPO@lbl.gov referring to " Brain Modulyzer (2016-149),."
 
NOTICE.  This software was developed under funding from the U.S. Department of Energy.  As such, the U.S. Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, prepare derivative works, and perform publicly and display publicly.  Beginning five (5) years after the date permission to assert copyright is obtained from the U.S. Department of Energy, and subject to any subsequent five (5) year renewals, the U.S. Government is granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the Software to reproduce, prepare derivative works, distribute copies to the public, perform publicly and display publicly, and to permit others to do so.
<!--![ScreenShot](http://s32.postimg.org/f3a3uyms5/Teaser_CGraph_View_Page_1.jpg)-->
