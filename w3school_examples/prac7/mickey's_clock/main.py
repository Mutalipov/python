import pygame as p
import time
import math

p.init()

w, h = 800, 800
screen = p.display.set_mode((w, h))
p.display.set_caption("Mickey Clock - Lines Only")

clock = p.time.Clock()

center = (w // 2, h // 2)
radius = 350
back = (250, 250, 250)

def draw_numbers():
    font = p.font.SysFont(None, 40)
    for i in range(1, 13):
        angle = math.radians(i * 30 - 90)
        x = center[0] + (radius - 40) * math.cos(angle)
        y = center[1] + (radius - 40) * math.sin(angle)
        text = font.render(str(i), True, (0, 0, 0))
        rect = text.get_rect(center=(x, y))
        screen.blit(text, rect)

def draw_ticks():
    for i in range(60):
        angle = math.radians(i * 6 - 90)
        if i % 5 == 0:
            length, width = 25, 4
        else:
            length, width = 12, 2
        x1 = center[0] + radius * math.cos(angle)
        y1 = center[1] + radius * math.sin(angle)
        x2 = center[0] + (radius - length) * math.cos(angle)
        y2 = center[1] + (radius - length) * math.sin(angle)
        p.draw.line(screen, (0, 0, 0), (x1, y1), (x2, y2), width)

def draw_hand(angle, length, width, color):
    # Convert angle to radians and adjust so 0 is at 12 o'clock
    rad = math.radians(angle - 90)
    x = center[0] + length * math.cos(rad)
    y = center[1] + length * math.sin(rad)
    p.draw.line(screen, color, center, (x, y), width)

running = True
while running:
    for event in p.event.get():
        if event.type == p.QUIT:
            running = False

    screen.fill(back)
    
    # Draw Clock Face
    p.draw.circle(screen, (200, 200, 200), center, radius, 15)
    draw_ticks()
    draw_numbers()
    
    t = time.localtime()
    
    # Calculate angles in degrees
    # 360 / 60 = 6 degrees per second/minute
    # 360 / 12 = 30 degrees per hour
    sec_angle = t.tm_sec * 6
    min_angle = t.tm_min * 6 + t.tm_sec * 0.1
    hour_angle = (t.tm_hour % 12) * 30 + t.tm_min * 0.5

    # Draw Hands as Lines
    draw_hand(hour_angle, 180, 8, (0, 0, 0))      # Hour hand
    draw_hand(min_angle, 260, 5, (50, 50, 50))    # Minute hand
    draw_hand(sec_angle, 300, 2, (255, 0, 0))     # Second hand (Red)

    p.draw.circle(screen, (0, 0, 0), center, 8)

    p.display.flip()
    clock.tick(60)

p.quit()