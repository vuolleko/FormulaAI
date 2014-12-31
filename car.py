import pygame
from math import sin, cos, pi

import constants

class Car(pygame.sprite.Sprite):
    def __init__(self):
        super(Car, self).__init__()
        self.get_image()
        self.rect = self.image.get_rect()
        self.rect.center = (100, 100)
        # self.rect.x = 100
        # self.rect.y = 100

        self.speed = 0
        self.direction = 0

    def get_image(self):
        self.car_sprite = pygame.image.load(constants.CARFILE).convert()
        self.image = pygame.Surface(self.car_sprite.get_size()).convert()

    def update(self):
        self.image = pygame.transform.rotate(self.car_sprite,
                                             self.direction+270)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.x += self.speed * cos(self.direction * pi / 180.)
        self.rect.y -= self.speed * sin(self.direction * pi / 180.)
        self.image.set_colorkey(constants.BLACK)

    def accelerate(self):
        self.speed += 0.1

    def brake(self):
        self.speed -= 0.1

    def turn(self, angle):
        self.direction += angle
