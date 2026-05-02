
import pygame
import random
import json
import os
from config import *


# Settings helpers

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")

DEFAULT_SETTINGS = {
    "snake_color": list(GREEN),
    "grid_overlay": True,
    "sound": False,
}


def load_settings() -> dict:
    try:
        with open(SETTINGS_PATH, "r") as f:
            data = json.load(f)
        # Merge with defaults to handle missing keys
        merged = dict(DEFAULT_SETTINGS)
        merged.update(data)
        return merged
    except Exception:
        return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict):
    try:
        with open(SETTINGS_PATH, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"[Settings] save error: {e}")


# Direction constants


UP    = ( 0, -1)
DOWN  = ( 0,  1)
LEFT  = (-1,  0)
RIGHT = ( 1,  0)

OPPOSITES = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


# Snake

class Snake:
    def __init__(self, color):
        start = (COLS // 2, ROWS // 2)
        self.body = [start, (start[0] - 1, start[1]), (start[0] - 2, start[1])]
        self.direction = RIGHT
        self.next_dir   = RIGHT
        self.grow_count = 0
        self.color      = tuple(color)

    # Direction
    def set_direction(self, new_dir):
        if new_dir != OPPOSITES.get(self.direction):
            self.next_dir = new_dir

    def apply_direction(self):
        self.direction = self.next_dir

    # Movement 
    def move(self):
        self.apply_direction()
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        self.body.insert(0, new_head)
        if self.grow_count > 0:
            self.grow_count -= 1
        else:
            self.body.pop()

    def grow(self, amount=1):
        self.grow_count += amount

    def shorten(self, amount):
        """Remove *amount* tail segments. Returns True if still alive."""
        for _ in range(amount):
            if len(self.body) > 1:
                self.body.pop()
        return len(self.body) > POISON_MIN_LENGTH

    # Collision queries
    def head(self):
        return self.body[0]

    def hits_wall(self):
        x, y = self.body[0]
        return not (0 <= x < COLS and 0 <= y < ROWS)

    def hits_self(self):
        return self.body[0] in self.body[1:]

    def hits_obstacle(self, obstacles: set):
        return self.body[0] in obstacles

    # Drawing 
    def draw(self, surface):
        for i, (cx, cy) in enumerate(self.body):
            rect = pygame.Rect(cx * CELL_SIZE, cy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = self.color if i > 0 else tuple(min(c + 60, 255) for c in self.color)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, DARK_BG, rect, 1)


# Food item

class FoodItem:
    def __init__(self, pos, food_type, has_timer=False):
        self.pos = pos
        self.type = food_type
        self.points = FOOD_POINTS[food_type]
        self.color = FOOD_COLORS[food_type]
        self.spawn_ms = pygame.time.get_ticks()
        self.has_timer = has_timer         # whether it expires

    def is_expired(self):
        if not self.has_timer:
            return False
        return pygame.time.get_ticks() - self.spawn_ms > FOOD_DISAPPEAR_MS

    def time_left_frac(self):
        """Fraction of lifetime remaining (0–1). Only meaningful when has_timer."""
        elapsed = pygame.time.get_ticks() - self.spawn_ms
        return max(0.0, 1.0 - elapsed / FOOD_DISAPPEAR_MS)

    def draw(self, surface):
        cx, cy = self.pos
        rect = pygame.Rect(cx * CELL_SIZE + 2, cy * CELL_SIZE + 2,
                           CELL_SIZE - 4, CELL_SIZE - 4)
        pygame.draw.ellipse(surface, self.color, rect)

        # Dim timed food as timer runs out
        if self.has_timer:
            frac = self.time_left_frac()
            overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            alpha = int((1 - frac) * 180)
            overlay.fill((0, 0, 0, alpha))
            surface.blit(overlay, (cx * CELL_SIZE, cy * CELL_SIZE))


# Power-up item

class PowerUp:
    def __init__(self, pos, pu_type):
        self.pos = pos
        self.type = pu_type
        self.color = PU_COLORS[pu_type]
        self.spawn_ms = pygame.time.get_ticks()

    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_ms > POWERUP_LIFESPAN_MS

    def draw(self, surface):
        cx, cy = self.pos
        center = (cx * CELL_SIZE + CELL_SIZE // 2, cy * CELL_SIZE + CELL_SIZE // 2)
        radius = CELL_SIZE // 2 - 2
        pygame.draw.circle(surface, self.color, center, radius)
        pygame.draw.circle(surface, WHITE, center, radius, 2)


# GameState

class GameState:
    """
    Holds and updates all mutable game state.
    Call .update() each logical tick; call .draw() each frame.
    """
    def __init__(self, settings: dict, personal_best: int = 0):
        self.eat_sound = None
        self.game_over_sound = None
        self.powerup_sound = None
        self.settings      = settings
        self.personal_best = personal_best
        self.field_powerup = None
        # Snake
        self.snake = Snake(settings["snake_color"])

        # Score / level
        self.score         = 0
        self.level         = 1
        self.food_eaten    = 0       # counter toward next level

        # Obstacles (grid cells, as (col, row) tuples)
        self.obstacles: set[tuple] = set()

        # Food list
        self.foods: list[FoodItem] = []
        self._spawn_food()
        self._maybe_spawn_poison()

        # Power-up on field
        self.field_powerup: PowerUp | None = None
        self._next_powerup_at = pygame.time.get_ticks() + random.randint(5000, 12000)

        # Active power-up effect
        self.active_pu: str | None = None
        self.active_pu_end: int    = 0

        # Shield: absorbs ONE collision
        self.shield_active = False

        # Speed
        self.current_speed = INITIAL_SPEED

        # Game-over flag
        self.game_over = False

        # Personal best
        self.new_best = False

    # Internal helpers

    def _occupied_cells(self) -> set:
        occupied = set(self.snake.body) | self.obstacles
        occupied |= {f.pos for f in self.foods}
        if self.field_powerup:
            occupied.add(self.field_powerup.pos)
        return occupied

    def _random_free_cell(self):
        occupied = self._occupied_cells()
        free = [
            (c, r)
            for c in range(COLS)
            for r in range(ROWS)
            if (c, r) not in occupied
        ]
        return random.choice(free) if free else None

    def _spawn_food(self):
        """Ensure at least one non-poison food exists."""
        types  = [FOOD_NORMAL, FOOD_BONUS, FOOD_TIMED]
        weights = [6, 2, 2]
        food_type = random.choices(types, weights=weights, k=1)[0]
        has_timer = (food_type == FOOD_TIMED)
        pos = self._random_free_cell()
        if pos:
            self.foods.append(FoodItem(pos, food_type, has_timer))

    def _maybe_spawn_poison(self):
        """20 % chance to spawn a poison food if none exists."""
        has_poison = any(f.type == FOOD_POISON for f in self.foods)
        if not has_poison and random.random() < 0.20:
            pos = self._random_free_cell()
            if pos:
                self.foods.append(FoodItem(pos, FOOD_POISON))

    def _place_obstacles(self):
        """Add obstacle blocks for the current level (level ≥ 3)."""
        count = OBSTACLES_PER_LEVEL
        head  = self.snake.head()
        attempts = 0
        placed = 0
        while placed < count and attempts < 500:
            attempts += 1
            c = random.randint(1, COLS - 2)
            r = random.randint(1, ROWS - 2)
            cell = (c, r)
            # Don't place on snake, food, power-up, or too close to head
            if cell in self._occupied_cells():
                continue
            if abs(c - head[0]) < 4 and abs(r - head[1]) < 4:
                continue
            self.obstacles.add(cell)
            placed += 1

    def _advance_level(self):
        self.level      += 1
        self.food_eaten  = 0
        self.current_speed = INITIAL_SPEED + (self.level - 1) * SPEED_INCREMENT
        if self.level >= OBSTACLES_FROM_LVL:
            self._place_obstacles()

    def _apply_powerup(self, pu_type: str):
        self.active_pu     = pu_type
        self.active_pu_end = pygame.time.get_ticks() + POWERUP_EFFECT_MS
        if pu_type == PU_SPEED_BOOST:
            self.current_speed += 4
        elif pu_type == PU_SLOW_MOTION:
            self.current_speed = max(2, self.current_speed - 4)
        elif pu_type == PU_SHIELD:
            self.shield_active = True

    def _expire_powerup(self):
        if self.active_pu == PU_SPEED_BOOST:
            self.current_speed -= 4
        elif self.active_pu == PU_SLOW_MOTION:
            self.current_speed += 4
        elif self.active_pu == PU_SHIELD:
            self.shield_active = False
        self.active_pu = None

    # Public interface

    def handle_key(self, key):
        mapping = {
            pygame.K_UP: UP,    pygame.K_w: UP,
            pygame.K_DOWN: DOWN, pygame.K_s: DOWN,
            pygame.K_LEFT: LEFT, pygame.K_a: LEFT,
            pygame.K_RIGHT: RIGHT, pygame.K_d: RIGHT,
        }
        if key in mapping:
            self.snake.set_direction(mapping[key])

    def update(self):
        """Advance one game-logic tick. Call at current_speed Hz."""
        if self.game_over:
            return

        now = pygame.time.get_ticks()

        # Expire active power-up effect
        if self.active_pu and now > self.active_pu_end:
            self._expire_powerup()

        # Spawn / expire field power-up
        if self.field_powerup and self.field_powerup.is_expired():
            self.field_powerup = None
        if not self.field_powerup and now >= self._next_powerup_at:
            pos = self._random_free_cell()
            if pos:
                pu_type = random.choice([PU_SPEED_BOOST, PU_SLOW_MOTION, PU_SHIELD])
                self.field_powerup = PowerUp(pos, pu_type)
            self._next_powerup_at = now + random.randint(8000, 18000)

        # Expire timed food
        self.foods = [f for f in self.foods if not f.is_expired()]
        # Ensure at least one edible food
        if not any(f.type != FOOD_POISON for f in self.foods):
            self._spawn_food()

        # Move snake
        self.snake.move()
        head = self.snake.head()

        # Wall collision
        if self.snake.hits_wall():
            if self.shield_active:
                self.shield_active = False
                self.active_pu = None
                # Wrap instead of die
                head = (head[0] % COLS, head[1] % ROWS)
                self.snake.body[0] = head
            else:
                self.game_over = True
                return

        # Self collision
        if self.snake.hits_self():
            if self.shield_active:
                self.shield_active = False
                self.active_pu = None
            else:
                self.game_over = True
                return

        # Obstacle collision
        if self.snake.hits_obstacle(self.obstacles):
            if self.shield_active:
                self.shield_active = False
                self.active_pu = None
            else:
                self.game_over = True
                return

        # Food collision
        eaten = [f for f in self.foods if f.pos == head]
        if eaten and self.settings["sound"] and self.eat_sound:
            self.eat_sound.play()
        for food in eaten:
            self.foods.remove(food)
            if food.type == FOOD_POISON:
                alive = self.snake.shorten(POISON_SHORTEN)
                if not alive:
                    self.game_over = True
                    return
            else:
                self.score     += food.points * self.level
                self.food_eaten += 1
                self.snake.grow()
                if self.food_eaten >= FOOD_PER_LEVEL:
                    self._advance_level()
            # Possibly spawn poison after eating
            self._maybe_spawn_poison()
            # Always replenish normal food
            if food.type != FOOD_POISON:
                self._spawn_food()

        # Power-up collection
        if self.field_powerup and self.field_powerup.pos == head:
            self._apply_powerup(self.field_powerup.type)
            self.field_powerup = None

        # Personal best check
        if self.score > self.personal_best:
            self.personal_best = self.score
            self.new_best = True

    # Drawing

    def draw(self, surface):
        surface.fill(DARK_BG)

        # Grid overlay
        if self.settings.get("grid_overlay", True):
            for c in range(COLS):
                for r in range(ROWS):
                    rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(surface, GRID_COLOR, rect, 1)

        # Obstacles
        for (c, r) in self.obstacles:
            rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, WALL_COLOR, rect)
            pygame.draw.rect(surface, DARK_BG, rect, 2)

        # Food
        for food in self.foods:
            food.draw(surface)

        # Power-up on field
        if self.field_powerup:
            self.field_powerup.draw(surface)

        # Snake
        self.snake.draw(surface)

        # Shield glow around head
        if self.shield_active:
            hx, hy = self.snake.head()
            cx = hx * CELL_SIZE + CELL_SIZE // 2
            cy = hy * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(surface, PURPLE, (cx, cy), CELL_SIZE, 2)

    def draw_hud(self, surface, font_sm, font_md):
        """Draw HUD overlay (score, level, personal best, active power-up)."""
        # Background strip at top
        hud_rect = pygame.Rect(0, 0, WINDOW_WIDTH, 40)
        pygame.draw.rect(surface, (10, 10, 20), hud_rect)

        texts = [
            (f"Score: {self.score}", WHITE, 10),
            (f"Level: {self.level}", GOLD, 180),
            (f"Best: {self.personal_best}", CYAN if not self.new_best else GOLD, 350),
            (f"Length: {len(self.snake.body)}", LIGHT_GRAY, 530),
        ]
        for text, color, x in texts:
            surf = font_sm.render(text, True, color)
            surface.blit(surf, (x, 10))

        # Active power-up indicator
        if self.active_pu:
            now = pygame.time.get_ticks()
            remaining = max(0, self.active_pu_end - now) / 1000
            label = PU_LABELS.get(self.active_pu, self.active_pu)
            pu_text = f"{label}  {remaining:.1f}s"
            surf = font_sm.render(pu_text, True, PU_COLORS[self.active_pu])
            surface.blit(surf, (WINDOW_WIDTH - surf.get_width() - 10, 10))