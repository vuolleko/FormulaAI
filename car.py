import pygame
from math import sin, cos, pi, sqrt, asin

import constants

class Car(pygame.sprite.Sprite):
    """
    This class implements the drawing and behavior of cars (excluding controls.)
    """
    def __init__(self, name, color, start_position, start_direction, driver):
        super(Car, self).__init__()
        self.name = name
        self.color = color
        self._start_position = start_position
        self._start_direction = start_direction
        self.driver = driver

        self._get_image()
        self.rect = self.image.get_rect()
        self.reset(0.)

        self.distance_total = 0.
        self.laps_total = 0
        self.lap_frame_best = 999999
        self.crashes = 0
        width, height = self._car_sprite.get_size()
        self.half_diag = sqrt(width**2. + height**2.) / 2.
        self.center2corner_angle = asin(width / 2. / self.half_diag)

    def _get_image(self):
        """
        Load the car sprite and paint it.
        """
        self._car_sprite = pygame.image.load(constants.CAR_FILE).convert_alpha()
        car_sprite_pixelarray = pygame.PixelArray(self._car_sprite)
        car_sprite_pixelarray.replace(constants.RED_ORIG_CAR, self.color, 0.1)
        self._car_sprite = car_sprite_pixelarray.make_surface()
        # self._car_sprite = pygame.transform.scale(self._car_sprite, (10, 15))
        self.image = pygame.Surface(self._car_sprite.get_size()).convert_alpha()

    def init_controls(self):
        """
        Sets car controls to defaults.
        """
        self.accelerate = constants.ALWAYS_FULLGAS
        self.brake = False
        self.turn_left = False
        self.turn_right = False

    def reset(self, frame_counter):
        """
        Resets the car back to start.
        """
        self.init_controls()
        self.speed = 0.
        self.direction = self._start_direction
        self.distance_try = 0.
        self.halfway = False
        self.laps = 0
        self.lap_frame = 0.
        self.lap_frame_prev = frame_counter
        self.rect.center = self._start_position
        self.pos_x = self.rect.x  # pos_x is float, rect.x is int
        self.pos_y = self.rect.y
        self.image = pygame.transform.rotate(self._car_sprite,
                            (self._start_direction-constants.CAR_IMAGE_ANGLE) * 180 / pi)
        # self.image.set_colorkey(constants.BLACK)

    def update(self, track, frame_counter):
        """
        Updates the car's position according to the velocity vector.
        Checks if the car has gone off track etc.
        Updates the car's driver.
        """
        if self.accelerate:
            self.speed += constants.ACCELERATION
        if self.brake:
            self.speed -= constants.BRAKING
        if self.turn_left:
            self.turn(constants.TURN_SPEED)
        if self.turn_right:
            self.turn(-constants.TURN_SPEED)
        self.speed -= constants.FRICTION
        if self.speed < 0.:
            self.speed = 0.

        self.distance_total += self.speed
        self.distance_try += self.speed
        self.pos_x += self.speed * cos(self.direction)
        self.pos_y -= self.speed * sin(self.direction)  # pos down
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)

        if self.off_track(track):
            self.crash(frame_counter)
        else:
            self.passed_halfway(track)
            self.passed_finish(track, frame_counter)

        self.driver.look(self, track)
        self.driver.update(self, frame_counter)

    def turn(self, angle):
        """
        Updates the car's direction angle and rotates the image.
        """
        self.direction += angle
        self.image = pygame.transform.rotate(self._car_sprite,
                            (self.direction - constants.CAR_IMAGE_ANGLE)*180/pi)
        self.image.set_colorkey(constants.BLACK)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.pos_x = self.rect.x + self.pos_x % 1  # include decimal part
        self.pos_y = self.rect.y + self.pos_y % 1

    def get_corners(self):
        """
        Returns the coordinates corresponding to the front corners of the car.
        """
        corners = []
        for angle in [-self.center2corner_angle, self.center2corner_angle]:
            x = self.rect.center[0] + self.half_diag * cos(self.direction+angle)
            y = self.rect.center[1] - self.half_diag * sin(self.direction+angle)
            corners.append([int(x), int(y)])
        return corners

    def passed_halfway(self, track):
        """
        Mark that the car has passed the halfway mark. Makes it impossible
        to finish by simply reversing at start.
        """
        if track.track_mask.get_at(self.rect.center) == constants.COLOR_HALFWAY:
            self.halfway = True

    def passed_finish(self, track, frame_counter):
        """
        Called when car passes the finish line. Only laps
        that pass through the halfway mark are counted.
        """
        if track.track_mask.get_at(self.rect.center) == constants.COLOR_FINISH:
            if self.halfway:
                self.laps += 1
                self.laps_total += 1
                self.lap_frame = frame_counter - self.lap_frame_prev
                self.lap_frame_prev = frame_counter
                self.lap_frame_best = min(self.lap_frame_best, self.lap_frame)
                self.halfway = False
                # print(self.name + ": FINISH!")

    def off_track(self, track):
        """
        Check if the car is off track.
        """
        for point in self.get_corners():
            if track.off_track(*point):
                return True
        return False

    def crash(self, frame_counter):
        """
        Car crashes onto something. Reset and increase the crash counter.
        """
        self.crashes += 1
        self.reset(frame_counter)

    def flip(self):
        """
        Flip car's direction.
        """
        self.speed = 0.
        self.direction += pi
