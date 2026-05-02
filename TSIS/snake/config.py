
# Window
WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 600
TITLE         = "Snake Game - TSIS"

# Grid
CELL_SIZE     = 20
COLS          = WINDOW_WIDTH  // CELL_SIZE   # initial value = 40
ROWS          = WINDOW_HEIGHT // CELL_SIZE   # initial value = 30

# Gameplay
INITIAL_SPEED       = 8          # FPS (frames per second the game logic updates)
SPEED_INCREMENT     = 1          # extra FPS per level
FOOD_PER_LEVEL      = 5          # food items eaten to advance a level
OBSTACLES_FROM_LVL  = 3          # obstacles appear from this level onward
OBSTACLES_PER_LEVEL = 4          # new blocks added each level (from lvl 3)

# Food timers (in milliseconds)
FOOD_DISAPPEAR_MS   = 7000       # normal timed food lifespan
POWERUP_LIFESPAN_MS = 8000       # power-up on-field lifespan
POWERUP_EFFECT_MS   = 5000       # power-up active effect duration

# Poison
POISON_SHORTEN      = 2          # segments removed when poison eaten
POISON_MIN_LENGTH   = 1          # length at which eating poison = game over

# Colors  (R, G, B)
BLACK       = (  0,   0,   0)
WHITE       = (255, 255, 255)
DARK_BG     = ( 15,  15,  25)
GRID_COLOR  = ( 30,  30,  45)

GREEN       = ( 50, 205,  50)
DARK_GREEN  = ( 20, 120,  20)
RED         = (220,  50,  50)
DARK_RED    = (120,   0,   0)     # poison food
GOLD        = (255, 215,   0)
BLUE        = ( 50, 150, 255)
PURPLE      = (160,  32, 240)
ORANGE      = (255, 140,   0)
CYAN        = (  0, 220, 220)
GRAY        = (100, 100, 100)
LIGHT_GRAY  = (200, 200, 200)
WALL_COLOR  = ( 80,  80, 100)

# Food types
FOOD_NORMAL   = "normal"
FOOD_BONUS    = "bonus"
FOOD_TIMED    = "timed"
FOOD_POISON   = "poison"

FOOD_POINTS = {
    FOOD_NORMAL: 10,
    FOOD_BONUS:  25,
    FOOD_TIMED:  15,
    FOOD_POISON:  0,
}

FOOD_COLORS = {
    FOOD_NORMAL: GREEN,
    FOOD_BONUS:  GOLD,
    FOOD_TIMED:  CYAN,
    FOOD_POISON: DARK_RED,
}

# Power-up types
PU_SPEED_BOOST = "speed_boost"
PU_SLOW_MOTION = "slow_motion"
PU_SHIELD      = "shield"

PU_COLORS = {
    PU_SPEED_BOOST: ORANGE,
    PU_SLOW_MOTION: BLUE,
    PU_SHIELD:      PURPLE,
}

PU_LABELS = {
    PU_SPEED_BOOST: "SPEED",
    PU_SLOW_MOTION: "SLOW",
    PU_SHIELD:      "SHIELD",
}

# DB connection 
DB_DSN = "dbname=snakegame user=postgres password=Sh7376990608 host=localhost port=5432"