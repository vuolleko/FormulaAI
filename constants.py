BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
RED_ORIG_CAR = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

COLOR_TEXT = (30, 30, 30)

# colors in track mask file
COLOR_OFF_TRACK = (255, 255, 255)
COLOR_HALFWAY = (0, 200, 0)
COLOR_FINISH = (200, 0, 0)

WIDTH_TRACK = 600
HEIGHT_TRACK = 600
WIDTH_STATUS = 200
HEIGHT_STATUS = HEIGHT_TRACK
WIDTH_SCREEN = WIDTH_TRACK + WIDTH_STATUS
HEIGHT_SCREEN = HEIGHT_TRACK

FRAME_RATE = 60

CAR_FILE = "assets/car_red.png"
TRACK_FILE = "assets/track2_show.png"
TRACK_MASK_FILE = "assets/track2_mask.png"

CAR_IMAGE_ANGLE = 1.570796  # 90 deg, 0 deg = right
TURN_SPEED = 0.052360  # 3 deg
ACCELERATION = 0.05
BRAKING = 0.1