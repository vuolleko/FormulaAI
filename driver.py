import numpy as np
import pygame

import constants

class Driver(object):
    def __init__(self,
                 view_distance=100,
                 view_resolution=(5,5),
                 view_angle=90):
        self.view_distance = view_distance
        self.view_resolution = view_resolution
        self.view_angle = view_angle
        self.draw_visual = True
        self.init_view()

    def init_view(self):
        self.view_distances = np.linspace(constants.MIN_VIEW_DISTANCE,
                                          self.view_distance,
                                          self.view_resolution[1])
        self.view_angles = np.linspace(-self.view_angle/2.,
                                       self.view_angle/2.,
                                       self.view_resolution[0]) * np.pi/180.
        self.view_matrix = np.zeros(self.view_resolution)

    def look(self, location, direction, track, screen):
        cos_angles = np.cos(direction + self.view_angles)
        x_matrix = location[0] + np.outer(cos_angles, self.view_distances)
        x_matrix = np.where((x_matrix < 0) | (x_matrix >= constants.WIDTH_TRACK), 0., x_matrix)

        sin_angles = np.sin(direction + self.view_angles)
        y_matrix = location[1] - np.outer(sin_angles, self.view_distances)
        y_matrix = np.where((y_matrix < 0) | (y_matrix >= constants.HEIGHT_TRACK), 0., y_matrix)

        x_matrix = x_matrix.astype(int)
        y_matrix = y_matrix.astype(int)

        self.view_matrix = track.off_track(x_matrix, y_matrix)

        if self.draw_visual:
            for point in zip(x_matrix.flatten(), y_matrix.flatten()):
                pygame.draw.line(screen, constants.COLOR_VIEW_LINES, location, point)
