import pygame
import sys

# --- Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BALL_RADIUS = 25
BALL_COLOR = (255, 0, 0)
BG_COLOR = (255, 255, 255)
MOVE_SPEED = 5  # Reduced speed for continuous movement

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Continuous Moving Ball")
    
    # Starting position
    ball_x = SCREEN_WIDTH // 2
    ball_y = SCREEN_HEIGHT // 2
    
    clock = pygame.time.Clock()

    while True:
        # 1. Standard Event Handling (for quitting)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # 2. Continuous Input Handling
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_UP]:
            if ball_y - MOVE_SPEED >= BALL_RADIUS:
                ball_y -= MOVE_SPEED
        if keys[pygame.K_DOWN]:
            if ball_y + MOVE_SPEED <= SCREEN_HEIGHT - BALL_RADIUS:
                ball_y += MOVE_SPEED
        if keys[pygame.K_LEFT]:
            if ball_x - MOVE_SPEED >= BALL_RADIUS:
                ball_x -= MOVE_SPEED
        if keys[pygame.K_RIGHT]:
            if ball_x + MOVE_SPEED <= SCREEN_WIDTH - BALL_RADIUS:
                ball_x += MOVE_SPEED

        # 3. Drawing
        screen.fill(BG_COLOR)
        pygame.draw.circle(screen, BALL_COLOR, (ball_x, ball_y), BALL_RADIUS)
        
        # 4. Update Display
        pygame.display.flip()
        
        # 5. Framerate (Controls how "fast" the loop runs)
        clock.tick(60)

if __name__ == "__main__":
    main()