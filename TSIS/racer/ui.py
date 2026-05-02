# ui.py — All Pygame screens

import pygame
import sys
from config import *
from persistence import load_leaderboard, add_entry


# ══════════════════════════════════════════════════════════════
# Common helpers
# ══════════════════════════════════════════════════════════════

def draw_text(surface, text, font, color, pos, anchor="topleft"):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    setattr(rect, anchor, pos)
    surface.blit(surf, rect)
    return rect


def make_button(label, cx, y, w=180, h=42):
    r = pygame.Rect(0, 0, w, h)
    r.centerx = cx
    r.y = y
    return (label, r)


def draw_button(surface, label, rect, font, hovered=False):
    bg     = (55, 55, 90) if not hovered else (85, 85, 140)
    border = GOLD if hovered else GRAY
    pygame.draw.rect(surface, bg, rect, border_radius=8)
    pygame.draw.rect(surface, border, rect, 2, border_radius=8)
    draw_text(surface, label, font, WHITE, rect.center, anchor="center")


def button_column(labels, start_y, cx=None, w=180, h=42, gap=12):
    if cx is None:
        cx = WIDTH // 2
    return [make_button(lab, cx, start_y + i * (h + gap), w, h) for i, lab in enumerate(labels)]


# ══════════════════════════════════════════════════════════════
# Username entry
# ══════════════════════════════════════════════════════════════

