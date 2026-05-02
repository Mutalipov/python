import os
import pygame
import sys
from config import *
from racer import GameState
from ui import (screen_username, screen_main_menu, screen_settings,
                screen_leaderboard, screen_game_over)
from persistence import load_settings, save_settings, add_entry

def run_game(surface, clock, fonts, settings,coin_sound,crash_sound):
    """Run one gameplay session. Returns (score, distance, coins)."""
    f_lg, f_md, f_sm, f_xs = fonts
    state     = GameState(settings, coin_sound, crash_sound)
    state.coin_sound = coin_sound
    state.crash_sound = crash_sound
    key_delay = {}   # simple key-repeat suppression

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return state.score, state.distance // 60, state.coins_collected
                state.handle_key(event.key)

        # Held keys for smooth lane changes
        keys = pygame.key.get_pressed()
        now  = pygame.time.get_ticks()
        for k in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
            if keys[k]:
                last = key_delay.get(k, 0)
                if now - last > 160:
                    state.handle_key(k)
                    key_delay[k] = now

        state.update()

        if state.game_over:
            return int(state.score), state.distance // 60, state.coins_collected

        state.draw(surface)
        state.draw_hud(surface, f_sm, f_xs)
        pygame.display.flip()


def main():
    pygame.init()
    pygame.mixer.init()
    BASE_DIR = os.path.dirname(__file__)

    coin_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, r"assets\coin.wav"))
    crash_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, r"assets\crash.wav"))
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock   = pygame.time.Clock()

    f_lg = pygame.font.SysFont("consolas", 54, bold=True)
    f_md = pygame.font.SysFont("consolas", 26)
    f_sm = pygame.font.SysFont("consolas", 20)
    f_xs = pygame.font.SysFont("consolas", 16)
    fonts = (f_lg, f_md, f_sm, f_xs)

    settings = load_settings()
    username = screen_username(surface, clock, fonts)

    while True:
        choice = screen_main_menu(surface, clock, fonts, username)

        if choice == "Quit":
            break

        elif choice == "Leaderboard":
            screen_leaderboard(surface, clock, fonts)

        elif choice == "Settings":
            screen_settings(surface, clock, fonts, settings)

        elif choice == "Play":
            while True:
                score, distance, coins = run_game(surface, clock, fonts, settings, coin_sound, crash_sound)

                # Save to leaderboard
                add_entry(username, score, distance, coins)

                action = screen_game_over(surface, clock, fonts, score, distance, coins)
                if action == "Main Menu":
                    break
                # else Retry — loop continues

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()