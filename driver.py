import numpy as np
import pygame

import constants
import ann


class Driver(object):
    """
    This class implements the car's driver: visibility, controls etc.
    """
    def __init__(self,
                 view_distance=constants.MAX_VIEW_DISTANCE,
                 view_resolution=constants.VIEW_RESOLUTION,
                 view_angle=constants.VIEW_ANGLE):
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

        self.view_field[:] = track.off_track(x_matrix0, y_matrix0)

        # block the view behind corners etc.
        if constants.BLOCK_VIEW:
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
            pygame.draw.circle(screen, constants.COLOR_VIEWFIELD[int(colind)], (xx, yy), 3)

    def update(self, car, *args):
        """
        Default actions for drivers.
        """
        car.accelerate = constants.ALWAYS_FULLGAS
        car.brake = False
        car.turn_left = False
        car.turn_right = False


class Player(Driver):
    """
    This class implements the driver for the player car.
    """
    def __init__(self, *args, **kwargs):
        super(Player, self).__init__(*args, **kwargs)

    def update(self, car):
        """
        Read keyboard for controlling the player car.
        """
        super(Player, self).update(car)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            car.accelerate = True
        if keys[pygame.K_DOWN]:
            car.brake = True
        if keys[pygame.K_LEFT]:
            car.turn_left = True
        if keys[pygame.K_RIGHT]:
            car.turn_right = True


class AI_TIF(Driver):
    """
    This class implements a simple AI driver that tries to keep most of 
    the track in front of its view field.
    """
    def __init__(self, *args, **kwargs):
        super(AI_TIF, self).__init__(*args, **kwargs)
        # speed that still (kind of) allows a 90 degree turn
        self.allowed_speed = constants.MAX_VIEW_DISTANCE / (
                             np.pi / (2. * constants.TURN_SPEED))

    def update(self, car):
        """
        The car turns depending on whether its closest side checks
        are off track. Brake is applied if the car is going too fast
        with wall in front, and especially if the corner is tight.
        """
        super(AI_TIF, self).update(car)
        car.accelerate = True
        if self.view_field[0,0] and not self.view_field[-1,0]:
            car.turn_left = True
        elif self.view_field[-1,0] and not self.view_field[0,0]:
            car.turn_right = True

        if self.view_field[self.view_resolution[0]/2, -1]:
            car.brake = car.speed > self.allowed_speed

            # special handling of tight corners
            if not all(self.view_field[[0,-1],-1]) and car.speed > 1.:
                car.brake = True



class ANN_Online(Driver):
    """
    This class implements the AI driver for a neural network.
    The network is trained online using stochastic gradient descent.
    """
    def __init__(self,
                 n_hidden_neurons=5,
                 model_car=None,
                 learning_rate=0.2,
                 regularization=1.,
                 *args, **kwargs):
        super(ANN_Online, self).__init__(*args, **kwargs)
        self.model_car = model_car  # the car to learn from
        self.learning_rate = learning_rate
        self.regularization = regularization

        n_inputs = self.view_resolution[0] * self.view_resolution[1] + 1  # viewpoints + speed
        n_outputs = 4  # accelerate, brake, left, right
        self.ann = ann.ANN(n_inputs, n_hidden_neurons, n_outputs)

    def update(self, own_car):
        super(ANN_Online, self).update(own_car)

        self.learn()
        inputs = self.prepare_inputs(own_car)
        outputs = self.ann.feedforward(inputs)
        self.process_output(outputs, own_car)

    def learn(self):
        model_inputs = self.prepare_inputs(self.model_car)
        self.ann.train1(model_inputs, self.model_actions(),
                        self.learning_rate, self.regularization)

    def prepare_inputs(self, car):
        inputs = car.driver.view_field.flatten().astype(float)
        # speed_transform = np.exp(-car.speed)
        speed_transform = 1. / max(car.speed, 1.)
        inputs = np.insert(inputs, 0, speed_transform, axis=0)
        return inputs

    def model_actions(self):
        return np.array([self.model_car.accelerate,
                         self.model_car.brake,
                         self.model_car.turn_left,
                         self.model_car.turn_right]).astype(float)

    def process_output(self, outputs, car):
        threshold = 0.5
        if outputs[0] > threshold:
            car.accelerate = True
        if outputs[1] > threshold:
            car.brake = True
        if outputs[2] > threshold:
            car.turn_left = True
        if outputs[3] > threshold:
            car.turn_right = True

    def error(self):
        inputs = self.prepare_inputs(self.model_car)
        outputs = self.ann.feedforward(inputs)
        wanted = self.model_actions()
        return self.ann.cost(outputs, wanted)


class ANN_Batch(ANN_Online):
    """
    This class implements the AI driver for a neural network.
    The network is trained online using gradient descent with
    a batch of accumulated samples.
    """
    def __init__(self,
                 n_hidden_neurons=5,
                 model_car=None,
                 learning_rate=0.2,
                 regularization=0.1,
                 epochs=60,
                 mini_batch_size=100,
                 *args, **kwargs):
        super(ANN_Batch, self).__init__(n_hidden_neurons, model_car,
            learning_rate, regularization, *args, **kwargs)
        self.epochs = epochs
        self.mini_batch_size = mini_batch_size
        self.reset_samples()

    def learn(self):
        """
        This method is called by the update method in the parent class.
        Here we only spy the model car.
        """
        self.input_samples.append(self.prepare_inputs(self.model_car))
        self.output_samples.append(self.model_actions())

    def train(self):
        """
        Train the whole set of samples.
        NOTE: May take a while and pause the game!
        """
        print "Training {} samples for {} epochs in batches of {}".format(
               len(self.input_samples), self.epochs, self.mini_batch_size)
        self.ann.train_set(self.input_samples, self.output_samples,
                           self.learning_rate, self.regularization,
                           self.epochs, self.mini_batch_size)
        self.reset_samples()

    def reset_samples(self):
        self.input_samples = []
        self.output_samples = []
