import pygame
import numpy as np

import constants

class Track():
    def __init__(self):
        self.load_track()
        self.rect = self.image.get_rect()

    def load_track(self):
        """
        Load the track image and its mask file.
        """
        track_image = pygame.image.load(constants.TRACK_FILE).convert()
        self.image = pygame.Surface((constants.WIDTH_TRACK, constants.HEIGHT_TRACK))
        self.image.blit(track_image, (0, 0))

        self.track_mask = pygame.image.load(constants.TRACK_MASK_FILE).convert()

    def draw(self, screen):
        screen.blit(self.image, (0, 0))

    def off_track(self, point):
        """
        Check if the coordinate point (x,y) is off track.
        """
        return self.track_mask.get_at(point) == constants.COLOR_OFF_TRACK

    def find_start(self, num_cars):
        """
        Finds the starting coordinates and orientation for cars.
        """
        reds = pygame.surfarray.pixels_red(self.track_mask)
        markers = np.where(reds == constants.COLOR_FINISH[0])
        startpos = np.empty((2, num_cars))
        for ii in range(2):
            marker_space = np.linspace(markers[ii][0], markers[ii][-1], num_cars+1)
            startpos[ii,:] = (marker_space[:-1] + marker_space[1:]) / 2.
        startpos_list = [(startpos[0,ii], startpos[1,ii]) for ii in range(num_cars)]

        normal = [markers[1][-1]-markers[1][0], markers[0][0]-markers[0][-1]]
        start_direction = np.arctan(-normal[1] / normal[0])

        return startpos_list, start_direction
