
import pygame
import sys
from config import *
from game  import GameState, load_settings, save_settings
import db
 
 
# Helpers
 
def draw_text(surface, text, font, color, cx, cy, anchor="center"):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if anchor == "center":
        rect.center = (cx, cy)
    elif anchor == "topleft":
        rect.topleft = (cx, cy)
    elif anchor == "topright":
        rect.topright = (cx, cy)
    surface.blit(surf, rect)
    return rect
 
 
def draw_button(surface, text, font, rect, hovered=False):
    color  = (60, 60, 90) if not hovered else (90, 90, 140)
    border = GOLD if hovered else GRAY
    pygame.draw.rect(surface, color, rect, border_radius=8)
    pygame.draw.rect(surface, border, rect, 2, border_radius=8)
    draw_text(surface, text, font, WHITE, rect.centerx, rect.centery)
 
 
def button_rects(labels, start_y, width=200, height=44, gap=14, cx=None):
    if cx is None:
        cx = WINDOW_WIDTH // 2
    rects = []
    for i, label in enumerate(labels):
        r = pygame.Rect(0, 0, width, height)
        r.centerx = cx
        r.y = start_y + i * (height + gap)
        rects.append((label, r))
    return rects
 
 
# Username input screen
 
def screen_username(surface, clock, font_lg, font_md, font_sm):
    username = ""
    error    = ""
 
    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    name = username.strip()
                    if len(name) < 2:
                        error = "Username must be at least 2 characters."
                    elif len(name) > 20:
                        error = "Username must be at most 20 characters."
                    else:
                        return name
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.unicode.isprintable() and len(username) < 20:
                    username += event.unicode
 
        surface.fill(DARK_BG)
        draw_text(surface, "SNAKE GAME", font_lg, GREEN, WINDOW_WIDTH // 2, 140)
        draw_text(surface, "Enter your username", font_md, LIGHT_GRAY, WINDOW_WIDTH // 2, 220)
 
        # Input box
        box = pygame.Rect(WINDOW_WIDTH // 2 - 150, 265, 300, 46)
        pygame.draw.rect(surface, (30, 30, 50), box, border_radius=6)
        pygame.draw.rect(surface, GOLD, box, 2, border_radius=6)
        draw_text(surface, username + "|", font_md, WHITE, box.centerx, box.centery)
 
        if error:
            draw_text(surface, error, font_sm, RED, WINDOW_WIDTH // 2, 330)
 
        draw_text(surface, "Press ENTER to continue", font_sm, GRAY, WINDOW_WIDTH // 2, 370)
        pygame.display.flip()
 
 
# Main menu
 
def screen_main_menu(surface, clock, font_lg, font_md, font_sm, username):
    buttons = button_rects(["Play", "Leaderboard", "Settings", "Quit"], start_y=260)
 
    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for label, rect in buttons:
                    if rect.collidepoint(mx, my):
                        return label
 
        surface.fill(DARK_BG)
        draw_text(surface, "SNAKE GAME", font_lg, GREEN, WINDOW_WIDTH // 2, 110)
        draw_text(surface, f"Welcome, {username}", font_sm, CYAN, WINDOW_WIDTH // 2, 190)
 
        # Snake decoration
        for i, x in enumerate(range(200, 600, 30)):
            c = (50, 180, 50) if i > 0 else (100, 255, 100)
            pygame.draw.rect(surface, c, (x, 220, 26, 26), border_radius=4)
 
        for label, rect in buttons:
            draw_button(surface, label, font_md, rect, rect.collidepoint(mx, my))
 
        pygame.display.flip()
 
 
# Gameplay screen
 
def screen_gameplay(surface, clock, font_md, font_sm, settings, personal_best, eat_sound, game_over_sound, power_up_sound):
    state      = GameState(settings, personal_best)
    logic_acc  = 0          # milliseconds accumulator
    prev_time  = pygame.time.get_ticks()
 
    while True:
        now  = pygame.time.get_ticks()
        dt   = now - prev_time
        prev_time = now
        clock.tick(60)       # render at 60 fps; logic at current_speed hz
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return state   # return to menu
                state.handle_key(event.key)
 
        # Fixed-step game logic
        logic_ms  = 1000 // max(1, state.current_speed)
        logic_acc += dt
        while logic_acc >= logic_ms:
            state.update()
            logic_acc -= logic_ms
            if state.game_over:
                return state
 
        # Draw
        state.draw(surface)
        state.draw_hud(surface, font_sm, font_md)
        pygame.display.flip()
 
    return state
 
 
# Game-over screen
 
def screen_game_over(surface, clock, font_lg, font_md, font_sm,
                     score, level, personal_best, new_best):
    buttons = button_rects(["Retry", "Main Menu"], start_y=380)
 
    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for label, rect in buttons:
                    if rect.collidepoint(mx, my):
                        return label
 
        surface.fill(DARK_BG)
        draw_text(surface, "GAME OVER", font_lg, RED, WINDOW_WIDTH // 2, 120)
        draw_text(surface, f"Score:  {score}",         font_md, WHITE,      WINDOW_WIDTH // 2, 210)
        draw_text(surface, f"Level:  {level}",         font_md, GOLD,       WINDOW_WIDTH // 2, 255)
 
        best_color = GOLD if new_best else CYAN
        best_label = "NEW BEST!" if new_best else f"Personal Best:  {personal_best}"
        draw_text(surface, best_label, font_md, best_color, WINDOW_WIDTH // 2, 300)
 
        for label, rect in buttons:
            draw_button(surface, label, font_md, rect, rect.collidepoint(mx, my))
 
        pygame.display.flip()
 
 
# Leaderboard screen
 
def screen_leaderboard(surface, clock, font_lg, font_md, font_sm, db_ok):
    rows    = db.get_leaderboard() if db_ok else []
    back_rect = pygame.Rect(WINDOW_WIDTH // 2 - 60, 545, 120, 38)
 
    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(mx, my):
                    return
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                return
 
        surface.fill(DARK_BG)
        draw_text(surface, "LEADERBOARD", font_lg, GOLD, WINDOW_WIDTH // 2, 45)
 
        # Header
        headers = [("Rank", 80), ("Player", 230), ("Score", 400), ("Level", 530), ("Date", 670)]
        for h, x in headers:
            draw_text(surface, h, font_sm, CYAN, x, 100, anchor="center")
        pygame.draw.line(surface, GRAY, (40, 115), (760, 115), 1)
 
        if not db_ok:
            draw_text(surface, "Database not available.", font_md, RED, WINDOW_WIDTH // 2, 280)
        elif not rows:
            draw_text(surface, "No scores yet. Be the first!", font_md, LIGHT_GRAY, WINDOW_WIDTH // 2, 280)
        else:
            for i, row in enumerate(rows):
                y     = 130 + i * 38
                color = [GOLD, LIGHT_GRAY, (205, 127, 50)][min(i, 2)] if i < 3 else WHITE
                date_str = row["played_at"].strftime("%Y-%m-%d") if row.get("played_at") else "-"
                cols_data = [
                    (str(row["rank"]),          80),
                    (str(row["username"])[:16], 230),
                    (str(row["score"]),          400),
                    (str(row["level_reached"]),  530),
                    (date_str,                   670),
                ]
                for text, x in cols_data:
                    draw_text(surface, text, font_sm, color, x, y, anchor="center")
 
        draw_button(surface, "Back", font_md, back_rect, back_rect.collidepoint(mx, my))
        pygame.display.flip()
 
 
# Settings screen
 
COLOR_PRESETS = [
    ("Green",   (50, 205, 50)),
    ("Blue",    (50, 150, 255)),
    ("Orange",  (255, 140, 0)),
    ("Purple",  (180, 50, 220)),
    ("Red",     (220, 60, 60)),
    ("Cyan",    (0, 220, 220)),
    ("White",   (230, 230, 230)),
    ("Yellow",  (240, 210, 40)),
]
 
 
def screen_settings(surface, clock, font_lg, font_md, font_sm, settings: dict):
    local = dict(settings)
 
    save_rect = pygame.Rect(WINDOW_WIDTH // 2 - 110, 500, 220, 44)
 
    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Toggle grid
                grid_rect = pygame.Rect(WINDOW_WIDTH // 2 + 60, 195, 120, 36)
                if grid_rect.collidepoint(mx, my):
                    local["grid_overlay"] = not local["grid_overlay"]
 
                # Toggle sound
                sound_rect = pygame.Rect(WINDOW_WIDTH // 2 + 60, 255, 120, 36)
                if sound_rect.collidepoint(mx, my):
                    local["sound"] = not local["sound"]
 
                # Color swatches
                for i, (name, rgb) in enumerate(COLOR_PRESETS):
                    sx = 100 + i * 80
                    sy = 350
                    swatch = pygame.Rect(sx, sy, 60, 60)
                    if swatch.collidepoint(mx, my):
                        local["snake_color"] = list(rgb)
 
                # Save & Back
                if save_rect.collidepoint(mx, my):
                    settings.update(local)
                    save_settings(settings)
                    return
 
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
 
        surface.fill(DARK_BG)
        draw_text(surface, "SETTINGS", font_lg, WHITE, WINDOW_WIDTH // 2, 60)
 
        # Grid toggle
        draw_text(surface, "Grid Overlay", font_md, LIGHT_GRAY, 200, 213, anchor="center")
        grid_rect = pygame.Rect(WINDOW_WIDTH // 2 + 60, 195, 120, 36)
        grid_on   = local["grid_overlay"]
        pygame.draw.rect(surface, (30, 80, 30) if grid_on else (60, 30, 30), grid_rect, border_radius=6)
        pygame.draw.rect(surface, GREEN if grid_on else RED, grid_rect, 2, border_radius=6)
        draw_text(surface, "ON" if grid_on else "OFF", font_sm, WHITE, grid_rect.centerx, grid_rect.centery)
 
        # Sound toggle
        draw_text(surface, "Sound", font_md, LIGHT_GRAY, 200, 273, anchor="center")
        sound_rect = pygame.Rect(WINDOW_WIDTH // 2 + 60, 255, 120, 36)
        snd_on     = local["sound"]
        pygame.draw.rect(surface, (30, 80, 30) if snd_on else (60, 30, 30), sound_rect, border_radius=6)
        pygame.draw.rect(surface, GREEN if snd_on else RED, sound_rect, 2, border_radius=6)
        draw_text(surface, "ON" if snd_on else "OFF", font_sm, WHITE, sound_rect.centerx, sound_rect.centery)
 
        # Snake color
        draw_text(surface, "Snake Color", font_md, LIGHT_GRAY, WINDOW_WIDTH // 2, 330)
        cur_color = tuple(local["snake_color"])
        for i, (name, rgb) in enumerate(COLOR_PRESETS):
            sx = 100 + i * 80
            swatch = pygame.Rect(sx, 350, 60, 60)
            pygame.draw.rect(surface, rgb, swatch, border_radius=8)
            if tuple(rgb) == cur_color:
                pygame.draw.rect(surface, WHITE, swatch, 3, border_radius=8)
            draw_text(surface, name, font_sm, LIGHT_GRAY, sx + 30, 418, anchor="center")
 
        draw_button(surface, "Save & Back", font_md, save_rect, save_rect.collidepoint(mx, my))
        pygame.display.flip()
 
 
# Main
 
def main():
    pygame.init()
    pygame.mixer.init()
    eat_sound = pygame.mixer.Sound("assets/eat.wav")
    game_over_sound = pygame.mixer.Sound("assets/game_over.wav")
    power_up_sound = pygame.mixer.Sound("assets/power_up.wav")
    surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
 
    # Fonts
    font_lg = pygame.font.SysFont("consolas", 52, bold=True)
    font_md = pygame.font.SysFont("consolas", 26)
    font_sm = pygame.font.SysFont("consolas", 18)
 
    # DB
    db_ok = db.init_db()
    if not db_ok:
        print("[Main] Running without database (scores will not be saved).")
 
    # Settings
    settings = load_settings()
 
    # Username
    username  = screen_username(surface, clock, font_lg, font_md, font_sm)
    player_id = db.get_or_create_player(username) if db_ok else None
 
    personal_best = db.get_personal_best(username) if db_ok else 0
 
    # Main loop
    while True:
        choice = screen_main_menu(surface, clock, font_lg, font_md, font_sm, username)
 
        if choice == "Quit":
            break
 
        elif choice == "Leaderboard":
            screen_leaderboard(surface, clock, font_lg, font_md, font_sm, db_ok)
 
        elif choice == "Settings":
            screen_settings(surface, clock, font_lg, font_md, font_sm, settings)
 
        elif choice == "Play":
            while True:
                state = screen_gameplay(
                    surface, clock, font_md, font_sm, settings, personal_best, eat_sound, game_over_sound, power_up_sound
                )
 
                if state.game_over:
                    # Save to DB
                    if db_ok and player_id:
                        db.save_session(player_id, state.score, state.level)
                    personal_best = max(personal_best, state.score)
 
                    action = screen_game_over(
                        surface, clock, font_lg, font_md, font_sm,
                        state.score, state.level, personal_best, state.new_best
                    )
                    if action == "Main Menu":
                        break
                    # else Retry — loop continues
                else:
                    # Player pressed ESC — back to menu
                    break
 
    pygame.quit()
    sys.exit()
 
 
if __name__ == "__main__":
    main()