import pygame as p
import random
import time
import math

# --- Setup ---
p.init()
WIDTH, HEIGHT = 600, 600
screen = p.display.set_mode((WIDTH, HEIGHT))
p.display.set_caption("Realistic Snake Pro")
clock = p.time.Clock()
font = p.font.SysFont("Segoe UI", 25, bold=True)

# Colors
BG_COLOR = (20, 25, 30)
GRID_COLOR = (30, 35, 40)
SNAKE_HEAD = (0, 255, 150)
SNAKE_BODY = (0, 150, 100)
WALL_COLOR = (60, 70, 80)

CELL_SIZE = 25
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

class Food:
    def __init__(self):
        self.spawn()

    def spawn(self):
        # 1. Random Weight (Higher weight = Bigger/Rarer)
        self.weight = random.choices([1, 3, 5], weights=[70, 20, 10])[0]
        
        # 2. Appearance based on weight
        if self.weight == 1: self.color = (100, 255, 100) # Green
        elif self.weight == 3: self.color = (255, 100, 100) # Red
        else: self.color = (255, 200, 0) # Gold
            
        # 3. Position (avoiding the very edges for aesthetics)
        self.x = random.randint(1, GRID_WIDTH - 2) * CELL_SIZE
        self.y = random.randint(1, GRID_HEIGHT - 2) * CELL_SIZE
        
        # 4. Expiration Timer (5 to 12 seconds)
        self.spawn_time = time.time()
        self.lifetime = random.randint(5, 12)

    def draw(self, surf):
        elapsed = time.time() - self.spawn_time
        remaining = max(0, self.lifetime - elapsed)
        
        # Calculate pulse effect
        pulse = math.sin(time.time() * 10) * 2
        radius = (CELL_SIZE // 2) - 2 + pulse
        
        # Draw Glow/Shadow
        p.draw.circle(surf, (50, 50, 50), (self.x + CELL_SIZE//2, self.y + CELL_SIZE//2), radius + 2)
        
        # Draw Main Food (Circle is more realistic than square)
        p.draw.circle(surf, self.color, (self.x + CELL_SIZE//2, self.y + CELL_SIZE//2), radius)
        
        # Draw Timer Ring
        angle = (remaining / self.lifetime) * 360
        if angle > 0:
            rect = p.Rect(self.x - 2, self.y - 2, CELL_SIZE + 4, CELL_SIZE + 4)
            p.draw.arc(surf, (255, 255, 255), rect, 0, math.radians(angle), 2)

# --- Initial State ---
snake = [[5 * CELL_SIZE, 5 * CELL_SIZE], [4 * CELL_SIZE, 5 * CELL_SIZE], [3 * CELL_SIZE, 5 * CELL_SIZE]]
direction = "RIGHT"
change_to = direction
score = 0
food = Food()
running = True

def draw_background():
    screen.fill(BG_COLOR)
    # Draw subtle grid lines
    for x in range(0, WIDTH, CELL_SIZE):
        p.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        p.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))
    # Draw Border Walls
    p.draw.rect(screen, WALL_COLOR, (0, 0, WIDTH, HEIGHT), CELL_SIZE // 2)

while running:
    # 1. Input Handling
    for event in p.event.get():
        if event.type == p.QUIT:
            running = False
        if event.type == p.KEYDOWN:
            if event.key == p.K_UP and direction != "DOWN": change_to = "UP"
            if event.key == p.K_DOWN and direction != "UP": change_to = "DOWN"
            if event.key == p.K_LEFT and direction != "RIGHT": change_to = "LEFT"
            if event.key == p.K_RIGHT and direction != "LEFT": change_to = "RIGHT"

    direction = change_to

    # 2. Movement
    head = list(snake[0])
    if direction == "UP": head[1] -= CELL_SIZE
    if direction == "DOWN": head[1] += CELL_SIZE
    if direction == "LEFT": head[0] -= CELL_SIZE
    if direction == "RIGHT": head[0] += CELL_SIZE
    
    snake.insert(0, head)

    # 3. Game Logic
    # Eating Food
    if head[0] == food.x and head[1] == food.y:
        score += food.weight
        food.spawn()
    else:
        snake.pop() # Remove tail if no food eaten

    # Food Expiration
    if time.time() - food.spawn_time > food.lifetime:
        food.spawn()

    # Death Conditions
    if head[0] < CELL_SIZE//2 or head[0] > WIDTH - CELL_SIZE or \
       head[1] < CELL_SIZE//2 or head[1] > HEIGHT - CELL_SIZE or \
       head in snake[1:]:
        running = False

    # 4. Rendering
    draw_background()
    food.draw(screen)
    
    # Draw Snake with Gradient/Rounded corners
    for i, part in enumerate(snake):
        color = SNAKE_HEAD if i == 0 else SNAKE_BODY
        # Make the tail slightly smaller
        padding = min(i, 5) 
        rect = p.Rect(part[0] + padding, part[1] + padding, CELL_SIZE - (padding*2), CELL_SIZE - (padding*2))
        p.draw.rect(screen, color, rect, border_radius=5)

    # UI
    score_surf = font.render(f"SCORE: {score}", True, (255, 255, 255))
    screen.blit(score_surf, (30, 30))

    p.display.flip()
    clock.tick(10 + (score // 10)) # Speed ramps up with score

p.quit()