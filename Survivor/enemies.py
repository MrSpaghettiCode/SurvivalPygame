import numpy as np
import pygame
from base_classes import enemy


class chicken(enemy):
    def __init__(self, player, point, screen, bounds, frame_set, size):
        mass = np.random.randint(4, 14) + np.random.rand()
        hp = 5
        enemy.__init__(self, point, size, mass, screen, bounds, player, frame_set, hp, blood_drop=8)

        self.speed = np.random.randint(5, 20) * 0.01




class cow(enemy):
    def __init__(self, player, point, screen, bounds, frame_set, size):
        mass = np.random.randint(20, 30) + np.random.rand()
        hp = 10
        enemy.__init__(self, point, size, mass, screen, bounds, player, frame_set, hp, exp_drop=4, blood_drop=16)

        self.speed = np.random.randint(4, 15) * 0.01