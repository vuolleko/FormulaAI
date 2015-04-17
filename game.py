import pygame

from car import Car
import driver
from track import Track
from statusbar import Status_bar
from plot_error import Error_plot
import constants

# init stuff
pygame.init()
clock = pygame.time.Clock()
done = False
draw_viewfield = False
learn_from_player = False

screen = pygame.display.set_mode((constants.WIDTH_SCREEN,
                                  constants.HEIGHT_SCREEN))
pygame.display.set_caption("FormulaAI")

track = Track()
start_position, start_direction = track.find_start(4)

player_car = Car("Player", constants.BLUE, start_position[0], start_direction,
                 driver.Player())
ai_tif_car = Car("AI_TIF", constants.YELLOW, start_position[3], start_direction,
                 driver.AI_TIF())
ann_online_car = Car("ANN_Online", constants.RED, start_position[2],
                     start_direction, driver.ANN_Online(model_car=ai_tif_car))
ann_batch_car = Car("ANN_Batch", constants.GREEN, start_position[1],
                    start_direction, driver.ANN_Batch(model_car=ai_tif_car))

sprite_list = pygame.sprite.Group()
car_list = pygame.sprite.Group()
for car in [player_car, ann_online_car, ann_batch_car, ai_tif_car]:
    car_list.add(car)
    sprite_list.add(car)

status_bar = Status_bar(car_list)
sprite_list.add(status_bar)

if constants.PLOT_ERROR:
    error_plot = Error_plot()

frame_counter = 0

while not done:
    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_v:
                draw_viewfield = not draw_viewfield
            elif event.key == pygame.K_l:
                learn_from_player = not learn_from_player
            elif event.key == pygame.K_r:
                for car in car_list:
                    car.reset(frame_counter)
                ann_batch_car.driver.reset_samples()
            elif event.key == pygame.K_t:
                ann_batch_car.driver.train()
            elif event.key == pygame.K_p:
                paused = True
                while paused:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_p:
                                paused = False
                    clock.tick(constants.FRAME_RATE)  # fps

    # update game status and handle game logic
    car_list.update(track, frame_counter)
    status_bar.update(frame_counter)

    # update draw buffer
    track.draw(screen)
    sprite_list.draw(screen)
    if draw_viewfield:
        for car in car_list:
            car.driver.draw_viewfield(screen)

    # update error plot
    if constants.PLOT_ERROR:
        if frame_counter % constants.PLOT_ERROR_INTERVAL == 0:
            error1 = ann_online_car.driver.error()
            error2 = ann_batch_car.driver.error()
            error_plot.update(error1, error2)

    # update screen
    clock.tick(constants.FRAME_RATE)  # fps
    frame_counter += 1
    pygame.display.flip()


pygame.quit()
