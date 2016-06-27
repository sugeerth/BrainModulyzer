import colorsys
import math
import numpy as np
from PySide import QtCore, QtGui
from color_table import *

def ColorToInt(color):
    r, g, b, a = map(np.uint32, color)
    return a << 24 | r << 16 | g << 8 | b

"""
Class that Implements the slice view in the anatomical view
"""
class SliceViewer(QtGui.QWidget):
    sliceChanged = QtCore.Signal(int)
    regionSelected = QtCore.Signal(int)

    def __init__(self, templateData, parcelationData, axis, correlationTable, colorTable, selectedColor):
        super(SliceViewer, self).__init__()

        self.template = templateData
        self.regionId = None
        self.parcelation = parcelationData
        self.axis = axis
        self.CommunityMode = False
        self.correlationTable = correlationTable
        self.colorTable= colorTable
        self.selectedColor = selectedColor
        self.CommunityMode = False
        self.displayedSlice = 0
        # FIX  with the scale factor it was 350 earlier 
        if len(self.correlationTable.data) > 100: 
            scalefactor = 350 
        else: 
            scalefactor = 350
        self.scaleFactor = int(math.ceil(scalefactor / self.parcelation.shape[0]))

        numColors = self.parcelation.max()
        self.clut = np.zeros(numColors, dtype=np.uint32)
        for i in range(numColors):
            r, g, b = colorsys.hls_to_rgb(float(i) / float(numColors), 0.5, 1.0)
            self.clut[i] = (255 << 24 | int(255*r) << 16 | int(255*g) << 8 | int(255*b))

        slice_view_layout = QtGui.QHBoxLayout()
        self.setLayout(slice_view_layout)

        slider = QtGui.QSlider()
        slider.setRange(0, self.template.shape[self.axis]-1)
        slider.valueChanged.connect(self.setDisplayedSlice)
        slider.sliderReleased.connect(self.handleSliderRelease)
        slider.setValue(self.displayedSlice)
        slice_view_layout.addWidget(slider)

        self.label = QtGui.QLabel()
        self.updateSliceLabel()
        slice_view_layout.addWidget(self.label)

    # """
    # wheel Events Changes   
    # """    
    # def wheelEvent(self, event):
    #     self.scaleView(math.pow(2.0, -event.delta() / 1040.0))
    # """
    # Scale things based on wheel events
    # """
    # def scaleView(self, scaleFactor):
    #     factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 5, 5)).width()
    #     if factor < 0.07 or factor > 100:
    #         return
    #     self.scale(scaleFactor, scaleFactor)
    #     del factor

    def extractSlice(self, volData):
        if self.axis == 0:
            return volData[self.displayedSlice, :, :]
        elif self.axis == 1:
            return volData[:, self.displayedSlice, :]
        elif self.axis == 2:
            return volData[:, :, self.displayedSlice]

    def updateSliceLabel(self):
        image_slice = self.extractSlice(self.template)
        image_data = (255 << 24 | image_slice << 16 | image_slice << 8 | image_slice)
        # print image_data
        parcelation_slice = self.extractSlice(self.parcelation)
        indices = np.flatnonzero(parcelation_slice)
        for idx in indices:
            image_data.flat[idx] = self.clut[parcelation_slice.flat[idx]-1]
        image_data = np.array(image_data[:, ::-1], order='F')
        image = QtGui.QImage(image_data, image_data.shape[0], image_data.shape[1], QtGui.QImage.Format_ARGB32)
        # if self.scaleFactor > 1:
        image = image.scaled(self.scaleFactor*image.width(), self.scaleFactor*image.height())
        self.label.setPixmap(QtGui.QPixmap.fromImage(image))

    def setDisplayedSlice(self, sliceNo):
        self.displayedSlice = sliceNo
        self.updateSliceLabel()

    def handleSliderRelease(self):
        # print "Getting invoked"
        self.sliceChanged.emit(self.displayedSlice)

    def colorRelativeToRegion(self, regionId):
        # print "receiving in slice views",self.sender() 

        if not(self.CommunityMode): 
        # start_time = time.time()
            for i in range(self.clut.shape[0]):
                if(i == len(self.correlationTable.data)):
                    return
                if i != regionId:
                    t = self.correlationTable.value(regionId, i)
                    self.clut[i] = ColorToInt(self.colorTable.getColor(t))
                else:
                    self.clut[i] = ColorToInt(self.selectedColor)
        self.updateSliceLabel()
        # print("SliceViewer CorrelationTable --- %f seconds ---" % (time.time() - start_time))

    def Community(self, Flag):
        self.CommunityMode = Flag
        # print self.CommunityMode, "in slice" 
        self.updateSliceLabel()
        if not(Flag):
            self.colorRelativeToRegion(0)

    def setRegionColors(self, colors):
        assert(len(colors) == self.clut.shape[0])
        # self.CommunityMode = True
        # print "I am getting called"

        for i in range(self.clut.shape[0]):
            self.clut[i] = ColorToInt(colors[i])
        self.updateSliceLabel()

    def mousePressEvent(self, event):

        pos = self.label.mapFromParent(event.pos())
        x, y = pos.x(), pos.y()
        
        if self.scaleFactor > 1:
            x /= self.scaleFactor
            y /= self.scaleFactor

        # Dont understand what this does
        parcelation_slice = self.extractSlice(self.parcelation)[:, ::-1]
        
        # Dont understand what this does
        if x < parcelation_slice.shape[0] and y < parcelation_slice.shape[1]:
            newId = parcelation_slice[x, y]

            if newId != 0:
                newId -= 1
                if self.CommunityMode:
                    self.regionId = newId
                    # self.colorRelativeToRegionCommunity(newId)
                else: 
                    self.colorRelativeToRegion(newId)
                # print "getting invoked"
                self.regionSelected.emit(newId)



