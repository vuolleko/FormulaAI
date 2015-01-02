import pygame
from math import sin, cos, pi, sqrt, asin

import constants

class Car(pygame.sprite.Sprite):
    def __init__(self, color, start_position, start_direction):
        super(Car, self).__init__()
        self.start_position = start_position
        self.start_direction = start_direction

        self.get_image(color)
        self.rect = self.image.get_rect()
        self.reset()

        self.distance_total = 0.
        width, height = self.car_sprite.get_size()
        self.half_diag = sqrt(width**2. + height**2.) / 2.
        self.center2corner_angle = asin(width / 2. / self.half_diag)

    def get_image(self, color):
        self.car_sprite = pygame.image.load(constants.CAR_FILE).convert()
        car_sprite_pixelarray = pygame.PixelArray(self.car_sprite)
        car_sprite_pixelarray.replace(constants.RED_ORIG_CAR, color, 0.1)
        self.car_sprite = car_sprite_pixelarray.make_surface()
        self.car_sprite = pygame.transform.scale(self.car_sprite, (10, 15))
        self.image = pygame.Surface(self.car_sprite.get_size()).convert()

    def reset(self):
        self.speed = 0.
        self.direction = self.start_direction
        self.distance_try = 0.
        self.halfway = False
        self.rect.center = self.start_position
        self.pos_x = self.rect.x  # pos_x is float, rect.x is int
        self.pos_y = self.rect.y
        self.image = pygame.transform.rotate(self.car_sprite,
                            (self.start_direction-constants.CAR_IMAGE_ANGLE) * 180 / pi)
        self.image.set_colorkey(constants.BLACK)

    def update(self):
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
        self.direction += angle
        self.image = pygame.transform.rotate(self.car_sprite,
                            (self.direction - constants.CAR_IMAGE_ANGLE)*180/pi)
        self.image.set_colorkey(constants.BLACK)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.pos_x = self.rect.x + self.pos_x % 1  # include decimal part
        self.pos_y = self.rect.y + self.pos_y % 1

    def get_corners(self):
        corners = []
        for angle in [-self.center2corner_angle, self.center2corner_angle]:
            x = self.rect.center[0] + self.half_diag * cos(self.direction+angle)
            y = self.rect.center[1] + self.half_diag * sin(self.direction+angle)
            corners.append([int(x), int(y)])
        return corners

    def passed_halfway(self):
        self.halfway = True
