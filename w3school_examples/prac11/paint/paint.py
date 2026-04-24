import pygame as p
import math
import os

p.init()

# screen
icon = p.image.load(r"C:\Users\Admin\Desktop\python\images\icon_paint.png")
WIDTH, HEIGHT = 1000, 850
p.display.set_caption("Paint")
p.display.set_icon(icon)
screen = p.display.set_mode((WIDTH, HEIGHT))
clock = p.time.Clock()
font = p.font.SysFont("Arial", 12, bold=True)
large_font = p.font.SysFont("Arial", 18, bold=True)

# painting surface
canvas_offset = (100, 150)
canvas = p.Surface((800, 600))
canvas.fill((255, 255, 255))

# initial values
color = (0, 0, 0)
brush_size = 3
tool = "draw"
drawing = False
start_pos = None 


btns = {
    # Colors
    "black":   {"rect": p.Rect(10, 10, 40, 40), "color": (0,0,0)},
    "red":     {"rect": p.Rect(60, 10, 40, 40), "color": (255,0,0)},
    "green":   {"rect": p.Rect(110, 10, 40, 40), "color": (0,255,0)},
    "blue":    {"rect": p.Rect(160, 10, 40, 40), "color": (0,0,255)},
    "purple":  {"rect": p.Rect(210, 10, 40, 40), "color": (128,0,128)},
    "orange":  {"rect": p.Rect(260, 10, 40, 40), "color": (255,165,0)},
    "cyan":    {"rect": p.Rect(310, 10, 40, 40), "color": (0,255,255)},
    "eraser":  {"rect": p.Rect(370, 10, 60, 40), "color": (255,255,255), "label": "eraser"},
    
    # Tools
    "draw":    {"rect": p.Rect(10, 60, 70, 40), "label": "pencil"},
    "square":  {"rect": p.Rect(90, 60, 70, 40), "label": "rectangle"},
    "rect_tri": {"rect": p.Rect(170, 60, 70, 40), "label": "r-tri"},
    "eq_tri":  {"rect": p.Rect(250, 60, 70, 40), "label": "e-tri"},
    "rhombus": {"rect": p.Rect(330, 60, 70, 40), "label": "rhombus"},
    
    # Width
    "minus":   {"rect": p.Rect(450, 60, 40, 40), "label": "-"},
    "plus":    {"rect": p.Rect(500, 60, 40, 40), "label": "+"},
    
    # Clear
    "clear":   {"rect": p.Rect(910, 10, 70, 40), "label": "clear"}
}

def get_shape_points(shape_type, start, end):
    x1, y1 = start
    x2, y2 = end
    w, h = x2 - x1, y2 - y1
    if shape_type == "rect_tri": return [(x1, y1), (x1, y2), (x2, y2)]
    elif shape_type == "eq_tri":
        side = x2 - x1
        height = (math.sqrt(3) / 2) * side
        return [(x1 + side/2, y1), (x1, y1 + height), (x1 + side, y1 + height)]
    elif shape_type == "rhombus": return [(x1 + w/2, y1), (x2, y1 + h/2), (x1 + w/2, y2), (x1, y1 + h/2)]
    return []

running = True
last_draw_pos = None

while running:
    mx, my = p.mouse.get_pos()
    cx, cy = mx - canvas_offset[0], my - canvas_offset[1]
    
    for event in p.event.get():
        if event.type == p.QUIT:
            running = False

        if event.type == p.MOUSEBUTTONDOWN:
            clicked_ui = False
            for name, info in btns.items():
                if info["rect"].collidepoint(mx, my):
                    clicked_ui = True
                    if "color" in info:
                        color = info["color"]
                        if name == "eraser": tool = "draw"
                    elif name == "plus": brush_size = min(50, brush_size + 1)
                    elif name == "minus": brush_size = max(1, brush_size - 1)
                    elif name == "clear": canvas.fill((255, 255, 255))
                    else: tool = name
            
            if not clicked_ui and 0 <= cx <= 800 and 0 <= cy <= 600:
                drawing = True
                start_pos = (cx, cy)
                last_draw_pos = (cx, cy)

        if event.type == p.MOUSEBUTTONUP:
            if drawing:
                if tool != "draw" and start_pos:
                    if tool == "square":
                        side = max(abs(cx - start_pos[0]), abs(cy - start_pos[1]))
                        rect = p.Rect(start_pos[0], start_pos[1], side, side)
                        p.draw.rect(canvas, color, rect, brush_size)
                    else:
                        pts = get_shape_points(tool, start_pos, (cx, cy))
                        if len(pts) > 2: p.draw.polygon(canvas, color, pts, brush_size)
                drawing = False
                start_pos = None

    #drawing with pencil
    if drawing and tool == "draw":
        if 0 <= cx <= 800 and 0 <= cy <= 600:
            p.draw.line(canvas, color, last_draw_pos, (cx, cy), brush_size)
            p.draw.circle(canvas, color, (cx, cy), brush_size // 2) # Smooths the line
            last_draw_pos = (cx, cy)

   
    screen.fill((230, 230, 230))
    
    
    for name, info in btns.items():
        
        bg = (255, 255, 255)
        if "color" in info: bg = info["color"]
        if tool == name: bg = (255, 255, 0) # Highlight active tool
        
        p.draw.rect(screen, bg, info["rect"])
        p.draw.rect(screen, (0, 0, 0), info["rect"], 2)
        
        
        if "label" in info:
            text_color = (0,0,0)
            txt = font.render(info["label"], True, text_color)
            screen.blit(txt, (info["rect"].centerx - txt.get_width()//2, info["rect"].centery - txt.get_height()//2))

    
    screen.blit(large_font.render(f"Width: {brush_size}", True, (0,0,0)), (560, 65))
    p.draw.rect(screen, color, (680, 60, 40, 40))
    p.draw.rect(screen, (0,0,0), (680, 60, 40, 40), 2)

    
    screen.blit(canvas, canvas_offset)
    p.draw.rect(screen, (0,0,0), (canvas_offset[0], canvas_offset[1], 800, 600), 2)

    
    if drawing and tool != "draw" and start_pos:
        ps = (start_pos[0] + canvas_offset[0], start_pos[1] + canvas_offset[1])
        if tool == "square":
            side = max(abs(mx - ps[0]), abs(my - ps[1]))
            p.draw.rect(screen, color, (ps[0], ps[1], side, side), 1)
        else:
            pts = get_shape_points(tool, ps, (mx, my))
            if len(pts) > 2: p.draw.polygon(screen, color, pts, 1)

    p.display.flip()
    clock.tick(120)

p.quit()