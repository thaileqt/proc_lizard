import ctypes
import pygame
import sys
from lizard import Lizard
import win32api
import win32con
import win32gui
from win32gui import SetWindowPos
import pystray
import threading
from PIL import Image

class SystemTrayThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        icon_image = Image.open("icon.png")
        self.icon = pystray.Icon("lizark", icon_image, menu=pystray.Menu(pystray.MenuItem("Quit", self.on_quit)))

    def run(self):
        self.icon.run()

    def on_quit(self):
        global running
        self.icon.stop()
        running = False

tray_thread = SystemTrayThread()
tray_thread.start()


pygame.init()
# Set up the display
info = pygame.display.Info()
WIDTH, HEIGHT = 1600, 900
# WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("lizark")
pygame.display.set_icon(pygame.image.load("icon.png"))


# Create layered window
hwnd = pygame.display.get_wm_info()["window"]
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                       win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TOOLWINDOW)
fuchsia = (255, 0, 128)
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)
SetWindowPos(pygame.display.get_wm_info()['window'], win32con.HWND_TOPMOST, 0,0,0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

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