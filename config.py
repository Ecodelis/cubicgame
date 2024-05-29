import pyglet
from PIL import Image, ImageDraw
import pathlib

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 500
WINDOW_TITLE = "CUBIC-RUNNER"
# BACKGROUND_COLOR = (217, 194, 186)  # Beige Background
BACKGROUND_COLOR = (255, 255, 255)  # White

# Soundtracks
MUSIC_1 = "Audio\\Soundtracks\\Shmelt-Tutorial_Theme_v02.wav"
MUSIC_2 = "Audio\\Soundtracks\\Cubic_Game_Theme.wav"

bubble_1 = "Audio\\Sound Effects\\bubble-1.wav"
death_1 = "Audio\\Sound Effects\\death-1.wav"
up_1 = "Audio\\Sound Effects\\up-1.wav"
down_1 = "Audio\\Sound Effects\\down-1.wav"
powerup_1 = "Audio\\Sound Effects\\powerup-1.wav"




# Set up the screen
SCREEN_NUM = 0
SCREENS = pyglet.canvas.Display().get_screens()
SCREEN = SCREENS[SCREEN_NUM]

# Level
NUM_PLATFORMS = 2

# Player
PLAYER_SPEED = 4.0
INITIAL_SIZE = 35  # Pixels
GRID_SIZE = INITIAL_SIZE


# CREATE ENTITY IMG (Written by Copilot) ------
def create_Boxes():
    # Create a new image with RGBA mode
    image = Image.new("RGBA", (GRID_SIZE, GRID_SIZE))
    # Create a draw object
    draw = ImageDraw.Draw(image)
    # Draw a black rectangle
    draw.rectangle([(0, 0), (GRID_SIZE, GRID_SIZE)], fill=(0, 0, 0, 255))
    # Save the image
    directory = "Assets"
    image.save(f"{directory}/box-1.png")


def create_Rect():
    # Create a new image with RGBA mode
    image = Image.new("RGBA", (SCREEN_WIDTH, SCREEN_HEIGHT))
    # Create a draw object
    draw = ImageDraw.Draw(image)
    # Draw a black rectangle
    draw.rectangle([(0, 0), (SCREEN_WIDTH + 200, SCREEN_HEIGHT)], fill=(0, 0, 0, 255))
    # Save the image
    directory = "Assets"
    image.save(f"{directory}/rect-1.png")


def create_Bubble_1():
    # Dimensions
    # Create a new image with RGBA mode
    image = Image.new("RGBA", (15, 15))
    # Create a draw object
    draw = ImageDraw.Draw(image)
    # Draw a black rectangle
    draw.rectangle(
        [(0, 0), (15, 15)],
        fill=(0, 0, 255, 255),
    )
    # Save the image
    directory = "Assets"
    image.save(f"{directory}/bubble-1.png")

# looks at Assets directory
ASSETS_PATH = (
    pathlib.Path(__file__).resolve().parent / "assets"
)  

# LANES Y COORDINATES
Lane_0 = SCREEN_HEIGHT / 2 - GRID_SIZE * (1 / 2)
Lane_1 = SCREEN_HEIGHT / 2 + GRID_SIZE * (1 / 2)
Lane_2 = SCREEN_HEIGHT / 2 - GRID_SIZE * (3 / 2)
Lane_3 = SCREEN_HEIGHT / 2 + GRID_SIZE * (3 / 2)
Lane_4 = SCREEN_HEIGHT / 2 - GRID_SIZE * (5 / 2)
Lane_5 = SCREEN_HEIGHT / 2 + GRID_SIZE * (5 / 2)

Lane_6 = SCREEN_HEIGHT / 2 - GRID_SIZE * (7 / 2)
Lane_7 = SCREEN_HEIGHT / 2 + GRID_SIZE * (7 / 2)

# 7 5 3 1 0 2 4 6
LANE_AXIS = [
    Lane_0,
    Lane_1,
    Lane_2,
    Lane_3,
    Lane_4,
    Lane_5,
    Lane_6,
    Lane_7,
]  # 6 and 7 reserved for wall

# 0 1 2 3 4 5 6 7
T_LVL1 = 6
T_LVL2 = T_LVL1 + 6
T_LVL3 = T_LVL2 + 6
T_LVL4 = T_LVL3 + 6
T_LVL5 = T_LVL4 + 6
T_LVL6 = T_LVL5 + 6
T_LVL7 = T_LVL6 + 6

LEVEL_PROG_TIME = [0, T_LVL1, T_LVL2, T_LVL3, T_LVL4, T_LVL5, T_LVL6, T_LVL7]
