"""
Settings and constants for the Escape Room game.
"""

# Debug settings
DEBUG_MODE = False  # Set to True to show collision areas and other debug info

# Game window settings
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Escape Room: PMBOK vs Scrum"
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
BROWN = (165, 42, 42)
DARK_GREEN = (0, 100, 0)
NAVY = (0, 0, 128)
TEAL = (0, 128, 128)
MAROON = (128, 0, 0)
OLIVE = (128, 128, 0)
SILVER = (192, 192, 192)
CHARCOAL = (54, 69, 79)
CREAM = (255, 253, 208)

# Stardew Valley inspired colors
SDV_BLUE = (106, 135, 204)      # Sky blue
SDV_GREEN = (143, 188, 143)     # Soft green
SDV_BROWN = (139, 69, 19)       # Wood brown
SDV_YELLOW = (255, 223, 0)      # Golden yellow
SDV_ORANGE = (210, 105, 30)     # Rustic orange
SDV_CREAM = (255, 248, 220)     # Cream
SDV_DARK_GREEN = (85, 107, 47)  # Forest green
SDV_LIGHT_BROWN = (222, 184, 135) # Tan
SDV_PURPLE = (147, 112, 219)    # Soft purple
SDV_PINK = (255, 182, 193)      # Light pink

# Player settings
PLAYER_SPEED = 5
PLAYER_WIDTH = 150  # Aumentado de 115 a 150 (30% más)
PLAYER_HEIGHT = 150  # Aumentado de 115 a 150 (30% más)
PLAYER_ANIMATION_SPEED = 0.1

# Room settings
ROOM_TIME_LIMIT = 300  # 5 minutes in seconds
ROOM_WIDTH = 1200
ROOM_HEIGHT = 650
ROOM_BORDER_WIDTH = 10

# Object settings
OBJECT_HOVER_DISTANCE = 100  # Distance at which objects show hover effect
OBJECT_INTERACTION_DISTANCE = 80  # Distance at which player can interact with objects

# UI settings
UI_FONT_SIZE_LARGE = 48
UI_FONT_SIZE_MEDIUM = 32
UI_FONT_SIZE_SMALL = 24
UI_FONT_SIZE_TINY = 18
UI_PADDING = 20
UI_BORDER_WIDTH = 2
UI_BUTTON_WIDTH = 250
UI_BUTTON_HEIGHT = 60
UI_BUTTON_RADIUS = 10  # Rounded corners
UI_TOOLTIP_WIDTH = 300
UI_TOOLTIP_PADDING = 10

# Animation settings
ANIMATION_SPEED = 0.1
TRANSITION_SPEED = 0.05
PARTICLE_COUNT = 20
PARTICLE_SPEED = 2
PARTICLE_SIZE = 5
PARTICLE_LIFETIME = 30

# Game states
STATE_MENU = "menu"
STATE_GAME = "game"
STATE_INSTRUCTIONS = "instructions"
STATE_GAME_OVER = "game_over"
STATE_VICTORY = "victory"
STATE_PATH_SELECTION = "path_selection"
STATE_LOADING = "loading"
STATE_PAUSE = "pause"
STATE_DIALOG = "dialog"
STATE_PUZZLE = "puzzle"
STATE_TRANSITION = "transition"
STATE_CUTSCENE = "cutscene"
STATE_CREDITS = "credits"

# Paths
PATH_PMBOK = "pmbok"
PATH_SCRUM = "scrum"

# Asset paths
ASSETS_DIR = "assets"
IMAGES_DIR = f"{ASSETS_DIR}/images"
SOUNDS_DIR = f"{ASSETS_DIR}/sounds"
FONTS_DIR = f"{ASSETS_DIR}/fonts"
