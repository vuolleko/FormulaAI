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
        self.error = 0.

    def init_view(self):
        """
        Initialize the driver's view.
        """
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

    def update(self, car, frame_counter, *args):
        """
        Default actions for drivers.
        """
        car.init_controls()


class Player(Driver):
    """
    This class implements the driver for the player car.
    """
    def __init__(self, *args, **kwargs):
        super(Player, self).__init__(*args, **kwargs)

    def update(self, car, frame_counter, *args, **kwargs):
        """
        Read keyboard for controlling the player car.
        """
        super(Player, self).update(car, frame_counter, *args, **kwargs)

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
                             np.pi / (1.5 * constants.TURN_SPEED))

    def update(self, car, frame_counter, *args):
        """
        The car turns depending on whether its closest side checks
        are off track. Brake is applied if the car is going too fast
        with wall in front, and especially if the corner is tight.
        """
        # TODO: tuned for track and settings, generalize!
        super(AI_TIF, self).update(car, frame_counter, *args)
        car.accelerate = True
        if self.view_field[0,0] and not self.view_field[-1,0]:
            car.turn_left = True
        elif self.view_field[-1,0] and not self.view_field[0,0]:
            car.turn_right = True

        if self.view_field[self.view_resolution[0]//2, -1]:
            car.brake = car.speed > self.allowed_speed

            # special handling of tight corners
            if not all(self.view_field[[0,-1], 1]) and car.speed > 1.:
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
                 use_keras=False,
                 *args, **kwargs):
        super(ANN_Online, self).__init__(*args, **kwargs)
        self.model_car = model_car  # the car to learn from
        self.learning_rate = learning_rate
        self.regularization = regularization
        self.use_keras = use_keras

        n_inputs = self.view_resolution[0] * self.view_resolution[1] + 1  # viewpoints + speed
        n_outputs = 4  # accelerate, brake, left, right

        if self.use_keras:
            self.ann = ann.create_ANN_Keras(n_inputs, n_hidden_neurons, n_outputs)
        else:
            self.ann = ann.ANN(n_inputs, n_hidden_neurons, n_outputs)

    def update(self, own_car, frame_counter, *args):
        super(ANN_Online, self).update(own_car, frame_counter, *args)

        if constants.PLOT_ERROR:
            self.evaluate_error()

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

        if self.use_keras:
            return inputs[None, :]
        else:
            return inputs

    def model_actions(self):
        actions = np.array([self.model_car.accelerate,
                         self.model_car.brake,
                         self.model_car.turn_left,
                         self.model_car.turn_right]).astype(float)
        if self.use_keras:
            return actions[None, :]
        else:
            return actions

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

    def evaluate_error(self):
        """
        Evaluate the cost function with model input data.
        """
        inputs = self.prepare_inputs(self.model_car)
        outputs = self.ann.feedforward(inputs)
        wanted = self.model_actions()
        self.error = self.ann.cost(outputs, wanted)


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
        print("Training {} samples for {} epochs in batches of {}".format(
               len(self.input_samples), self.epochs, self.mini_batch_size))
        self.ann.train_set(self.input_samples, self.output_samples,
                           self.learning_rate, self.regularization,
                           self.epochs, self.mini_batch_size)
        self.reset_samples()

    def reset_samples(self):
        self.input_samples = []
        self.output_samples = []


class ReinforcedLearner(ANN_Online):
    """
    This class implements the AI driver that learns all by itself
    using Reinforced learning (Q-Learning).

    Some inspiration from:
    http://outlace.com/Reinforcement-Learning-Part-3/
    """
    def __init__(self,
                 discount=0.9,
                 n_memories=300,
                 mini_batch_size=50,
                 learning_rate=0.2,
                 regularization=0.1,
                 *args, **kwargs):
        super(ReinforcedLearner, self).__init__(*args, **kwargs)
        self.discount = discount
        self.prob_random = 1.  # initial probability of chooosing random action
        self.skip_frames = 5

        # init state
        self.prev_state = np.concatenate(([0], self.view_field.flatten().astype(float)))
        if self.use_keras:
            self.prev_state = self.prev_state[None, :]
        self.qval = self.ann.predict(self.prev_state)[0]
        self.action = 1  # brake, since car at start which gives neg. reward

        self.n_memories = n_memories
        self.memories = []  # prev_state, action, new_state, reward
        self.mini_batch_size = mini_batch_size

    def update(self, own_car, frame_counter, *args):
        if frame_counter % self.skip_frames != 0:
            return

        own_car.init_controls()
        # super(ReinforcedLearner, self).update(own_car)

        # get reward from previous action
        reward = self.get_reward(own_car, frame_counter)
        print('reward {:.2f}, prob {:.2f}'.format(reward, self.prob_random))

        new_state = self.prepare_inputs(own_car)
        self.memories.append([self.prev_state, self.action, new_state, reward])

        # remove too old memories
        if len(self.memories) > self.n_memories:
            self.memories.pop(0)

        # select memories to train on
        sel_inds = np.random.choice(len(self.memories),
                                    min(len(self.memories), self.mini_batch_size),
                                    replace=False)

        inputs = []
        targets = []
        for ind in sel_inds:
            prev_state = self.memories[ind][0]
            action = self.memories[ind][1]
            new_state = self.memories[ind][2]
            reward = self.memories[ind][3]

            target = self.ann.predict(prev_state)[0]  # Q for previous state
            new_Q = self.ann.predict(new_state)[0]  # Q for new state after move
            target[action] += reward #- self.learning_rate * target[action]
            if not np.isclose(reward, -10):  # check for terminal state
                target[action] += self.discount * np.max(new_Q)
                # target[action] += self.learning_rate * self.discount * np.max(new_Q)

            inputs.append(prev_state)
            targets.append(target)

        if self.use_keras:
            self.ann.fit(np.array(inputs), np.array(targets), batch_size=len(inputs), nb_epoch=1, verbose=0)
        else:
            self.ann.train_set(inputs, targets, self.learning_rate, self.regularization)

        new_state = self.memories[-1][2]
        self.qval = self.ann.predict(new_state)[0]

        # choose action
        if self.prob_random > np.random.rand():
            self.action = np.random.randint(0, 4)
        else:
            self.action = np.argmax(self.qval)

        # set car controls according to the chosen action
        self.process_output(np.eye(1, 4, self.action)[0], own_car)
        self.prev_state = new_state

        # decrease randomness over time
        if self.prob_random > 0.1 and own_car.speed > 0:
            self.prob_random *= 0.99

        if constants.PLOT_ERROR:
            self.evaluate_error()

    def get_reward(self, own_car, frame_counter):
        # check if car just hit a wall and was reset to beginning
        if own_car.lap_frame_prev >= frame_counter - self.skip_frames:
        # if own_car.distance_try < 1e-4:
            return -10
        else:  # give reward for clear view and speed
            # clearness = 2. - np.sum(self.view_field[2, :3]) - 2. * np.sum(self.view_field[:, 0])
            # clearness = (self.view_resolution[0]-2) - np.sum(self.view_field[1:-1, :2])
            # clearness = self.view_resolution[0] * self.view_resolution[1] - np.sum(self.view_field) * 2.6
            # return clearness * (own_car.speed) * 2
            # return clearness * (own_car.speed + constants.ACCELERATION) * 5
            # return own_car.distance_try
            return own_car.speed - constants.ACCELERATION
