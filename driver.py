import numpy as np

import constants

class Driver(object):
    def __init__(self,
                 view_distance=100,
                 view_resolution=(5,5),
                 view_angle=90):
        self.view_distance = view_distance
        self.view_resolution = view_resolution
        self.view_angle = view_angle
        self.init_view()

    def init_view(self):
        self.view_distances = np.linspace(constants.MIN_VIEW_DISTANCE,
                                          self.view_distance,
                                          self.view_resolution[1])
        self.view_angles = np.linspace(-self.view_angle/2.,
                                       self.view_angle/2.,
                                       self.view_resolution[0]) * np.pi/180.
        self.view_matrix = np.zeros(self.view_resolution)

    def look(self, location, direction, track):
        cos_angles = np.cos(direction + self.view_angles)
        sin_angles = np.sin(direction + self.view_angles)
        x_matrix = location[0] + int(np.dot(cos_angles, self.view_distances))
        y_matrix = location[1] - int(np.dot(sin_angles, self.view_distances))
        self.view_matrix = track.off_track(x_matrix, y_matrix)
        