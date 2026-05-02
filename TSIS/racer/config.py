# config.py — Game-wide constants

# Window
WIDTH  = 480
HEIGHT = 640
TITLE  = "Racer"
FPS    = 60

# Road layout
LANES       = 2
ROAD_LEFT   = 80
ROAD_RIGHT  = 400
ROAD_WIDTH  = ROAD_RIGHT - ROAD_LEFT        # 320
LANE_W      = ROAD_WIDTH // LANES           # 80
LANE_CENTERS = [ROAD_LEFT + LANE_W * i + LANE_W // 2 for i in range(LANES)]  # [120,200,280,360]

# Player car
PLAYER_W     = 36
PLAYER_H     = 60
PLAYER_START_Y = HEIGHT - 120

# Road scroll
BASE_ROAD_SPEED = 5          # pixels per frame
SPEED_INCREMENT = 0.0008     # added per frame (continuous difficulty)

# Spawn rates (frames between spawns; lower = more frequent)
TRAFFIC_SPAWN_BASE   = 90
OBSTACLE_SPAWN_BASE  = 120
COIN_SPAWN_BASE      = 50
POWERUP_SPAWN_BASE   = 300
HAZARD_SPAWN_BASE    = 180   # lane hazard zones

# Scoring
SCORE_PER_FRAME      = 0.05  # distance score per frame
SCORE_PER_COIN       = 10    # multiplied by coin weight in racer.py

# Leaderboard / settings files
LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE    = "settings.json"

# Colors
BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
DARK_BG    = ( 18,  18,  28)
ROAD_DARK  = ( 40,  40,  50)
ROAD_LINE  = (220, 200,  50)
GRASS_L    = ( 30,  80,  30)
GRASS_R    = ( 30,  80,  30)
GRAY       = (120, 120, 130)
LIGHT_GRAY = (210, 210, 220)
RED        = (220,  50,  50)
GREEN      = ( 50, 210,  60)
BLUE       = ( 50, 140, 240)
GOLD       = (255, 210,   0)
ORANGE     = (255, 140,   0)
PURPLE     = (170,  50, 230)
CYAN       = (  0, 210, 220)
DARK_RED   = (140,  20,  20)

# Car colour presets (name, RGB)
CAR_COLORS = [
    ("Red",    (220, 50,  50)),
    ("Blue",   (50,  130, 240)),
    ("Green",  (50,  200, 70)),
    ("Yellow", (240, 210, 40)),
    ("Purple", (160, 50,  230)),
    ("White",  (230, 230, 230)),
]

# Difficulty presets  (label, traffic_mult, obstacle_mult, speed_add)
DIFFICULTIES = [
    ("Easy",   0.6, 0.6, 0.0),
    ("Medium", 1.0, 1.0, 0.0),
    ("Hard",   1.4, 1.4, 2.0),
]

# Power-up types
PU_NITRO  = "nitro"
PU_SHIELD = "shield"
PU_REPAIR = "repair"

PU_COLORS = {PU_NITRO: ORANGE, PU_SHIELD: CYAN, PU_REPAIR: GREEN}
PU_LABELS = {PU_NITRO: " NITRO", PU_SHIELD: "SHIELD", PU_REPAIR: " REPAIR"}
PU_DURATION = {PU_NITRO: FPS * 4, PU_SHIELD: 0, PU_REPAIR: 0}   # frames; 0 = instant/until-hit

POWERUP_LIFESPAN = FPS * 8   # frames before uncollected power-up disappears

# Obstacle types
OBS_BARRIER = "barrier"
OBS_OIL     = "oil"
OBS_POTHOLE = "pothole"

OBS_COLORS = {OBS_BARRIER: GRAY, OBS_OIL: (20, 20, 60), OBS_POTHOLE: (60, 40, 20)}
OBS_LABELS  = {OBS_BARRIER: "BARRIER", OBS_OIL: "OIL", OBS_POTHOLE: "POTHOLE"}