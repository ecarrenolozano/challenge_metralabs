#!/bin/env python

import json

import numpy as np

from PIL import ImageDraw

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QVBoxLayout, QAction, QSlider

from pyvistaqt import QtInteractor, MainWindow

import pyvista as pv
import pyvistaqt as pvqt

from metralabs.data import DataFolder, DataQuery, TimeRange
from metralabs.message import MessageMeta, MessageType
from metralabs.camera import Camera

class PickSlider(QSlider):
    '''
    QSlider that allows the user to pick an element from a list.
    '''
    def __init__(self, elements):

        QSlider.__init__(self, Qt.Horizontal)
        self.setMinimum(0)
        self.setMaximum(len(elements) - 1)
        self.setValue(0)
        self.setTickPosition(QSlider.TicksBelow)
        self.setTickInterval(1)

        self.elements_ = elements

    def get_element(self):
        '''
        Returns the current element picked by the slider.
        '''

        return self.elements_[self.value()]

class MessageVisualization:

    def __init__(self, plotter, meta : MessageMeta, data_folder : DataFolder):
        
        self.plotter_ = plotter
        self.meta_ = meta
        self.data_folder_ = data_folder

        self.actors_ = [self.plotter_.add_mesh(**kwargs) for kwargs in self.create_polydata()]

    def create_polydata(self):
        return []

    def __del__(self):
        for actor in self.actors_:
            self.plotter_.remove_actor(actor)

class ImageVisualization(MessageVisualization):

    def __init__(self, plotter, meta : MessageMeta, data_folder : DataFolder, label):

        self.boxes_ = [] if label is None else label['boxes']

        MessageVisualization.__init__(self, plotter, meta, data_folder)


    def create_polydata(self):

        image = self.data_folder_.load_image(self.meta_.file_path())

        draw = ImageDraw.Draw(image)

        for box in self.boxes_:
            draw.rectangle(box, width=7, outline='red', fill=None)

        texture = pv.numpy_to_texture(np.array(image))

        pose = self.meta_.pose()
        
        # project the image onto the shelf
        # the y coordinate of the camera position is the distance from the shelf
        dist = pose.trans_[1] + 0.1

        camera = Camera(self.meta_)

        texture_coordinates = [
            (0,0), (1,1), (1,0), (0,1),
        ]

        points = [
            camera.get_world_position(x,y, dist) for x,y in texture_coordinates
        ]

        plane = pv.PolyData(points, faces=[4,0,2,1,3])

        plane.active_texture_coordinates = np.array([(u, 1.0 - v) for u,v in texture_coordinates])

        yield dict(
            mesh=plane,
            texture=texture,
            opacity=0.85
        )



class PointCloudVisualization(MessageVisualization):

    def create_polydata(self):

        pc = self.data_folder_.load_pcd(self.meta_.file_path())

        yield dict(
            mesh=pc,
            point_size=1,
            render_points_as_spheres=True
        )

class PlotWindow(MainWindow):

    def __init__(self, data : DataFolder):
        super().__init__()

        self.data_ = data

        self.labels_ = [json.load(open(label_path, 'rb')) for label_path in data.path_.glob('**/*_label.json')]

        self.visualizers_ = []

        self.setWindowTitle("Shelf Scanning Inspector")
        self.resize(1200, 900)
        
        # create the frame
        self.frame_ = QFrame()
        layout = QVBoxLayout()

        # add the pyvista interactor object
        self.plotter_ = QtInteractor(self.frame_)
        
        layout.addWidget(self.plotter_.interactor)
        self.signal_close.connect(self.plotter_.close)

        self.frame_.setLayout(layout)
        self.setCentralWidget(self.frame_)

        # time slider 
        self.slider_ = PickSlider(self.data_.meta_)
        self.slider_.setTracking(False)

        self.slider_.valueChanged.connect(self.on_slider_changed)

        # time range of messages to display left and right of the slider value
        self.time_range_ = int(4 * 1e9)

        layout.addWidget(self.slider_)

        self.update_query()

    def on_slider_changed(self):
        self.update_query()

    def get_visualizer(self, meta : MessageMeta):
        '''
        Returns the active visualizer for the metadata.
        Returns None if the data is currently not being visualized.
        '''
        gen = (vis for vis in self.visualizers_ if vis.meta_ == meta)
        return next(gen, None)

    def create_visualizer(self, meta : MessageMeta):

        if meta.type() == MessageType.POINT_CLOUD:
            return PointCloudVisualization(self.plotter_, meta, self.data_)
        else:
            label = next((label for label in self.labels_ if label['file'] == meta.file_path_str()), None)

            return ImageVisualization(self.plotter_, meta, self.data_, label)

    def update_query(self):

        picked_element : MessageMeta = self.slider_.get_element()

        self.query_ = TimeRange(picked_element.time() - self.time_range_//2, picked_element.time() + self.time_range_//2)
        
        self.update_messages()

    def update_messages(self):

        result = self.query_.run(self.data_.meta_)
        
        visualizers = []

        for meta in result:
            
            vis = self.get_visualizer(meta)
            
            visualizers.append(vis if vis is not None else self.create_visualizer(meta))

        self.visualizers_ = visualizers



if __name__ == '__main__':

    import sys

    import signal

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)

    window = PlotWindow(
        data = DataFolder(sys.argv[1])
    )

    window.show()

    app.exec()

