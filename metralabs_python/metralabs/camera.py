
import numpy as np

from metralabs.data import MessageMeta, MessageType

class Camera:
    '''
    Utility class for camera transformations.
    '''

    def __init__(self, meta : MessageMeta):
        
        self.meta_ = meta

        if meta.type in [MessageType.IMAGE_DEPTH, MessageType.IMAGE_COLOR_REG]:
            self.fx_ = 0.510
            self.fy_ = 0.906
            self.cx_ = 0.500
            self.cy_ = 0.499
        else:
            self.fx_ = 0.711
            self.fy_ = 1.264
            self.cx_ = 0.504
            self.cy_ = 0.522

    def get_position(self, x, y, dist) -> np.typing.ArrayLike:
        '''
        Get the 3D position of a point in the image at the specified distance within the camera's coordinate frame.
        
        :param x:       Image coordinate [0, 1]
        :param y:       Image coordinate [0, 1]
        :param dist:    Distance in [m]
        '''

        x_cam = (x - self.cx_) * dist / self.fx_
        y_cam = (y - self.cy_) * dist / self.fy_
        z_cam = dist

        return np.array([x_cam, y_cam, z_cam])

    def get_world_position(self, x, y, dist) -> np.typing.ArrayLike:
        '''
        Get the world position of a point in the image at the specified distance.

        :param x:       Image coordinate [0, 1]
        :param y:       Image coordinate [0, 1]
        :param dist:    Distance in [m]
        '''

        return self.meta_.pose().apply(self.get_position(x, y, dist))

    def get_world_normal(self):
        '''
        Normal vector of the image plane (where the camera is pointing) in world coordinates. 
        '''

        return self.meta_.pose().rot_.apply([0,0,1])
    
    def get_world_center(self, dist):
        '''
        Center of the image plane in world coordinates.
        '''
        p1,p2 = self.get_world_extent(dist)

        return 0.5 * (p1 + p2)

    def get_world_extent(self, dist):
        '''
        Returns (min_corner, max_corner) of the image plane at the specified distance.
        '''
        return self.get_world_position(0, 0, dist), self.get_world_position(1, 1, dist)
