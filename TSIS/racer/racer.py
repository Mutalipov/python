import pygame as p
import random
import json
import os

# --- Initialization ---
p.init()
WIDTH, HEIGHT = 400, 600
screen = p.display.set_mode((WIDTH, HEIGHT))
p.display.set_caption("Racer TSIS")
clock = p.time.Clock()

# Fonts
font = p.font.SysFont("Arial", 18, bold=True)
big_font = p.font.SysFont("Arial", 35, bold=True)

# --- Data Handling ---
def load_data(file, default):
    if not os.path.exists(file): return default
    try:
        with open(file, 'r') as f:
            data = json.load(f)
            for key in default:
                if key not in data: data[key] = default[key]
            return data
    except: return default

def save_data(file, data):
    with open(file, 'w') as f: json.dump(data, f, indent=4)

# Load global settings and scores
settings = load_data("settings.json", {"car_index": 0, "sound": True, "difficulty": "Medium"})
leaderboard = load_data("leaderboard.json", [])
DIFF_LEVELS = ["Easy", "Medium", "Hard"]

# --- Asset Loading ---
def get_img(path, size):
    try: return p.transform.scale(p.image.load(path).convert_alpha(), size)
    except:
        surf = p.Surface(size); surf.fill((random.randint(50,200), 50, 200))
        return surf

car_options = [get_img("images/player_1.png", (45, 90)), get_img("images/player_2.png", (45, 90))]
enemy_img = get_img("images/enemy.png", (45, 90))
coin_img = get_img("images/coin.png", (30, 30))
nitro_img = get_img("images/nitro.png", (30, 30))
shield_img = get_img("images/shield.png", (30, 30))
repair_img = get_img("images/repair.png", (30, 30))
road_img = get_img("images/road.png", (WIDTH, HEIGHT))

# --- Classes ---

