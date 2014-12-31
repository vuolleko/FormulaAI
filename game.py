import pygame

import car
import constants

pygame.init()

screen = pygame.display.set_mode((constants.SCREEN_WIDTH,
                                  constants.SCREEN_HEIGHT))
pygame.display.set_caption("FormulaAI")

player_car = car.Car(constants.BLUE)
car_list = pygame.sprite.Group()
car_list.add(player_car)

done = False
clock = pygame.time.Clock()

while not done:
    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player_car.accelerate()
    elif keys[pygame.K_DOWN]:
        player_car.brake()
    elif keys[pygame.K_LEFT]:
        player_car.turn(constants.TURN_SPEED)
    elif keys[pygame.K_RIGHT]:
        player_car.turn(-constants.TURN_SPEED)

    # update game status
    car_list.update()

    # handle game logic

    # update draw buffer
    screen.fill(constants.GREEN)
    car_list.draw(screen)

    # update screen
    clock.tick(60)  # 60 fps
    pygame.display.flip()


pygame.quit()