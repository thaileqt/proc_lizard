import math
import win32gui
from PIL import Image, ImageDraw


def constrain_angle(angle, anchor, constraint):
    diff = (angle - anchor + math.pi) % (2 * math.pi) - math.pi
    if abs(diff) <= constraint:
        return angle
    elif diff > constraint:
        return anchor + constraint
    else:
        return anchor - constraint

def get_global_mouse_pos():
    return win32gui.GetCursorPos()
