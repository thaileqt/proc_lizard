import tkinter as tk
from tkinter import ttk
import math
import pygame



class LizardConfig:
    DEFAULT_SPEED = 2
    DEFAULT_FLEE_SPEED = DEFAULT_SPEED * 3
    DEFAULT_FLEE_DISTANCE = 300
    DEFAULT_TURN_SPEED = 0.05
    DEFAULT_ANGLE_CONSTRAINT = math.pi / 8

    DEFAULT_SHADOW_WIDTH = 2
    DEFAULT_LEG_WIDTH = 5

    def __init__(self, lizard):
        self.lizard = lizard
        self.turn_speed = lizard.turn_speed
        self.speed = lizard.speed
        self.angle_constraint = lizard.angle_constraint
        self.config_window = None

    def show_config_dialog(self):
        if self.config_window is None:
            self.config_window = ConfigWindow(self)
        self.config_window.mainloop()

    def update_lizard_stats(self):
        self.lizard.turn_speed = self.turn_speed
        self.lizard.speed = self.speed
        self.lizard.angle_constraint = self.angle_constraint

class ConfigWindow(tk.Tk):
    def __init__(self, lizard_config):
        super().__init__()
        self.lizard_config = lizard_config
        self.title("Lizark Configuration")

        # Create the UI elements with min, max, and current value labels
        self.turn_speed_var = tk.DoubleVar(value=lizard_config.turn_speed)
        self.speed_var = tk.DoubleVar(value=lizard_config.speed)
        self.angle_constraint_var = tk.DoubleVar(value=lizard_config.angle_constraint)

        # Turn Speed
        turn_speed_label = ttk.Label(self, text="Turn Speed:")
        turn_speed_label.grid(row=0, column=0, padx=10, pady=10)

        turn_speed_min_label = ttk.Label(self, text="0.01")
        turn_speed_min_label.grid(row=0, column=1, padx=5, pady=10)

        turn_speed_slider = ttk.Scale(self, variable=self.turn_speed_var, from_=0.01, to=0.2, orient=tk.HORIZONTAL,
                                      command=self.update_turn_speed_value)
        turn_speed_slider.grid(row=0, column=2, padx=5, pady=10)

        turn_speed_max_label = ttk.Label(self, text="0.2")
        turn_speed_max_label.grid(row=0, column=3, padx=5, pady=10)

        self.turn_speed_value_label = ttk.Label(self, text=f"{self.turn_speed_var.get():.2f}")
        self.turn_speed_value_label.grid(row=0, column=4, padx=5, pady=10)

        # Speed
        speed_label = ttk.Label(self, text="Speed:")
        speed_label.grid(row=1, column=0, padx=10, pady=10)

        speed_min_label = ttk.Label(self, text="1")
        speed_min_label.grid(row=1, column=1, padx=5, pady=10)

        speed_slider = ttk.Scale(self, variable=self.speed_var, from_=1, to=5, orient=tk.HORIZONTAL,
                                 command=self.update_speed_value)
        speed_slider.grid(row=1, column=2, padx=5, pady=10)

        speed_max_label = ttk.Label(self, text="5")
        speed_max_label.grid(row=1, column=3, padx=5, pady=10)

        self.speed_value_label = ttk.Label(self, text=f"{self.speed_var.get():.2f}")
        self.speed_value_label.grid(row=1, column=4, padx=5, pady=10)

        # Angle Constraint
        angle_constraint_label = ttk.Label(self, text="Angle Constraint:")
        angle_constraint_label.grid(row=2, column=0, padx=10, pady=10)

        angle_constraint_min_label = ttk.Label(self, text="0.01")
        angle_constraint_min_label.grid(row=2, column=1, padx=5, pady=10)

        angle_constraint_slider = ttk.Scale(self, variable=self.angle_constraint_var, from_=0.01, to=math.pi / 4,
                                            orient=tk.HORIZONTAL, command=self.update_angle_constraint_value)
        angle_constraint_slider.grid(row=2, column=2, padx=5, pady=10)

        angle_constraint_max_label = ttk.Label(self, text=f"{round(math.pi / 4, 2)}")
        angle_constraint_max_label.grid(row=2, column=3, padx=5, pady=10)

        self.angle_constraint_value_label = ttk.Label(self, text=f"{self.angle_constraint_var.get():.2f}")
        self.angle_constraint_value_label.grid(row=2, column=4, padx=5, pady=10)

        # Apply Button
        apply_button = ttk.Button(self, text="Apply", command=self.apply_changes)
        reset_button = ttk.Button(self, text="Reset", command=self.reset_changes)
        apply_button.grid(row=3, column=1, columnspan=2, padx=10, pady=10)
        reset_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def update_turn_speed_value(self, value):
        self.turn_speed_value_label.config(text=f"{float(value):.2f}")

    def update_speed_value(self, value):
        self.speed_value_label.config(text=f"{float(value):.2f}")

    def update_angle_constraint_value(self, value):
        self.angle_constraint_value_label.config(text=f"{float(value):.2f}")

    def apply_changes(self):
        self.lizard_config.turn_speed = self.turn_speed_var.get()
        self.lizard_config.speed = self.speed_var.get()
        self.lizard_config.angle_constraint = self.angle_constraint_var.get()
        self.lizard_config.update_lizard_stats()

        self.lizard_config.config_window = None
        self.destroy()

    def reset_changes(self):
        self.turn_speed_var.set(LizardConfig.DEFAULT_TURN_SPEED)
        self.speed_var.set(LizardConfig.DEFAULT_SPEED)
        self.angle_constraint_var.set(LizardConfig.DEFAULT_ANGLE_CONSTRAINT)
        self.update_turn_speed_value(LizardConfig.DEFAULT_TURN_SPEED)
        self.update_speed_value(LizardConfig.DEFAULT_SPEED)
        self.update_angle_constraint_value(LizardConfig.DEFAULT_ANGLE_CONSTRAINT)