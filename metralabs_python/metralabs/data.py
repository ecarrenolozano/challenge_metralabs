#
# Copyright (C) by
#   MetraLabs GmbH (MLAB), GERMANY
# All rights reserved.
# 
# Redistribution and modification of this code is strictly prohibited.
# 
# IN NO EVENT SHALL "MLAB" BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,
# SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE
# OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF "MLAB" HS BEEN
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# "MLAB" SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER IS ON AN
# "AS IS" BASIS, AND "MLAB" HAS NO OBLIGATION TO PROVIDE MAINTENANCE,
# SUPPORT, UPDATES, ENHANCEMENTS OR MODIFICATIONS.
# 

#
# @file data.py
#    Data handling utilities.
# 
# @author Adrian Kriegel
# @date   Tue May 07 2024
# 

import os

import json

from pathlib import Path

from typing import Iterator

import numpy as np

import open3d as o3d

from PIL import Image

import pyvista as pv

from metralabs.message import MessageMeta, MessageType

class DataFolder:

    def __init__(self, path):

        self.path_ = Path(os.path.expanduser(path))

        if not self.path_.exists():
            raise OSError(f'Specified data directory not found: {self.path_.absolute()}')
        
        self.meta_paths_ = self.path_.glob('**/*_meta.json')

        self.meta_ = sorted(
            (MessageMeta(json.load(open(meta_file))) for meta_file in self.meta_paths_),
            key=lambda meta: meta.time()
        )

    def __iter__(self):

        return self.meta_.__iter__()

    def __len__(self):

        return len(self.meta_)

    def get_start_time(self):

        return self.meta_[0].time_ if len(self.meta_) > 0 else -1
    
    def get_end_time(self):

        return self.meta_[-1].time_ if len(self.meta_) > 0 else -1


    def load_data(self, meta : MessageMeta):
        '''
        Returns load_image(...) or load_pcl(...) dpending on message type.
        '''
        msg_type = meta.type()

        if msg_type == MessageType.POINT_CLOUD:
            return self.load_pcd(meta.file_path())
        elif msg_type.startswith('IMAGE'):
            return self.load_image(meta.file_path())
        else:
            raise Exception('Unsupported message type: ' + msg_type)

    def resolve(self, path) -> Path:
        '''
        Resolve file relative to the data directory.
        '''
        return self.path_.joinpath(path)

    def load_image(self, file_path):
        '''
        Load image file.
        '''
        return Image.open(self.resolve(file_path).__str__())

    def load_pcd(self, file_path) -> pv.PolyData:
        '''
        Load .pcd file relative to data directory as pv.PolyData.

        See https://docs.pyvista.org/version/stable/api/core/_autosummary/pyvista.PolyData.html
        '''
        
        pc = o3d.io.read_point_cloud(self.resolve(file_path).__str__())

        return pv.PolyData(np.asarray(pc.points))

class DataQuery:

    def matches(self, meta : MessageMeta) -> bool:
        '''
        Override to generate custom queries.
        '''
        return True

    def run(self, meta : Iterator[MessageMeta]) -> Iterator[MessageMeta]:
        return (m for m in meta if self.matches(m))

class TimeRange(DataQuery):
    
    def __init__(self, start : int, end : int):
        self.start_ = start
        self.end_ = end

    def matches(self, meta : MessageMeta):
        
        return self.start_ <= meta.time_ <= self.end_