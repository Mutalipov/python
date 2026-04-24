import pygame as p
import random

p.init()

# window setup
icon = p.image.load("images/racer.png")
WIDTH, HEIGHT = 400, 600
screen = p.display.set_mode((WIDTH, HEIGHT))
p.display.set_caption("Racer Game")
p.display.set_icon(icon)
clock = p.time.Clock()

#  Global Variables
SPEED = 5
TOTAL_SCORE = 0    # Sum of weights
COIN_COUNT = 0     # Number of coins picked up
N = 5              # Increase speed every N coins collected

player_img = p.transform.scale(p.image.load("images/player.png").convert_alpha(), (45, 90))
enemy_img = p.transform.scale(p.image.load("images/enemy.png").convert_alpha(), (45, 90))
coin_img = p.transform.scale(p.image.load("images/coin.png").convert_alpha(), (30, 30))

def draw_road(surface, y_offset):
    surface.fill((34, 139, 34)) # Grass
    p.draw.rect(surface, (50, 50, 50), (50, 0, 300, HEIGHT)) # Asphalt
    p.draw.line(surface, (255, 255, 255), (55, 0), (55, HEIGHT), 5) # Border
    p.draw.line(surface, (255, 255, 255), (345, 0), (345, HEIGHT), 5) # Border
    
    # Scrolling Dashed Lines
    for i in range(-100, HEIGHT + 100, 80):
        p.draw.rect(surface, (255, 255, 255), (WIDTH//2 - 2, i + y_offset, 4, 40))

class Enemy(p.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(60, 340), -100)

    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > HEIGHT:
            self.rect.top = -100
            self.rect.center = (random.randint(60, 340), -100)

class Coin(p.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = coin_img
        self.rect = self.image.get_rect()
        self.spawn()

    def spawn(self):
        self.weight = random.randint(1, 5) 
        self.rect.top = -100
        self.rect.center = (random.randint(60, 340), -100)

    def move(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > HEIGHT:
            self.spawn()

class Player(p.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.center = (200, 500)

    def move(self):
        keys = p.key.get_pressed()
        if keys[p.K_LEFT] and self.rect.left > 60:
            self.rect.move_ip(-5, 0)
        if keys[p.K_RIGHT] and self.rect.right < 340:
            self.rect.move_ip(5, 0)

# Initialize
P1 = Player()
E1 = Enemy()
C1 = Coin()

enemies = p.sprite.Group(E1)
coins = p.sprite.Group(C1)
all_sprites = p.sprite.Group(P1, E1, C1)

road_step = 0
running = True

while running:
    for event in p.event.get():
        if event.type == p.QUIT:
            running = False

    # Road Animation
    road_step = (road_step + SPEED) % 80
    draw_road(screen, road_step)

    # Move Entities
    for entity in all_sprites:
        screen.blit(entity.image, entity.rect)
        entity.move()

    # --- TWO COUNTS LOGIC ---
    coin_hit = p.sprite.spritecollideany(P1, coins)
    if coin_hit:
        # 1. Update Coin Count
        COIN_COUNT += 1
        
        # 2. Update Score
        TOTAL_SCORE += coin_hit.weight
        
        # Increase speed based on number of coins, not weight
        if COIN_COUNT % N == 0:
            SPEED += 1
            
        coin_hit.spawn()

    # UI Rendering
    font = p.font.SysFont("Arial", 20, bold=True)
    score_surf = font.render(f"Score: {TOTAL_SCORE}", True, (255, 255, 255))
    count_surf = font.render(f"Coins: {COIN_COUNT}", True, (255, 255, 0))
    screen.blit(score_surf, (10, 10))
    screen.blit(count_surf, (10, 35))

    # Enemy Collision
    if p.sprite.spritecollideany(P1, enemies):
        running = False

    p.display.update()
    clock.tick(60)

p.quit()