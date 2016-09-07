import os
import setuptools

def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

setuptools.setup(
	name="BrainModulyzer",
	version="0.0.0",
	maintainer="Sugeerth Murugesan",
	maintainer_email="smuru@ucdavis.edu",
	description=("A visualizer for brain networks"),
	license="BSD",
	packages=["brainmodulyzer"],
	package_data={'brainmodulyzer':['src/*']},
	scripts=['src/RunProjectMain.py'],
	url="https://github.com/sugeerth/BrainModulyzer",
	long_description=read('README'),
	classifiers=[
		"Development Status :: 4 - Beta",
		"Environment :: X11 Applications",
		"Intended Audience :: Science/Research",
		"Natural Language :: English",
		"Programming Language :: Python :: 2.7",
		"Topic :: Scientific/Engineering :: Visualization",
	],
	platforms=['any'],
	install_requires=["vtk","numpy","nibabel","networkx","pygraphviz","PySide","python-louvain"]
)