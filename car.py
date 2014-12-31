import pygame
from math import sin, cos, pi

import constants

class Car(pygame.sprite.Sprite):
    def __init__(self, color):
        super(Car, self).__init__()
        self.speed = 0.
        self.direction = 0.
        self.get_image()
        self.rect = self.image.get_rect()
        self.rect.center = (100, 100)

        self.pos_x = self.rect.x
        self.pos_y = self.rect.y

    def get_image(self):
        self.car_sprite = pygame.image.load(constants.CARFILE).convert()
        self.image = pygame.transform.rotate(self.car_sprite,
                                             self.direction+270)
        self.image.set_colorkey(constants.BLACK)

    def update(self):
        self.pos_x += self.speed * cos(self.direction * pi / 180.)
        self.pos_y -= self.speed * sin(self.direction * pi / 180.)
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
        self.pos_x = self.rect.x + self.pos_x % 1
        self.pos_y = self.rect.y + self.pos_y % 1
