import pygame

from car import Car
from track import Track
from statusbar import Status_bar
import constants

pygame.init()

screen = pygame.display.set_mode((constants.WIDTH_SCREEN,
                                  constants.HEIGHT_SCREEN))
pygame.display.set_caption("FormulaAI")

track = Track()
start_position, start_direction = track.find_start(3)

player_car = Car("Player", constants.BLUE, start_position[0], start_direction)
ann_car = Car("ANN", constants.RED, start_position[1], start_direction)
ai_car = Car("AI", constants.GREEN, start_position[2], start_direction)

sprite_list = pygame.sprite.Group()
car_list = pygame.sprite.Group()
for car in [player_car, ann_car, ai_car]:
    car_list.add(car)
    sprite_list.add(car)

status_bar = Status_bar(car_list)
sprite_list.add(status_bar)

done = False
clock = pygame.time.Clock()

while not done:
    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # controls for the player car
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player_car.accelerate()
    if keys[pygame.K_DOWN]:
        player_car.brake()
    if keys[pygame.K_LEFT]:
        player_car.turn(constants.TURN_SPEED)
    if keys[pygame.K_RIGHT]:
        player_car.turn(-constants.TURN_SPEED)

    # update game status and handle game logic
    car_list.update(track)
    status_bar.update()

    # update draw buffer
    track.draw(screen)
    sprite_list.draw(screen)

    # update screen
    clock.tick(constants.FRAME_RATE)  # fps
    pygame.display.flip()


pygame.quit()