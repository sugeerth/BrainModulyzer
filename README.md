# Interactive Visual Analysis of Functional Brain Connectivity #


Please click to watch the overview video.

[![ScreenShot](http://s32.postimg.org/mqw3ainkl/Architecture_Diag_Page_1.jpg)](https://vimeo.com/165523412)

# Brain Modulyzer #
We present *Brain Modulyzer*, an interactive visual exploration tool for functional magnetic resonance imaging (fMRI) brain scans, aimed at analyzing the correlation between different brain regions when resting or when performing mental tasks. Brain Modulyzer combines multiple coordinated views---such as heat maps, node link diagrams and anatomical views---using brushing and linking to provide an anatomical context for brain connectivity data. Integrating methods from graph theory and analysis, e.g., community detection and derived graph measures, makes it possible to explore the modular and hierarchical organization of functional brain networks. Providing immediate feedback by displaying analysis results instantaneously while changing parameters gives neuroscientists a powerful means to comprehend complex brain structure more effectively and efficiently and supports forming hypotheses that can then be validated via statistical analysis.

The following image shows the results of community detection with respect to anatomy. Each community is represented by a distinct color, and each region is colored according to its community
membership. Parcellated brain regions can be shown as outlines in Fig. A or
centroid depiction via a sphere Fig. C.

![ScreenShot](http://s32.postimg.org/blbh7yllh/Anatomical_Diagram_Page_1.jpg)

### Required dependencies ###
 
    Visit (Based on your distribution build visit from this build scirpt--- )
    PySide 
    networkx 
    nibabel  
    numpy 
    pygraphviz   
    communtiy
    
################################


################################
 

### Installation Procedure ###
look at the INSTALL_SCRIPT_NOTES

#### Major Files ####
BrainViewerDataPaths.py -- path for the dataset

RunMainProject.py -- path for running the applications with visit python backend
################################

In the following figure, A) the community graph highlights the subcommunities associated with the community selected in the dendrogram view. B) Configuration options provide various choices for interactivity, such as toggling hovering/clicking, choosing graph layout and varying the opacity of highlighted nodes. C) The brain region graph displays highlighted nodes associated with selected sub communities.
D) The dendrogram view displays the hierarchy of communities. The communities that do that not have any edges emanating from them are grayed out. E) A table view
lists important graph properties of the graph shown in Fig. C.
[![ScreenShot](http://s32.postimg.org/7zro1qnrp/Visual_Tool_Page_1.jpg)]()

![ScreenShot](http://s32.postimg.org/f3a3uyms5/Teaser_CGraph_View_Page_1.jpg)
