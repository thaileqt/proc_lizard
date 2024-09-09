import ctypes

import pygame
import sys
from lizard import Lizard
import win32api
import win32con
import win32gui
# Initialize Pygame
pygame.init()

# Set up the display
info = pygame.display.Info()
WIDTH, HEIGHT = 1600, 900
# WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Procedural Lizard Animation")
# Create layered window
hwnd = pygame.display.get_wm_info()["window"]
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                       win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
# Set window transparency color
fuchsia = (255, 0, 128)  # Transparency color
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)
# Set the window to be always on top (Windows-specific)
if sys.platform == "win32":
    hwnd = pygame.display.get_wm_info()["window"]
    ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)
# Create lizard
lizard = Lizard(pygame.math.Vector2(WIDTH // 2, HEIGHT // 2))

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    screen.fill(fuchsia)  # Transparent background

    lizard.update(WIDTH, HEIGHT)
    lizard.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()