import pygame

import car
import constants

pygame.init()

screen = pygame.display.set_mode((constants.SCREEN_WIDTH,
                                  constants.SCREEN_HEIGHT))
pygame.display.set_caption("FormulaAI")

player_car = car.Car()
car_list = pygame.sprite.Group()
car_list.add(player_car)

done = False
clock = pygame.time.Clock()

while not done:
    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player_car.accelerate()
            elif event.key == pygame.K_DOWN:
                player_car.brake()

    # update game status
    car_list.update()

    # handle game logic

    # update draw buffer
    car_list.draw(screen)

    # update screen
    clock.tick(60)  # 60 fps
    pygame.display.flip()


pygame.quit()