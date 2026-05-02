import pygame
from config import *
from db import Database
from settings import load_settings, save_settings

def draw_text(screen, text, size, x, y, color=WHITE):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect)

def draw_button(screen, text, x, y, width, height, inactive_color, active_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x < mouse[0] < x + width and y < mouse[1] < y + height:
        pygame.draw.rect(screen, active_color, (x, y, width, height))
        if click[0] == 1 and action:
            return action
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, width, height))
    draw_text(screen, text, 30, x + width // 2, y + height // 2)
    return None

def get_username(screen, font):
    username = ""
    input_active = True
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    username += event.unicode
        screen.fill(BLACK)
        draw_text(screen, f"Enter username: {username}", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        draw_text(screen, "Press Enter to confirm", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        pygame.display.flip()
    return username

def main_menu(screen, font, db):
    username = None
    while True:
        screen.fill(BLACK)
        draw_text(screen, "SNAKE GAME", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)

        if username is None:
            action = draw_button(screen, "Enter Username", 250, 200, 300, 50, GRAY, WHITE, "username")
            if action == "username":
                username = get_username(screen, font)
                if username:
                    player_id = db.get_or_create_player(username)
        else:
            action = draw_button(screen, "Play", 250, 200, 300, 50, GRAY, WHITE, "play")
            if action == "play":
                return {"action": "play", "username": username, "player_id": db.get_or_create_player(username)}

        action = draw_button(screen, "Leaderboard", 250, 270, 300, 50, GRAY, WHITE, "leaderboard")
        if action == "leaderboard":
            leaderboard_screen(screen, font, db)

        action = draw_button(screen, "Settings", 250, 340, 300, 50, GRAY, WHITE, "settings")
        if action == "settings":
            settings_screen(screen, font)

        action = draw_button(screen, "Quit", 250, 410, 300, 50, GRAY, WHITE, "quit")
        if action == "quit":
            pygame.quit()
            return {"action": "quit"}

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return {"action": "quit"}

def leaderboard_screen(screen, font, db):
    top_10 = db.get_top_10()
    running = True
    while running:
        screen.fill(BLACK)
        draw_text(screen, "LEADERBOARD", 64, SCREEN_WIDTH // 2, 50)
        for i, (username, score, level, date) in enumerate(top_10, 1):
            draw_text(screen, f"{i}. {username}: {score} (Lv. {level})", 30, SCREEN_WIDTH // 2, 100 + i * 40)
        action = draw_button(screen, "Back", 250, 500, 300, 50, GRAY, WHITE, "back")
        if action == "back":
            running = False
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

def settings_screen(screen, font):
    settings = load_settings()
    running = True
    while running:
        screen.fill(BLACK)
        draw_text(screen, "SETTINGS", 64, SCREEN_WIDTH // 2, 50)

        # Snake color
        draw_text(screen, "Snake Color:", 30, SCREEN_WIDTH // 2 - 150, 150)
        pygame.draw.rect(screen, settings["snake_color"], (SCREEN_WIDTH // 2 + 50, 140, 30, 30))

        # Grid toggle
        grid_text = "ON" if settings["grid"] else "OFF"
        action = draw_button(screen, f"Grid: {grid_text}", 250, 200, 300, 50, GRAY, WHITE, "grid")
        if action == "grid":
            settings["grid"] = not settings["grid"]

        # Sound toggle
        sound_text = "ON" if settings["sound"] else "OFF"
        action = draw_button(screen, f"Sound: {sound_text}", 250, 270, 300, 50, GRAY, WHITE, "sound")
        if action == "sound":
            settings["sound"] = not settings["sound"]

        action = draw_button(screen, "Save & Back", 250, 350, 300, 50, GRAY, WHITE, "save")
        if action == "save":
            save_settings(settings)
            running = False

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

def game_over_screen(screen, font, score, level, personal_best):
    running = True
    while running:
        screen.fill(BLACK)
        draw_text(screen, "GAME OVER", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        draw_text(screen, f"Score: {score}", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        draw_text(screen, f"Level: {level}", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text(screen, f"Personal Best: {personal_best}", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)

        action = draw_button(screen, "Retry", 250, 350, 300, 50, GRAY, WHITE, "retry")
        if action == "retry":
            return "retry"

        action = draw_button(screen, "Main Menu", 250, 420, 300, 50, GRAY, WHITE, "menu")
        if action == "menu":
            return "menu"

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "quit"