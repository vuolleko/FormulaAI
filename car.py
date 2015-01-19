import pygame
from math import sin, cos, pi, sqrt, asin

import constants

class Car(pygame.sprite.Sprite):
    def __init__(self, name, color, start_position, start_direction):
        super(Car, self).__init__()
        self.name = name
        self.color = color
        self._start_position = start_position
        self._start_direction = start_direction

        self._get_image()
        self.rect = self.image.get_rect()
        self._reset()

        self.distance_total = 0.
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

    def _reset(self):
        """
        Resets the car back to start.
        """
        self.speed = 0.
        self.direction = self._start_direction
        self.distance_try = 0.
        self.halfway = False
        self.laps = 0
        self.rect.center = self._start_position
        self.pos_x = self.rect.x  # pos_x is float, rect.x is int
        self.pos_y = self.rect.y
        self.image = pygame.transform.rotate(self._car_sprite,
                            (self._start_direction-constants.CAR_IMAGE_ANGLE) * 180 / pi)
        # self.image.set_colorkey(constants.BLACK)

    def update(self):
        """
        Updates the car's position according to the velocity vector.
        """
        self.distance_total += self.speed
        self.distance_try += self.speed
        self.pos_x += self.speed * cos(self.direction)
        self.pos_y -= self.speed * sin(self.direction)  # pos down
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)

    def accelerate(self):
        self.speed += constants.ACCELERATION

    def brake(self):
        self.speed -= constants.BRAKING

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

    def passed_halfway(self):
        """
        Mark that the car has passed the halfway mark. Makes it impossible
        to finish by simply reversing at start.
        """
        self.halfway = True

    def passed_finish(self):
        """
        Called when car passes the finish line. Only laps
        that pass through the halfway mark are counted.
        """
        if self.halfway:
            self.laps += 1
            self.halfway = False
            print "FINISH!"

    def crash(self):
        """
        Car crashes onto something. Reset and increase the crash counter.
        """
        self.crashes += 1
        self._reset()
