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
# @file message.py
#    Helper classes to efficiently query messages from a dataset.
# 
# @author Adrian Kriegel
# @date   Tue May 07 2024
# 

from enum import Enum

from pathlib import Path

import numpy as np

import pyvista as pv

from scipy.spatial.transform import Rotation


class MessageType(Enum):

    # 3D Point cloud.
    POINT_CLOUD = 'POINT_CLOUD'

    # Color image.
    IMAGE_COLOR = 'IMAGE_COLOR'

    # Registered Color image. Pixel coordinates align with the depth image at the same time stamp.
    IMAGE_COLOR_REG = 'IMAGE_COLOR_REG'

    # Single-channel depth image. Pixel values correspond to depth values in mm.
    IMAGE_DEPTH = 'IMAGE_DEPTH'

class Transform:

    def __init__(self, xyz, rpy=(0,0,0), rot=None):

        self.trans_ = np.array(xyz)
        
        if rot is not None:

            if not isinstance(rot, Rotation):
                raise TypeError('`rot` must be Rotation from scipy.spatial.transform.')

            if rpy is not None:
                raise Exception('Cannot use rpy and rot at the same time to construct Transform.')

            self.rot_ = rot
        else:
            self.rot_ = Rotation.from_euler('xyz', rpy, degrees=True)
        

    def apply(self, vec):

        return self.rot_.apply(vec) + self.trans_

    def matrix(self):

        mat = np.identity(4)

        mat[:3,:3] = self.rot_.as_matrix()
        mat[0:3,2] = self.trans_

        return mat

    def inv(self):
        rt = self.rot_.inv()

        return Transform(-rt.apply(self.trans_), rt)

class MessageMeta:
    '''
    Message metadata.
    This part of the message contains identifying information. 
    It does not contain the actual data, allowing for efficient queries.
    '''

    def __init__(self, data : dict):

        self.type_ : MessageType = MessageType[data['Type']]
        # self.bounds_ = load_bounds(data['Bounds'])
        self.time_ : int = data['Time']

        pose = data['Pose']

        self.pose_ = Transform([pose['X'], pose['Y'], pose['Z']], [pose['Roll'], pose['Pitch'], pose['Yaw']])

        self.file_path_ = Path(data['File'])
        self.file_path_str_ = data['File']

    def type(self) -> MessageType:
        '''
        Message type.
        '''
        return self.type_

    #def bounds(self) -> pv.Box:
        '''
        Bounding box of the associated data.
        Images are roughly projected onto the shelf. Instead of a [pinhole camera](https://en.wikipedia.org/wiki/Pinhole_camera), imagine a pinhole projector projecting the image onto the shelf. The resulting projection is the 3D plane representing the image, and therefore also the bounding box.
        '''
        #return self.bounds_

    def time(self) -> int:
        return self.time_

    def file_path(self) -> Path:
        return self.file_path_

    def file_path_str(self) -> str:
        return self.file_path_str_

    def pose(self):
        '''
        3d pose (x, y, z, roll, pitch, yaw) 
        Center of the bounding box for point clouds.
        Focal point (roughly the camera's position) for images.
        '''
        return self.pose_

def load_bounds(data : dict) -> pv.Box:

    min_corner = data['MinCorner']
    max_corner = data['MaxCorner']

    return pv.Box(
        bounds=(
            min_corner['X'],
            max_corner['X'],
            min_corner['Y'],
            max_corner['Y'],
            min_corner['Z'],
            max_corner['Z']
        )
    )