def screen_username(surface, clock, fonts):
    f_lg, f_md, f_sm, f_xs = fonts
    username = ""
    error    = ""

    while True:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    name = username.strip()
                    if len(name) < 2:
                        error = "At least 2 characters required."
                    elif len(name) > 18:
                        error = "Max 18 characters."
                    else:
                        return name
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                    error = ""
                elif event.unicode.isprintable() and len(username) < 18:
                    username += event.unicode
                    error = ""

        surface.fill(DARK_BG)
        draw_text(surface, "RACER", f_lg, RED, (WIDTH // 2, 120), anchor="center")
        draw_text(surface, "Enter your name:", f_md, LIGHT_GRAY, (WIDTH // 2, 210), anchor="center")

        box = pygame.Rect(WIDTH // 2 - 130, 245, 260, 44)
        pygame.draw.rect(surface, (28, 28, 48), box, border_radius=6)
        pygame.draw.rect(surface, GOLD, box, 2, border_radius=6)
        draw_text(surface, username + "|", f_md, WHITE, box.center, anchor="center")

        if error:
            draw_text(surface, error, f_xs, RED, (WIDTH // 2, 305), anchor="center")

        draw_text(surface, "Press ENTER to continue", f_xs, GRAY, (WIDTH // 2, 340), anchor="center")
        pygame.display.flip()


# ══════════════════════════════════════════════════════════════
# Main menu
# ══════════════════════════════════════════════════════════════

def screen_main_menu(surface, clock, fonts, username):
    f_lg, f_md, f_sm, f_xs = fonts
    buttons = button_column(["Play", "Leaderboard", "Settings", "Quit"], start_y=240)

    while True:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for label, rect in buttons:
                    if rect.collidepoint(mx, my):
                        return label

        surface.fill(DARK_BG)

        # Road decoration
        pygame.draw.rect(surface, ROAD_DARK, (WIDTH // 2 - 60, 0, 120, HEIGHT))
        for y in range(0, HEIGHT, 60):
            pygame.draw.rect(surface, ROAD_LINE, (WIDTH // 2 - 3, y, 6, 30))

        draw_text(surface, "RACER", f_lg, RED, (WIDTH // 2, 90), anchor="center")
        draw_text(surface, f"Driver: {username}", f_xs, CYAN, (WIDTH // 2, 165), anchor="center")

        for label, rect in buttons:
            draw_button(surface, label, rect, f_md, rect.collidepoint(mx, my))

        pygame.display.flip()


# ══════════════════════════════════════════════════════════════
# Settings screen
# ══════════════════════════════════════════════════════════════

def screen_settings(surface, clock, fonts, settings: dict):
    f_lg, f_md, f_sm, f_xs = fonts
    local = dict(settings)
    save_rect = pygame.Rect(WIDTH // 2 - 100, 530, 200, 42)

    while True:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Sound toggle
                snd_rect = pygame.Rect(WIDTH // 2 + 20, 178, 110, 34)
                if snd_rect.collidepoint(mx, my):
                    local["sound"] = not local["sound"]

                # Difficulty buttons
                for i, (dlabel, *_) in enumerate(DIFFICULTIES):
                    dr = pygame.Rect(50 + i * 120, 258, 100, 34)
                    if dr.collidepoint(mx, my):
                        local["difficulty"] = i

                # Car color swatches
                for i, (cname, crgb) in enumerate(CAR_COLORS):
                    col = i % 3
                    row = i // 3
                    sx  = 80 + col * 110
                    sy  = 370 + row * 70
                    swatch = pygame.Rect(sx, sy, 80, 50)
                    if swatch.collidepoint(mx, my):
                        local["car_color"] = list(crgb)

                # Save & Back
                if save_rect.collidepoint(mx, my):
                    settings.update(local)
                    from persistence import save_settings
                    save_settings(settings)
                    return

        surface.fill(DARK_BG)
        draw_text(surface, "SETTINGS", f_lg, WHITE, (WIDTH // 2, 50), anchor="center")

        # Sound
        draw_text(surface, "Sound", f_md, LIGHT_GRAY, (WIDTH // 2 - 20, 185), anchor="midright")
        snd_rect = pygame.Rect(WIDTH // 2 + 20, 178, 110, 34)
        snd_on   = local["sound"]
        pygame.draw.rect(surface, (28, 70, 28) if snd_on else (60, 28, 28), snd_rect, border_radius=6)
        pygame.draw.rect(surface, GREEN if snd_on else RED, snd_rect, 2, border_radius=6)
        draw_text(surface, "ON" if snd_on else "OFF", f_sm, WHITE, snd_rect.center, anchor="center")

        # Difficulty
        draw_text(surface, "Difficulty", f_md, LIGHT_GRAY, (WIDTH // 2, 232), anchor="center")
        for i, (dlabel, *_) in enumerate(DIFFICULTIES):
            dr = pygame.Rect(50 + i * 120, 258, 100, 34)
            selected = (local["difficulty"] == i)
            col = GOLD if selected else GRAY
            pygame.draw.rect(surface, (40, 40, 60), dr, border_radius=6)
            pygame.draw.rect(surface, col, dr, 2, border_radius=6)
            draw_text(surface, dlabel, f_xs, WHITE if selected else LIGHT_GRAY, dr.center, anchor="center")

        # Car color
        draw_text(surface, "Car Color", f_md, LIGHT_GRAY, (WIDTH // 2, 345), anchor="center")
        cur_color = tuple(local["car_color"])
        for i, (cname, crgb) in enumerate(CAR_COLORS):
            col = i % 3
            row = i // 3
            sx  = 80 + col * 110
            sy  = 370 + row * 70
            swatch = pygame.Rect(sx, sy, 80, 50)
            pygame.draw.rect(surface, crgb, swatch, border_radius=8)
            if tuple(crgb) == cur_color:
                pygame.draw.rect(surface, WHITE, swatch, 3, border_radius=8)
            draw_text(surface, cname, f_xs, LIGHT_GRAY, (sx + 40, sy + 55), anchor="center")

        draw_button(surface, "Save & Back", save_rect, f_md, save_rect.collidepoint(mx, my))
        pygame.display.flip()


# ══════════════════════════════════════════════════════════════
# Leaderboard screen
# ══════════════════════════════════════════════════════════════

def screen_leaderboard(surface, clock, fonts):
    f_lg, f_md, f_sm, f_xs = fonts
    rows      = load_leaderboard()
    back_rect = pygame.Rect(WIDTH // 2 - 60, 580, 120, 38)

    while True:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(mx, my):
                    return

        surface.fill(DARK_BG)
        draw_text(surface, "LEADERBOARD", f_lg, GOLD, (WIDTH // 2, 40), anchor="center")

        headers = [("#", 38), ("Name", 110), ("Score", 250), ("Dist", 340), ("Coins", 420)]
        for h, x in headers:
            draw_text(surface, h, f_xs, CYAN, (x, 95), anchor="topleft")
        pygame.draw.line(surface, GRAY, (30, 112), (WIDTH - 30, 112), 1)

        if not rows:
            draw_text(surface, "No scores yet!", f_md, LIGHT_GRAY, (WIDTH // 2, 300), anchor="center")
        else:
            for i, row in enumerate(rows[:10]):
                y   = 120 + i * 42
                col = [GOLD, LIGHT_GRAY, (200, 120, 40)][min(i, 2)] if i < 3 else WHITE
                cells = [
                    (str(i + 1),                     38),
                    (str(row.get("name", "?"))[:12], 110),
                    (str(row.get("score", 0)),       250),
                    (str(row.get("distance", 0)),    340),
                    (str(row.get("coins", 0)),       420),
                ]
                for text, x in cells:
                    draw_text(surface, text, f_xs, col, (x, y), anchor="topleft")

        draw_button(surface, "Back", back_rect, f_md, back_rect.collidepoint(mx, my))
        pygame.display.flip()


# ══════════════════════════════════════════════════════════════
# Game Over screen
# ══════════════════════════════════════════════════════════════

def screen_game_over(surface, clock, fonts, score, distance, coins):
    f_lg, f_md, f_sm, f_xs = fonts
    buttons = button_column(["Retry", "Main Menu"], start_y=400)

    while True:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for label, rect in buttons:
                    if rect.collidepoint(mx, my):
                        return label

        surface.fill(DARK_BG)
        draw_text(surface, "CRASH!", f_lg, RED, (WIDTH // 2, 100), anchor="center")

        stats = [
            (f"Score:    {int(score)}",    WHITE),
            (f"Distance: {distance}m",     CYAN),
            (f"Coins:    {coins}",         GOLD),
        ]
        for i, (text, color) in enumerate(stats):
            draw_text(surface, text, f_md, color, (WIDTH // 2, 210 + i * 52), anchor="center")

        for label, rect in buttons:
            draw_button(surface, label, rect, f_md, rect.collidepoint(mx, my))

        pygame.display.flip()