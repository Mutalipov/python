
import pygame
import random
import math
from config import *


# Utility

def rand_lane() -> int:
    return random.randint(0, LANES - 1)


def lane_x(lane: int) -> int:
    return LANE_CENTERS[lane]


# Road scroll strips

class RoadStrip:
    """A dashed centre-line segment."""
    HEIGHT = 40
    GAP    = 40

    def __init__(self, y):
        self.y = y

    def update(self, speed):
        self.y += speed

    def draw(self, surface):
        for lane in range(1, LANES):
            x = ROAD_LEFT + LANE_W * lane
            pygame.draw.rect(surface, ROAD_LINE, (x - 2, int(self.y), 4, self.HEIGHT))


# Player car

class PlayerCar:
    MOVE_SPEED = 5      # pixels per frame for lateral slide

    def __init__(self, color):
        self.lane   = LANES // 2
        self.x      = float(lane_x(self.lane))
        self.y      = float(PLAYER_START_Y)
        self.color  = tuple(color)
        self.target_x = self.x
        self.crashed  = False

    def set_color(self, color):
        self.color = tuple(color)

    def move_left(self):
        if self.lane > 0:
            self.lane -= 1
            self.target_x = lane_x(self.lane)

    def move_right(self):
        if self.lane < LANES - 1:
            self.lane += 1
            self.target_x = lane_x(self.lane)

    def update(self):
        # Smooth slide
        dx = self.target_x - self.x
        if abs(dx) < self.MOVE_SPEED:
            self.x = self.target_x
        else:
            self.x += self.MOVE_SPEED * (1 if dx > 0 else -1)

    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x) - PLAYER_W // 2,
            int(self.y) - PLAYER_H // 2,
            PLAYER_W, PLAYER_H
        )

    def draw(self, surface, shield_active: bool):
        r = self.rect()
        # Body
        pygame.draw.rect(surface, self.color, r, border_radius=6)
        # Windshield
        ws = pygame.Rect(r.x + 6, r.y + 8, r.width - 12, 14)
        pygame.draw.rect(surface, (180, 220, 255), ws, border_radius=3)
        # Wheels
        for wx, wy in [(r.x - 4, r.y + 6), (r.right - 4, r.y + 6),
                       (r.x - 4, r.bottom - 18), (r.right - 4, r.bottom - 18)]:
            pygame.draw.rect(surface, BLACK, (wx, wy, 8, 12), border_radius=2)
        # Shield ring
        if shield_active:
            cx, cy = r.centerx, r.centery
            pygame.draw.circle(surface, CYAN, (cx, cy), max(PLAYER_W, PLAYER_H) // 2 + 8, 3)


# Traffic car (enemy)

TRAFFIC_COLORS = [(180, 30, 30), (30, 100, 180), (180, 140, 30),
                  (100, 30, 180), (30, 150, 80), (150, 150, 150)]


class TrafficCar:
    W = 34
    H = 56

    def __init__(self, lane: int, y: float, speed: float):
        self.lane  = lane
        self.x     = float(lane_x(lane))
        self.y     = y
        self.speed = speed
        self.color = random.choice(TRAFFIC_COLORS)

    def update(self, road_speed: float):
        self.y += road_speed + self.speed

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x) - self.W // 2, int(self.y) - self.H // 2,
                           self.W, self.H)

    def draw(self, surface):
        r = self.rect()
        pygame.draw.rect(surface, self.color, r, border_radius=5)
        ws = pygame.Rect(r.x + 5, r.y + 8, r.width - 10, 12)
        pygame.draw.rect(surface, (180, 220, 255), ws, border_radius=3)
        for wx, wy in [(r.x - 3, r.y + 5), (r.right - 5, r.y + 5),
                       (r.x - 3, r.bottom - 16), (r.right - 5, r.bottom - 16)]:
            pygame.draw.rect(surface, BLACK, (wx, wy, 8, 11), border_radius=2)


# Coin

COIN_WEIGHTS = [
    (1, GOLD,    14),   # (weight, color, radius)  — common
    (2, ORANGE,  12),
    (3, RED,     10),   # rare
]


