import pygame
import random
import math
from utils import constrain_angle
from config import LizardConfig


SHADOW_COLOR = (0, 0, 0, 0)  # TODO: Transparency not working
SHADOW_OFFSET = pygame.math.Vector2(5, 5)

class Lizard:
    BODY_COLOR = (82, 121, 111)
    EYE_COLOR = (255, 255, 255)
    HEAD_COLOR = (60, 90, 80, 200)

    def __init__(self, position):
        self.position = position
        self.spine = [position.copy()]
        self.spine_angles = [0]
        self.body_width = [16, 18, 12, 18, 20, 22, 20, 15, 8, 4, 3, 3, 2, 2]
        self.segment_length = 20

        self.angle_constraint = LizardConfig.DEFAULT_ANGLE_CONSTRAINT
        self.speed = LizardConfig.DEFAULT_SPEED
        self.turn_speed = LizardConfig.DEFAULT_TURN_SPEED

        for _ in range(13):
            self.spine.append(self.spine[-1] + pygame.math.Vector2(0, self.segment_length))
            self.spine_angles.append(0)

        self.legs = [Leg(self, i) for i in range(4)]
        self.target = pygame.math.Vector2(random.randint(0, 800), random.randint(0, 600))


        self.heading = 0
        self.tail_phase = 0
        self.state = "moving"
        self.state_timer = 0
        self.look_around_angle = 0
        self.blink_timer = 0
        self.tongue_out = False
        self.tongue_timer = 0

        self.fleeing = False
        self.flee_target = None
        self.flee_speed = LizardConfig.DEFAULT_FLEE_SPEED
        self.flee_distance = LizardConfig.DEFAULT_FLEE_DISTANCE

    def update(self, width, height):
        self.state_timer += 1

        if self.state == "moving":
            self._move(width, height)
            if self.state_timer > random.randint(100, 200):
                self.state = "stopping"
                self.state_timer = 0
        elif self.state == "fleeing":
            self._flee()
        elif self.state == "stopping":
            if self.state_timer > random.randint(50, 100):
                self.state = "looking"
                self.state_timer = 0
                self.look_around_angle = random.uniform(-math.pi / 4, math.pi / 4)
        elif self.state == "looking":
            self._look_around()
            if self.state_timer > random.randint(50, 100):
                self.state = "moving"
                self.state_timer = 0
                self.target = pygame.math.Vector2(random.randint(0, width), random.randint(0, height))

        self._update_spine()
        self._update_legs()
        self._update_blinking()
        self._update_tongue()

    def _move(self, width, height):
        direction = self.target - self.position
        if direction.length() < 10:
            self.target = pygame.math.Vector2(random.randint(0, width), random.randint(0, height))
        else:
            target_angle = math.atan2(direction.y, direction.x)
            angle_diff = (target_angle - self.heading + math.pi) % (2 * math.pi) - math.pi
            if abs(angle_diff) > self.turn_speed:
                self.heading += self.turn_speed * (1 if angle_diff > 0 else -1)
            else:
                self.heading = target_angle

            move = pygame.math.Vector2(math.cos(self.heading), math.sin(self.heading)) * self.speed
            self.position += move

    def _flee(self):
        if self.flee_target is None:
            # Calculate a flee target that is a certain distance away from the lizard's current position
            flee_direction = pygame.math.Vector2(math.cos(self.heading), math.sin(self.heading))
            self.flee_target = self.position + flee_direction * self.flee_distance

        # Calculate the direction towards the flee target
        direction = self.flee_target - self.position
        direction.normalize_ip()

        # Smoothly rotate the lizard's heading towards the flee direction
        target_angle = math.atan2(direction.y, direction.x)
        angle_diff = (target_angle - self.heading + math.pi) % (2 * math.pi) - math.pi
        if abs(angle_diff) > self.turn_speed:
            self.heading += self.turn_speed * (1 if angle_diff > 0 else -1)
        else:
            self.heading = target_angle

        # Move the lizard in the flee direction
        self.position += direction * self.flee_speed

        # Check if the lizard has reached the flee target
        if (self.position - self.flee_target).length() < 10:
            self.fleeing = False
            self.flee_target = None
            self.state = "moving"
    def _look_around(self):
        self.heading += math.sin(self.state_timer * 0.1) * 0.02 * self.look_around_angle

    def _update_spine(self):
        self.spine[0] = self.position
        self.spine_angles[0] = self.heading

        for i in range(1, len(self.spine)):
            cur_angle = math.atan2(self.spine[i - 1].y - self.spine[i].y, self.spine[i - 1].x - self.spine[i].x)
            self.spine_angles[i] = constrain_angle(cur_angle, self.spine_angles[i - 1], self.angle_constraint)
            offset = pygame.math.Vector2(math.cos(self.spine_angles[i]),
                                         math.sin(self.spine_angles[i])) * self.segment_length
            self.spine[i] = self.spine[i - 1] - offset

        # Tail animation
        self.tail_phase += 0.1
        for i in range(7, len(self.spine)):
            self.spine_angles[i] += math.sin(self.tail_phase + i * 0.5) * 0.05

    def _update_legs(self):
        for leg in self.legs:
            leg.update()

    def _update_blinking(self):
        self.blink_timer += 1
        if self.blink_timer > random.randint(100, 200):
            self.blink_timer = 0

    def _update_tongue(self):
        if not self.tongue_out and random.random() < 0.005:
            self.tongue_out = True
            self.tongue_timer = 0
        if self.tongue_out:
            self.tongue_timer += 1
            if self.tongue_timer > 20:
                self.tongue_out = False

    def draw(self, screen):
        self._draw_shadow(screen)

        # Draw legs
        for leg in self.legs:
            leg.draw(screen)

        # Draw body
        points = []
        for i, joint in enumerate(self.spine):
            points.append(self.get_body_point(i, math.pi / 2))
        for i in range(len(self.spine) - 1, -1, -1):
            points.append(self.get_body_point(i, -math.pi / 2))

        pygame.draw.polygon(screen, self.BODY_COLOR, points)

        # Draw pattern
        pattern_points = [points[0], points[1], points[-2], points[-1]]
        pygame.draw.polygon(screen, self.HEAD_COLOR, pattern_points)

        # Draw eyes
        eye_pos1 = self.get_body_point(0, 3 * math.pi / 5, -2)
        eye_pos2 = self.get_body_point(0, -3 * math.pi / 5, -2)

        if self.blink_timer < 5:
            pygame.draw.line(screen, (0, 0, 0), (eye_pos1[0] - 3, eye_pos1[1]), (eye_pos1[0] + 3, eye_pos1[1]), 2)
            pygame.draw.line(screen, (0, 0, 0), (eye_pos2[0] - 3, eye_pos2[1]), (eye_pos2[0] + 3, eye_pos2[1]), 2)
        else:
            pygame.draw.circle(screen, self.EYE_COLOR, eye_pos1, 4)
            pygame.draw.circle(screen, self.EYE_COLOR, eye_pos2, 4)
            pygame.draw.circle(screen, (0, 0, 0), eye_pos1, 2)
            pygame.draw.circle(screen, (0, 0, 0), eye_pos2, 2)

        # Draw tongue
        if self.tongue_out:
            tongue_start = self.get_body_point(0, 0, -4)
            tongue_end = tongue_start + pygame.math.Vector2(math.cos(self.heading), math.sin(self.heading)) * 15
            pygame.draw.line(screen, (255, 0, 0), tongue_start, tongue_end, 2)



    def get_body_point(self, i, angle_offset, length_offset=0):
        angle = self.spine_angles[i] + angle_offset
        offset = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * (self.body_width[i] + length_offset)
        point = self.spine[i] + offset
        return (int(point.x), int(point.y))

    def _draw_shadow(self, screen: pygame.Surface):
        shadow_points = []
        for i, joint in enumerate(self.spine):
            shadow_points.append(self.get_body_point(i, math.pi / 2, length_offset=LizardConfig.DEFAULT_SHADOW_WIDTH) + SHADOW_OFFSET)
        for i in range(len(self.spine) - 1, -1, -1):
            shadow_points.append(self.get_body_point(i, -math.pi / 2, length_offset=LizardConfig.DEFAULT_SHADOW_WIDTH) + SHADOW_OFFSET)

        pygame.draw.polygon(screen, SHADOW_COLOR,shadow_points)


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
        shadow_points = [(int(joint.x + SHADOW_OFFSET.x), int(joint.y + SHADOW_OFFSET.y)) for joint in self.joints]
        pygame.draw.lines(screen, SHADOW_COLOR, False, shadow_points, LizardConfig.DEFAULT_LEG_WIDTH + LizardConfig.DEFAULT_SHADOW_WIDTH)

        pygame.draw.lines(screen, self.lizard.BODY_COLOR, False,
                          [(int(joint.x), int(joint.y)) for joint in self.joints], LizardConfig.DEFAULT_LEG_WIDTH)