class Player(p.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = car_options[settings["car_index"]]
        self.rect = self.image.get_rect(center=(200, 500))
        self.shield_on = False

    def move(self):
        keys = p.key.get_pressed()
        if keys[p.K_LEFT] and self.rect.left > 55: self.rect.move_ip(-6, 0)
        if keys[p.K_RIGHT] and self.rect.right < 345: self.rect.move_ip(6, 0)

class Enemy(p.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.spawn()

    def spawn(self):
        self.rect.center = (random.randint(70, 330), random.randint(-900, -100))

    def update(self, speed):
        self.rect.y += speed
        if self.rect.top > HEIGHT: self.spawn()

class Obstacle(p.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = p.Surface((45, 25))
        self.image.fill((70, 70, 70)) # Oil/Pothole
        self.rect = self.image.get_rect(center=(random.randint(70, 330), -100))

    def update(self, speed):
        self.rect.y += speed
        if self.rect.top > HEIGHT: self.kill()

class PowerUp(p.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = random.choices(["Nitro", "Shield", "Repair"], weights=[40, 30, 30])[0]
        imgs = {"Nitro": nitro_img, "Shield": shield_img, "Repair": repair_img}
        self.image = imgs[self.type]
        self.rect = self.image.get_rect(center=(random.randint(70, 330), -100))

    def update(self, speed):
        self.rect.y += speed
        if self.rect.top > HEIGHT: self.kill()

class Coin(p.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = coin_img
        self.weight = random.randint(1, 5)
        self.rect = self.image.get_rect(center=(random.randint(70, 330), -50))

    def update(self, speed):
        self.rect.y += speed
        if self.rect.top > HEIGHT: self.kill()

# --- Helpers ---
def draw_text(t, pos, color=(255, 255, 255), center=False):
    surf = font.render(t, True, color)
    rect = surf.get_rect(topleft=pos)
    if center: rect.centerx = WIDTH // 2
    screen.blit(surf, rect)

# --- Screen Logic ---

def settings_screen():
    global settings
    while True:
        screen.fill((40, 40, 40))
        draw_text("GARAGE & SETTINGS", (0, 50), center=True)
        screen.blit(car_options[settings["car_index"]], (WIDTH//2 - 22, 110))
        
        btns = [
            (f"CAR: {settings['car_index']+1}", p.Rect(100, 220, 200, 40), (0, 150, 255)),
            (f"SOUND: {'ON' if settings['sound'] else 'OFF'}", p.Rect(100, 280, 200, 40), (0, 200, 100)),
            (f"DIFF: {settings['difficulty']}", p.Rect(100, 340, 200, 40), (200, 150, 0)),
            ("SAVE & BACK", p.Rect(100, 450, 200, 50), (255, 255, 255))
        ]

        for txt, rect, col in btns:
            p.draw.rect(screen, col, rect)
            t_surf = font.render(txt, True, (0,0,0) if col == (255,255,255) else (255,255,255))
            screen.blit(t_surf, t_surf.get_rect(center=rect.center))

        for event in p.event.get():
            if event.type == p.QUIT: return "QUIT"
            if event.type == p.MOUSEBUTTONDOWN:
                if btns[0][1].collidepoint(event.pos): settings["car_index"] = (settings["car_index"] + 1) % len(car_options)
                if btns[1][1].collidepoint(event.pos): settings["sound"] = not settings["sound"]
                if btns[2][1].collidepoint(event.pos): 
                    idx = (DIFF_LEVELS.index(settings["difficulty"]) + 1) % 3
                    settings["difficulty"] = DIFF_LEVELS[idx]
                if btns[3][1].collidepoint(event.pos):
                    save_data("settings.json", settings)
                    return "MENU"
        p.display.update()

def leaderboard_screen():
    while True:
        screen.fill((20, 20, 20))
        draw_text("TOP 10 SCORES", (0, 50), (255, 215, 0), center=True)
        top_10 = sorted(leaderboard, key=lambda x: x['score'], reverse=True)[:10]
        for i, entry in enumerate(top_10):
            draw_text(f"{i+1}. {entry['name']} - {entry['score']}", (80, 120 + i*35))
        
        back_btn = p.Rect(100, 500, 200, 40)
        p.draw.rect(screen, (100, 100, 100), back_btn)
        draw_text("BACK", (0, 510), center=True)

        for event in p.event.get():
            if event.type == p.QUIT: return "QUIT"
            if event.type == p.MOUSEBUTTONDOWN and back_btn.collidepoint(event.pos): return "MENU"
        p.display.update()

def gameplay(username):
    base_v = {"Easy": 4, "Medium": 6, "Hard": 9}
    SPEED = base_v[settings["difficulty"]]
    SCORE, COINS, DISTANCE = 0, 0, 0
    nitro_end, road_y = 0, 0
    msg, msg_timer = "", 0
    
    player = Player()
    enemies = p.sprite.Group(Enemy(), Enemy())
    coins_grp = p.sprite.Group()
    hazards = p.sprite.Group()
    powerups = p.sprite.Group()

    while True:
        ticks = p.time.get_ticks()
        cur_speed = SPEED + 10 if ticks < nitro_end else SPEED
        road_y = (road_y + cur_speed) % HEIGHT
        screen.blit(road_img, (0, road_y)); screen.blit(road_img, (0, road_y - HEIGHT))

        for event in p.event.get():
            if event.type == p.QUIT: return "QUIT"

        player.move()
        enemies.update(cur_speed); hazards.update(cur_speed); powerups.update(cur_speed); coins_grp.update(cur_speed)
        DISTANCE += cur_speed / 20

        # Spawning Logic
        if random.randint(1, 100) == 1: hazards.add(Obstacle())
        if random.randint(1, 350) == 1: powerups.add(PowerUp())
        if len(coins_grp) < 3: coins_grp.add(Coin())
        if len(enemies) < 2 + (int(DISTANCE)//2000): enemies.add(Enemy())

        # Collisions
        if p.sprite.spritecollideany(player, coins_grp):
            for c in p.sprite.spritecollide(player, coins_grp, True):
                COINS += 1; SCORE += c.weight
                if COINS % 5 == 0: SPEED += 1

        p_hit = p.sprite.spritecollideany(player, powerups)
        if p_hit:
            if p_hit.type == "Nitro": nitro_end = ticks + 5000; msg = "NITRO BOOST!"
            elif p_hit.type == "Shield": player.shield_on = True; msg = "SHIELD EQUIPPED!"
            elif p_hit.type == "Repair": SCORE += 1000; msg = "REPAIRED +1000"
            msg_timer = 90; p_hit.kill()

        crash = p.sprite.spritecollideany(player, enemies) or p.sprite.spritecollideany(player, hazards)
        if crash:
            if player.shield_on:
                player.shield_on = False; msg = "SHIELD BROKEN!"; msg_timer = 60
                if isinstance(crash, Enemy): crash.spawn()
                else: crash.kill()
            else:
                leaderboard.append({"name": username, "score": SCORE + int(DISTANCE)})
                save_data("leaderboard.json", leaderboard)
                return "MENU"

        enemies.draw(screen); hazards.draw(screen); powerups.draw(screen); coins_grp.draw(screen)
        screen.blit(player.image, player.rect)
        if player.shield_on: p.draw.circle(screen, (0, 255, 255), player.rect.center, 55, 3)

        p.draw.rect(screen, (0,0,0), (0,0,WIDTH, 45))
        draw_text(f"SCORE: {SCORE} | COINS: {COINS} | {int(DISTANCE)}m", (10, 12))
        if msg_timer > 0:
            draw_text(msg, (0, HEIGHT//2), (255, 255, 0), center=True)
            msg_timer -= 1

        p.display.update(); clock.tick(60)

def main_menu():
    user = "Racer1"
    while True:
        screen.fill((30, 30, 30))
        draw_text("RACER PRO", (0, 80), (0, 255, 127), center=True)
        
        btns = [
            ("START RACE", p.Rect(100, 200, 200, 50), (0, 180, 0)),
            ("GARAGE/SETTINGS", p.Rect(100, 280, 200, 50), (0, 100, 255)),
            ("LEADERBOARD", p.Rect(100, 360, 200, 50), (200, 150, 0)),
            ("QUIT", p.Rect(100, 440, 200, 50), (180, 0, 0))
        ]

        for txt, rect, col in btns:
            p.draw.rect(screen, col, rect, border_radius=5)
            t_surf = font.render(txt, True, (255, 255, 255))
            screen.blit(t_surf, t_surf.get_rect(center=rect.center))

        for event in p.event.get():
            if event.type == p.QUIT: return "QUIT"
            if event.type == p.MOUSEBUTTONDOWN:
                if btns[0][1].collidepoint(event.pos): return gameplay(user)
                if btns[1][1].collidepoint(event.pos): return settings_screen()
                if btns[2][1].collidepoint(event.pos): return leaderboard_screen()
                if btns[3][1].collidepoint(event.pos): return "QUIT"
        p.display.update()

# --- Start ---
state = "MENU"
while state != "QUIT":
    if state == "MENU": state = main_menu()
p.quit()