import math

def constrain_angle(angle, anchor, constraint):
    diff = (angle - anchor + math.pi) % (2 * math.pi) - math.pi
    if abs(diff) <= constraint:
        return angle
    elif diff > constraint:
        return anchor + constraint
    else:
        return anchor - constraint