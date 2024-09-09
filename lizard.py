import pygame
import random
import math
from utils import constrain_angle

class Lizard:
    BODY_COLOR = (82, 121, 111)
    EYE_COLOR = (255, 255, 255)

    def __init__(self, position):
        self.position = position
        self.spine = [position.copy()]
        self.spine_angles = [0]
        self.body_width = [16, 18, 12, 18, 20, 22, 20, 15, 8, 4, 3, 3, 2, 2]
        self.segment_length = 20
        self.angle_constraint = math.pi / 8

        for _ in range(13):
            self.spine.append(self.spine[-1] + pygame.math.Vector2(0, self.segment_length))
            self.spine_angles.append(0)

        self.legs = [Leg(self, i) for i in range(4)]
        self.target = pygame.math.Vector2(random.randint(0, 800), random.randint(0, 600))
        self.speed = 2
        self.heading = 0  # New: current heading of the lizard
        self.turn_speed = 0.05  # New: how fast the lizard can turn (in radians per frame)

    def update(self, width, height):
        # Update spine
        direction = self.target - self.position
        if direction.length() < 10:
            self.target = pygame.math.Vector2(random.randint(0, width), random.randint(0, height))
        else:
            # New: Gradually turn towards the target
            target_angle = math.atan2(direction.y, direction.x)
            angle_diff = (target_angle - self.heading + math.pi) % (2 * math.pi) - math.pi
            if abs(angle_diff) > self.turn_speed:
                self.heading += self.turn_speed * (1 if angle_diff > 0 else -1)
            else:
                self.heading = target_angle

            # Move in the current heading direction
            move = pygame.math.Vector2(math.cos(self.heading), math.sin(self.heading)) * self.speed
            self.position += move

        self.spine[0] = self.position
        self.spine_angles[0] = self.heading  # Use the current heading for the first spine segment

        for i in range(1, len(self.spine)):
            cur_angle = math.atan2(self.spine[i - 1].y - self.spine[i].y, self.spine[i - 1].x - self.spine[i].x)
            self.spine_angles[i] = constrain_angle(cur_angle, self.spine_angles[i - 1], self.angle_constraint)
            offset = pygame.math.Vector2(math.cos(self.spine_angles[i]),
                                         math.sin(self.spine_angles[i])) * self.segment_length
            self.spine[i] = self.spine[i - 1] - offset

        # Update legs
        for leg in self.legs:
            leg.update()

    def draw(self, screen):
        # Draw body
        points = []
        for i, joint in enumerate(self.spine):
            points.append(self.get_body_point(i, math.pi/2))
        for i in range(len(self.spine) - 1, -1, -1):
            points.append(self.get_body_point(i, -math.pi/2))
        pygame.draw.polygon(screen, self.BODY_COLOR, points)

        # Draw eyes
        pygame.draw.circle(screen, self.EYE_COLOR, self.get_body_point(0, 3*math.pi/5, -2), 4)
        pygame.draw.circle(screen, self.EYE_COLOR, self.get_body_point(0, -3*math.pi/5, -2), 4)

        # Draw legs
        for leg in self.legs:
            leg.draw(screen)

    def get_body_point(self, i, angle_offset, length_offset=0):
        angle = self.spine_angles[i] + angle_offset
        offset = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * (self.body_width[i] + length_offset)
        point = self.spine[i] + offset
        return (int(point.x), int(point.y))

class Leg:
    def __init__(self, lizard, index):
        self.lizard = lizard
        self.index = index
        self.side = 1 if index % 2 == 0 else -1
        self.body_index = 3 if index < 2 else 7
        self.angle = math.pi/4 if index < 2 else math.pi/3
        self.length = 16
        self.segments = 3
        self.joints = [pygame.math.Vector2() for _ in range(self.segments + 1)]
        self.target = pygame.math.Vector2()

    def update(self):
        # Update leg anchor point
        self.joints[0] = pygame.math.Vector2(self.lizard.get_body_point(self.body_index, self.side * math.pi/2, -6))

        # Update leg target
        new_target = pygame.math.Vector2(self.lizard.get_body_point(self.body_index, self.side * self.angle, 25))
        if (new_target - self.target).length() > 60:
            self.target = new_target

        # Inverse Kinematics
        for _ in range(5):  # Iterations for IK solver
            # Forward reaching
            self.joints[-1] = self.target
            for i in range(self.segments - 1, 0, -1):
                dir = (self.joints[i] - self.joints[i+1]).normalize()
                self.joints[i] = self.joints[i+1] + dir * self.length

            # Backward reaching
            self.joints[0] = pygame.math.Vector2(self.lizard.get_body_point(self.body_index, self.side * math.pi/2, -6))
            for i in range(self.segments):
                dir = (self.joints[i+1] - self.joints[i]).normalize()
                self.joints[i+1] = self.joints[i] + dir * self.length

    def draw(self, screen):
        pygame.draw.lines(screen, self.lizard.BODY_COLOR, False, [(int(joint.x), int(joint.y)) for joint in self.joints], 4)