import pygame
import sys
import win32api, win32con, win32gui, ctypes
from win32gui import SetWindowPos
import pystray
import threading
from PIL import Image
import psutil
from lizard import Lizard
from config import LizardConfig, ConfigWindow
from utils import *


running = True
lizard_mode = "auto"  # Default mode

show_ram_fps = False
fps = 0
ram_usage = 0



def get_ram_usage():
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024  # Convert to MB

class SystemTrayThread(threading.Thread):
    def __init__(self, lizard):
        super().__init__()

        self.running = True
        icon_image = Image.open("icon.png")
        self.lizard_config = LizardConfig(lizard)
        self.lizard = lizard

        # Load icons
        self.icon_main = Image.open("icon.png")


        self.icon = pystray.Icon("lizark", self.icon_main, menu=self._create_menu())

    def _create_menu(self):
        return pystray.Menu(
            pystray.MenuItem("Mode", pystray.Menu(
                pystray.MenuItem("Follow", self.on_follow, checked=lambda item: lizard_mode == "follow", radio=True,
                                 default=False),
                pystray.MenuItem("Auto", self.on_auto, checked=lambda item: lizard_mode == "auto", radio=True,
                                 default=True)
            ), default=True),
            pystray.MenuItem("Show Performance", self.on_performance, checked=lambda item: show_ram_fps == True, default=False),
            pystray.MenuItem("Show Bones", self.on_show_bones, checked=lambda item: self.lizard.transparent == True, default=False),
            pystray.MenuItem("Config", self.on_config),
            pystray.MenuItem("Quit", self.on_quit),
        )

    def run(self):
        self.icon.run()

    def on_quit(self):
        global running
        self.icon.stop()
        running = False

    def on_config(self):
        self.lizard_config.show_config_dialog()

    def on_auto(self):
        global lizard_mode
        lizard_mode = "auto"
        self.icon.update_menu()

    def on_follow(self):
        global lizard_mode
        lizard_mode = "follow"
        self.icon.update_menu()

    def on_performance(self):
        global show_ram_fps
        show_ram_fps = not show_ram_fps

    def on_show_bones(self):
        self.lizard.transparent = not self.lizard.transparent


def main():
    global running, lizard_mode, fps, ram_usage

    pygame.init()
    # Set up the display
    info = pygame.display.Info()
    # WIDTH, HEIGHT = 1600, 900
    WIDTH, HEIGHT = info.current_w, info.current_h

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME | pygame.SRCALPHA)
    pygame.display.set_caption("lizark")
    pygame.display.set_icon(pygame.image.load("icon.png"))

    #
    # Create layered window
    hwnd = pygame.display.get_wm_info()["window"]
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                           win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TOOLWINDOW)
    fuchsia = (255, 0, 128)
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)
    SetWindowPos(pygame.display.get_wm_info()['window'], win32con.HWND_TOPMOST, 0,0,0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    # Create lizard
    lizard = Lizard(pygame.math.Vector2(WIDTH // 2, HEIGHT // 2))
    tray_thread = SystemTrayThread(lizard)
    tray_thread.start()
    # Main game loop
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                lizard.transparent = not lizard.transparent

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button click
                mouse_pos = pygame.mouse.get_pos()
                if lizard.position.distance_to(pygame.math.Vector2(mouse_pos)) < 50:  # Click within 50 pixels of the lizard
                    lizard.fleeing = True
                    lizard.state = "fleeing"

        screen.fill(fuchsia)  # Transparent background

        if lizard_mode == "follow":
            lizard.follow(pygame.math.Vector2(get_global_mouse_pos()))
        else:
            lizard.update(WIDTH, HEIGHT)
        lizard.draw(screen)

        if show_ram_fps:
            # Calculate and display FPS
            fps = clock.get_fps()
            fps_text = font.render(f"FPS: {fps:.0f}", True, (255, 255, 255))
            screen.blit(fps_text, (10, 10))

            # Calculate and display RAM usage
            ram_usage = get_ram_usage()
            ram_text = font.render(f"RAM: {ram_usage:.2f} MB", True, (255, 255, 255))
            screen.blit(ram_text, (10, 50))


        pygame.display.flip()
        clock.tick(60)


    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()