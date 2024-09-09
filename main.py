import pygame
import sys
from lizard import Lizard

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Procedural Lizard Animation")

# Colors
BACKGROUND = (40, 44, 52)

# Create lizard
lizard = Lizard(pygame.math.Vector2(WIDTH // 2, HEIGHT // 2))

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BACKGROUND)

    lizard.update(WIDTH, HEIGHT)
    lizard.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()