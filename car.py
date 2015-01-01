import pygame
from math import sin, cos, pi

import constants

class Car(pygame.sprite.Sprite):
    def __init__(self, color):
        super(Car, self).__init__()
        self.speed = 0.
        self.direction = 0.
        self.total_distance = 0.
        self.get_image(color)
        self.rect = self.image.get_rect()
        self.rect.center = (100, 100)

        self.pos_x = self.rect.x  # pos_x is float, rect.x is int
        self.pos_y = self.rect.y

    def get_image(self, color):
        self.car_sprite = pygame.image.load(constants.CAR_FILE).convert()
        car_sprite_pixelarray = pygame.PixelArray(self.car_sprite)
        car_sprite_pixelarray.replace(constants.RED_ORIG_CAR, color, 0.1)
        self.car_sprite = car_sprite_pixelarray.make_surface()
        self.car_sprite = pygame.transform.scale(self.car_sprite, (20, 30))
        # pygame.transform.threshold(self.car_sprite, self.car_sprite,
        #     constants.RED_ORIG_CAR, (1, 1, 1), diff_color=color, 2, self.car_sprite, True)
        self.image = pygame.transform.rotate(self.car_sprite,
                                             self.direction+270)
        self.image.set_colorkey(constants.BLACK)

    def update(self):
        self.total_distance += self.speed
        self.pos_x += self.speed * cos(self.direction * pi / 180.)
        self.pos_y -= self.speed * sin(self.direction * pi / 180.)  # pos down
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)

    def accelerate(self):
        self.speed += 0.1

    def brake(self):
        self.speed -= 0.1

    def turn(self, angle):
        self.direction += angle
        self.image = pygame.transform.rotate(self.car_sprite,
                                             self.direction+270)
        self.image.set_colorkey(constants.BLACK)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.pos_x = self.rect.x + self.pos_x % 1  # include decimal part
        self.pos_y = self.rect.y + self.pos_y % 1