class Coin:
    def __init__(self, lane: int, y: float):
        self.lane = lane
        self.x    = float(lane_x(lane))
        self.y    = y
        wt, col, r = random.choices(COIN_WEIGHTS, weights=[6, 3, 1], k=1)[0]
        self.weight = wt
        self.color  = col
        self.radius = r

    def update(self, speed: float):
        self.y += speed

    def rect(self) -> pygame.Rect:
        r = self.radius
        return pygame.Rect(int(self.x) - r, int(self.y) - r, r * 2, r * 2)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 1)
        # Weight label
        if self.weight > 1:
            font = pygame.font.SysFont("consolas", 9, bold=True)
            txt  = font.render(f"x{self.weight}", True, BLACK)
            surface.blit(txt, txt.get_rect(center=(int(self.x), int(self.y))))


# Road obstacle

class Obstacle:
    W = 60
    H = 20

    def __init__(self, lane: int, y: float, obs_type: str):
        self.lane = lane
        self.x    = float(lane_x(lane))
        self.y    = y
        self.type = obs_type
        self.color = OBS_COLORS[obs_type]

    def update(self, speed: float):
        self.y += speed

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x) - self.W // 2, int(self.y) - self.H // 2,
                           self.W, self.H)

    def draw(self, surface):
        r = self.rect()
        pygame.draw.rect(surface, self.color, r, border_radius=4)
        if self.type == OBS_OIL:
            # oil shimmer
            pygame.draw.ellipse(surface, (40, 40, 100), r.inflate(-4, -4))
        elif self.type == OBS_BARRIER:
            pygame.draw.rect(surface, RED, pygame.Rect(r.x, r.y, 8, r.height))
            pygame.draw.rect(surface, WHITE, pygame.Rect(r.right - 8, r.y, 8, r.height))

# Lane hazard zone (slow zone / oil patch — visual wide strip)

