import pygame

import constants

class Car(pygame.sprite.Sprite):
    def __init__(self):
        super(Car, self).__init__()
        self.get_image()
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 100

        self.speed_x = 0
        self.speed_y = 0

    def get_image(self):
        car_sprite = pygame.image.load(constants.CARFILE).convert()
        self.image = pygame.Surface(car_sprite.get_size()).convert()
        self.image.blit(car_sprite, (0, 0))
        self.image.set_colorkey(constants.BLACK)


    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

    def accelerate(self):
        self.speed_x += 1

    def brake(self):
        self.speed_x -= 1