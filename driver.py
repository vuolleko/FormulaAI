import numpy as np
import pygame

import constants
import ann

class Driver(object):
    """
    This class implements the car's driver: visibility, controls etc.
    """
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
        self.view_x = np.empty(self.view_resolution)
        self.view_y = np.empty(self.view_resolution)
        self.view_field = np.zeros(self.view_resolution)

    def look(self, car, track):
        """
        Evaluate the driver's view ahead.
        """
        cos_angles = np.cos(car.direction + self.view_angles)
        self.view_x = (car.rect.center[0]
                       + np.outer(cos_angles, self.view_distances)
                      ).astype(int)

        sin_angles = np.sin(car.direction + self.view_angles)
        self.view_y = (car.rect.center[1]
                       - np.outer(sin_angles, self.view_distances)
                      ).astype(int)

        # limit coordinates within track area (only for checking if off track)
        x_matrix0 = np.where((self.view_x < 0) | 
                             (self.view_x >= constants.WIDTH_TRACK),
                             0, self.view_x)
        y_matrix0 = np.where((self.view_y < 0) |
                             (self.view_y >= constants.HEIGHT_TRACK),
                             0, self.view_y)

        self.view_field = track.off_track(x_matrix0, y_matrix0)

        # block the view behind corners etc.
        for ii in range(self.view_resolution[0]):
            lineview = self.view_field[ii,:]
            if np.any(lineview):
                lineview[np.argmax(lineview):] = 1

    def draw_viewfield(self, screen):
        """
        Draw the field of view.
        """
        for xx, yy, colind in zip(self.view_x.flatten(),
                                  self.view_y.flatten(),
                                  self.view_field.flatten()):
            pygame.draw.circle(screen, constants.COLOR_VIEWFIELD[colind], (xx, yy), 3)

    def update(self, *args):
        pass


class Player(Driver):
    """
    This class implements the driver for the player car.
    """
    def __init__(self,
                 view_distance=150,
                 view_resolution=(7,7),
                 view_angle=90):
        super(Player, self).__init__(view_distance, view_resolution, view_angle)

    def update(self, car):
        """
        Read keyboard for controlling the player car.
        """
        car.accelerate = False
        car.brake = False
        car.turn_left = False
        car.turn_right = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            car.accelerate = True
        if keys[pygame.K_DOWN]:
            car.brake = True
        if keys[pygame.K_LEFT]:
            car.turn_left = True
        if keys[pygame.K_RIGHT]:
            car.turn_right = True


class AI_ANN(Driver):
    """
    This class implements the AI driver for a neural network.
    """
    def __init__(self,
                 view_distance=150,
                 view_resolution=(7,7),
                 view_angle=90,
                 n_hidden_neurons=5,
                 model_car=None,
                 learning_rate=0.01,
                 regularization=1):
        super(AI_ANN, self).__init__(view_distance, view_resolution, view_angle)
        self.model_car = model_car  # the car to learn from
        self.learning_rate = learning_rate
        self.regularization = regularization

        n_inputs = self.view_resolution[0] * self.view_resolution[1] + 1  # viewpoints + speed
        n_outputs = 4  # accelerate, brake, left, right
        self.ann = ann.ANN((n_inputs, n_hidden_neurons, n_outputs))

    def update(self, own_car):
        own_car.accelerate = False
        own_car.brake = False
        own_car.turn_left = False
        own_car.turn_right = False        
        model_inputs = self.prepare_inputs(self.model_car)
        self.ann.train1(model_inputs, self.model_actions(),
                        self.learning_rate, self.regularization)

        inputs = self.prepare_inputs(own_car)
        outputs = self.ann.feedforward(inputs)
        self.process_output(outputs, own_car)

    def prepare_inputs(self, car):
        inputs = car.driver.view_field.flatten()
        speed_transform = np.exp(-car.speed)
        inputs = np.insert(inputs, 0, speed_transform, axis=0)
        return inputs

    def model_actions(self):
        return np.array([self.model_car.accelerate,
                         self.model_car.brake,
                         self.model_car.turn_left,
                         self.model_car.turn_right]).astype(float)

    def process_output(self, outputs, car):
        print outputs
        threshold = 0.6
        if outputs[0] > threshold:
            car.accelerate = True
        if outputs[1] > threshold:
            car.brake = True
        if outputs[2] > threshold:
            car.turn_left = True
        if outputs[3] > threshold:
            car.turn_right = True