class LaneHazard:
    """A semi-transparent coloured strip covering one lane. Slows the player."""
    W = LANE_W - 8
    H = 60

    def __init__(self, lane: int, y: float):
        self.lane = lane
        self.x    = float(ROAD_LEFT + LANE_W * lane + LANE_W // 2)
        self.y    = y

    def update(self, speed: float):
        self.y += speed

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x) - self.W // 2, int(self.y) - self.H // 2,
                           self.W, self.H)

    def draw(self, surface):
        surf = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        surf.fill((80, 40, 0, 120))
        surface.blit(surf, (int(self.x) - self.W // 2, int(self.y) - self.H // 2))
        font = pygame.font.SysFont("consolas", 10)
        txt  = font.render("SLOW", True, ORANGE)
        surface.blit(txt, txt.get_rect(center=(int(self.x), int(self.y))))

# Nitro strip (road event — boost strip)

class NitroStrip:
    """Collecting this gives instant nitro boost."""
    W = ROAD_WIDTH
    H = 14

    def __init__(self, y: float):
        self.x = float(ROAD_LEFT + ROAD_WIDTH // 2)
        self.y = y
        self.collected = False

    def update(self, speed: float):
        self.y += speed

    def rect(self) -> pygame.Rect:
        return pygame.Rect(ROAD_LEFT, int(self.y) - self.H // 2, self.W, self.H)

    def draw(self, surface):
        surf = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        for i in range(self.W):
            frac = i / self.W
            r = int(ORANGE[0] * (1 - frac) + GOLD[0] * frac)
            g = int(ORANGE[1] * (1 - frac) + GOLD[1] * frac)
            b = int(ORANGE[2] * (1 - frac) + GOLD[2] * frac)
            pygame.draw.line(surf, (r, g, b, 180), (i, 0), (i, self.H))
        surface.blit(surf, (ROAD_LEFT, int(self.y) - self.H // 2))


# Power-up item

class PowerUpItem:
    R = 16

    def __init__(self, lane: int, y: float, pu_type: str):
        self.lane    = lane
        self.x       = float(lane_x(lane))
        self.y       = y
        self.type    = pu_type
        self.color   = PU_COLORS[pu_type]
        self.life    = POWERUP_LIFESPAN   # frames remaining on road

    def update(self, speed: float):
        self.y    += speed
        self.life -= 1

    def expired(self) -> bool:
        return self.life <= 0

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x) - self.R, int(self.y) - self.R,
                           self.R * 2, self.R * 2)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.R)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.R, 2)
        font = pygame.font.SysFont("consolas", 9, bold=True)
        label = {"nitro": "N", "shield": "S", "repair": "R"}[self.type]
        txt = font.render(label, True, BLACK)
        surface.blit(txt, txt.get_rect(center=(int(self.x), int(self.y))))


# GameState

class GameState:
    def __init__(self, settings: dict, personal_best: int = 0, coin_sound = None, crash_sound = None):
        self.settings = settings
        self.personal_best = personal_best
        self.coin_sound= coin_sound
        self.crash_sound = crash_sound
        diff_idx      = settings.get("difficulty", 1)
        diff          = DIFFICULTIES[diff_idx]
        self._diff_traffic  = diff[1]
        self._diff_obstacle = diff[2]
        self._diff_speed    = diff[3]

        # Player
        self.player = PlayerCar(settings.get("car_color", [220, 50, 50]))

        # Road
        self.road_speed   = BASE_ROAD_SPEED + self._diff_speed
        self.strips       = [RoadStrip(y) for y in range(-RoadStrip.HEIGHT,
                                                           HEIGHT, RoadStrip.HEIGHT + RoadStrip.GAP)]

        # Entities
        self.traffic:    list[TrafficCar]  = []
        self.coins:      list[Coin]        = []
        self.obstacles:  list[Obstacle]    = []
        self.hazards:    list[LaneHazard]  = []
        self.nitro_strips: list[NitroStrip] = []
        self.powerups:   list[PowerUpItem] = []

        # Timers (countdown in frames)
        self._t_traffic  = TRAFFIC_SPAWN_BASE
        self._t_obstacle = OBSTACLE_SPAWN_BASE
        self._t_coin     = COIN_SPAWN_BASE
        self._t_powerup  = POWERUP_SPAWN_BASE
        self._t_hazard   = HAZARD_SPAWN_BASE
        self._t_nitrostr = 400   # nitro strip event

        # Stats
        self.score     = 0.0
        self.distance  = 0
        self.coins_collected = 0
        self.frame     = 0

        # Active power-up
        self.active_pu:     str | None = None
        self.active_pu_frames: int     = 0

        self.shield_active = False
        self.slowed        = False     # from hazard
        self.slow_frames   = 0

        self.game_over = False

    # Spawn helpers

    def _player_lane(self):
        return self.player.lane

    def _safe_lanes(self) -> list[int]:
        """Lanes not occupied at spawn row (y < 0)."""
        used = {t.lane for t in self.traffic if t.y < 100}
        used |= {o.lane for o in self.obstacles if o.y < 80}
        return [l for l in range(LANES) if l not in used]

    def _spawn_traffic(self):
        safe = self._safe_lanes()
        if not safe:
            return
        lane  = random.choice(safe)
        speed = random.uniform(0.5, 2.5) * self._diff_traffic
        self.traffic.append(TrafficCar(lane, -40, speed))

    def _spawn_coin(self):
        lane = rand_lane()
        self.coins.append(Coin(lane, -20))

    def _spawn_obstacle(self):
        safe = [l for l in range(LANES) if l != self._player_lane()]
        if not safe:
            safe = list(range(LANES))
        lane = random.choice(safe)
        obs_type = random.choice([OBS_BARRIER, OBS_OIL, OBS_POTHOLE])
        self.obstacles.append(Obstacle(lane, -30, obs_type))

    def _spawn_hazard(self):
        lane = rand_lane()
        self.hazards.append(LaneHazard(lane, -40))

    def _spawn_powerup(self):
        if any(isinstance(p, PowerUpItem) for p in self.powerups):
            return   # only one on road
        lane    = rand_lane()
        pu_type = random.choice([PU_NITRO, PU_SHIELD, PU_REPAIR])
        self.powerups.append(PowerUpItem(lane, -30, pu_type))

    def _spawn_nitro_strip(self):
        self.nitro_strips.append(NitroStrip(-20))

    # Power-up activation

    def _activate_powerup(self, pu_type: str):
        # Expire previous
        self._deactivate_powerup()

        self.active_pu = pu_type
        if pu_type == PU_NITRO:
            self.road_speed += 4
            self.active_pu_frames = PU_DURATION[PU_NITRO]
        elif pu_type == PU_SHIELD:
            self.shield_active    = True
            self.active_pu_frames = 0   # until hit
        elif pu_type == PU_REPAIR:
            # Repair clears nearest obstacle ahead of player
            if self.obstacles:
                self.obstacles.sort(key=lambda o: abs(o.y - self.player.y))
                self.obstacles.pop(0)
            self.active_pu        = None
            self.active_pu_frames = 0

    def _deactivate_powerup(self):
        if self.active_pu == PU_NITRO:
            self.road_speed -= 4
        elif self.active_pu == PU_SHIELD:
            self.shield_active = False
        self.active_pu        = None
        self.active_pu_frames = 0

    # Update 

    def handle_key(self, key):
        if key == pygame.K_LEFT  or key == pygame.K_a:
            self.player.move_left()
        if key == pygame.K_RIGHT or key == pygame.K_d:
            self.player.move_right()

    def update(self):
        if self.game_over:
            return

        self.frame += 1

        # Difficulty scaling
        self.road_speed += SPEED_INCREMENT * self._diff_traffic
        spawn_mult = max(0.4, 1.0 - self.frame * 0.00015)  # intervals shrink over time

        # Active power-up timer
        if self.active_pu == PU_NITRO:
            self.active_pu_frames -= 1
            if self.active_pu_frames <= 0:
                self._deactivate_powerup()

        # Slow from hazard
        if self.slowed:
            self.slow_frames -= 1
            if self.slow_frames <= 0:
                self.slowed = False

        effective_speed = self.road_speed * (0.5 if self.slowed else 1.0)

        # Road strips
        for s in self.strips:
            s.update(effective_speed)
        self.strips = [s for s in self.strips if s.y < HEIGHT + RoadStrip.HEIGHT]
        if not self.strips or self.strips[-1].y > RoadStrip.HEIGHT + RoadStrip.GAP:
            last_y = min(s.y for s in self.strips) if self.strips else 0
            self.strips.append(RoadStrip(last_y - RoadStrip.HEIGHT - RoadStrip.GAP))

        # Spawn timers
        self._t_traffic -= 1
        if self._t_traffic <= 0:
            self._spawn_traffic()
            self._t_traffic = int(TRAFFIC_SPAWN_BASE * spawn_mult / self._diff_traffic)

        self._t_coin -= 1
        if self._t_coin <= 0:
            self._spawn_coin()
            self._t_coin = int(COIN_SPAWN_BASE * spawn_mult)

        self._t_obstacle -= 1
        if self._t_obstacle <= 0:
            self._spawn_obstacle()
            self._t_obstacle = int(OBSTACLE_SPAWN_BASE * spawn_mult / self._diff_obstacle)

        self._t_hazard -= 1
        if self._t_hazard <= 0:
            self._spawn_hazard()
            self._t_hazard = int(HAZARD_SPAWN_BASE * spawn_mult)

        self._t_powerup -= 1
        if self._t_powerup <= 0:
            self._spawn_powerup()
            self._t_powerup = POWERUP_SPAWN_BASE

        self._t_nitrostr -= 1
        if self._t_nitrostr <= 0:
            self._spawn_nitro_strip()
            self._t_nitrostr = random.randint(350, 600)

        # Move entities
        for t in self.traffic:      t.update(effective_speed)
        for c in self.coins:        c.update(effective_speed)
        for o in self.obstacles:    o.update(effective_speed)
        for h in self.hazards:      h.update(effective_speed)
        for p in self.powerups:     p.update(effective_speed)
        for n in self.nitro_strips: n.update(effective_speed)

        # Cull off-screen
        self.traffic      = [t for t in self.traffic      if t.y < HEIGHT + 80]
        self.coins        = [c for c in self.coins        if c.y < HEIGHT + 30]
        self.obstacles    = [o for o in self.obstacles    if o.y < HEIGHT + 30]
        self.hazards      = [h for h in self.hazards      if h.y < HEIGHT + 80]
        self.powerups     = [p for p in self.powerups     if p.y < HEIGHT + 30 and not p.expired()]
        self.nitro_strips = [n for n in self.nitro_strips if n.y < HEIGHT + 20]

        pr = self.player.rect()
        self.player.update()

        #   Coin collection
        eaten = [c for c in self.coins if pr.colliderect(c.rect())]
        for c in eaten:
            if self.coin_sound and self.settings.get("sound", True):
                self.coin_sound.play()
            self.coins.remove(c)
            pts = SCORE_PER_COIN * c.weight
            self.score          += pts
            self.coins_collected += 1

        # Power-up collection 
        collected_pu = [p for p in self.powerups if pr.colliderect(p.rect())]
        for p in collected_pu:
            self.powerups.remove(p)
            self._activate_powerup(p.type)

        #  Nitro strip collection 
        for n in self.nitro_strips:
            if not n.collected and pr.colliderect(n.rect()):
                n.collected = True
                self._activate_powerup(PU_NITRO)
        self.nitro_strips = [n for n in self.nitro_strips if not n.collected]

        # Hazard slow 
        for h in self.hazards:
            if pr.colliderect(h.rect()):
                self.slowed      = True
                self.slow_frames = FPS * 2

        #  Traffic collision 
        for t in self.traffic:
            if pr.colliderect(t.rect()):
                if self.shield_active:
                    self.shield_active = False
                    self.active_pu     = None
                    self.traffic.remove(t)
                    break
                else:
                    if self.crash_sound and self.settings.get("sound", True):
                        self.crash_sound.play()
                    self.game_over = True
                    return

        # Obstacle collision 
        for o in self.obstacles:
            if pr.colliderect(o.rect()):
                if self.shield_active:
                    self.shield_active = False
                    self.active_pu     = None
                    self.obstacles.remove(o)
                    break
                else:
                    self.game_over = True
                    return

        #  Distance & score 
        self.distance += 1
        self.score    += SCORE_PER_FRAME

    # Draw 

    def draw(self, surface):
        surface.fill(DARK_BG)

        # Grass
        pygame.draw.rect(surface, GRASS_L, (0, 0, ROAD_LEFT, HEIGHT))
        pygame.draw.rect(surface, GRASS_R, (ROAD_RIGHT, 0, WIDTH - ROAD_RIGHT, HEIGHT))

        # Road
        pygame.draw.rect(surface, ROAD_DARK, (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))

        # Road strips
        for s in self.strips:
            s.draw(surface)

        # Hazards
        for h in self.hazards:
            h.draw(surface)

        # Nitro strips
        for n in self.nitro_strips:
            n.draw(surface)

        # Coins
        for c in self.coins:
            c.draw(surface)

        # Obstacles
        for o in self.obstacles:
            o.draw(surface)

        # Power-ups
        for p in self.powerups:
            p.draw(surface)

        # Traffic
        for t in self.traffic:
            t.draw(surface)

        # Player
        self.player.draw(surface, self.shield_active)

        # Road borders
        pygame.draw.rect(surface, WHITE, (ROAD_LEFT - 3, 0, 3, HEIGHT))
        pygame.draw.rect(surface, WHITE, (ROAD_RIGHT, 0, 3, HEIGHT))

    def draw_hud(self, surface, font_sm, font_xs):
        # Top bar
        pygame.draw.rect(surface, (10, 10, 20), (0, 0, WIDTH, 38))

        def txt(text, color, x, y, anchor="topleft"):
            s = font_sm.render(text, True, color)
            r = s.get_rect()
            setattr(r, anchor, (x, y))
            surface.blit(s, r)

        txt(f"Score: {int(self.score)}", WHITE, 8, 8)
        txt(f"Coins: {self.coins_collected}", GOLD, WIDTH // 2, 8, anchor="midtop")
        dist_km = self.distance // 60
        txt(f"Dist: {dist_km}m", CYAN, WIDTH - 8, 8, anchor="topright")

        # Active power-up
        if self.active_pu:
            label = PU_LABELS.get(self.active_pu, self.active_pu)
            if self.active_pu == PU_NITRO:
                remaining = self.active_pu_frames / FPS
                label += f"  {remaining:.1f}s"
            s = font_xs.render(label, True, PU_COLORS.get(self.active_pu, WHITE))
            surface.blit(s, (8, HEIGHT - 24))

        if self.slowed:
            s = font_xs.render("SLOWED", True, ORANGE)
            surface.blit(s, (WIDTH - s.get_width() - 8, HEIGHT - 24))