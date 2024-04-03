import enemies
import numpy as np

from speed_buff_item import speed_buff

#todo:
# make enemies notspawn on player pos

MAX_WAVE_SIZE = 350
START_WAVE_SIZE = 10
WAVE_SIZE_INCREASE = 5
WAVE_SIZE_INCREASE_MULTIPLYER = 1.1
SPAWN_DELAY = 60

ITEM_SIZE = (10, 10)

class wave_spawner():
    def __init__(self, player, collision_map, screen, frame_sets):
        self.wave_size = START_WAVE_SIZE
        self.wave_size_increase = WAVE_SIZE_INCREASE
        self.wave_size_increase_multiplyer = WAVE_SIZE_INCREASE_MULTIPLYER
        self.max_wave_size = MAX_WAVE_SIZE
        self.item_size = ITEM_SIZE

        self.frame_sets = frame_sets

        self.player = player
        self.screen = screen
        self.collision_map = collision_map
        self.width, self.height = screen.get_size()

        self.spawn_delay = SPAWN_DELAY
        self.current_spawn_delay = 0

    def _incement_wave_size(self):
        if self.max_wave_size <= self.wave_size:
            self.wave_size = self.max_wave_size
            return 
        
        self.wave_size_increase *= self.wave_size_increase_multiplyer
        self.wave_size += int(self.wave_size_increase)
        

    def spawn_wave(self):
        if self.current_spawn_delay < self.spawn_delay:
            self.current_spawn_delay += 1
            return [], []
        
        self.current_spawn_delay = 0
        entities = []
        items = []
        for i in range(self.wave_size):
            if np.random.rand() > 0.5:
                e = enemies.cow(self.player, (np.random.randint(0, self.width), np.random.randint(0, self.height)), self.screen, (self.width, self.height), self.frame_sets["cow"][0], self.frame_sets["cow"][1])
            else:
                e = enemies.chicken(self.player, (np.random.randint(0, self.width), np.random.randint(0, self.height)), self.screen, (self.width, self.height), self.frame_sets["chicken"][0], self.frame_sets["chicken"][1])
            self.collision_map.add_rect(e.get_rect(), e)
            entities.append(e)
        
        for i in range(np.random.randint(0, 3)):
           s_item = speed_buff(self.player, (np.random.randint(0, self.width), np.random.randint(0, self.height)), self.item_size, self.screen, (0, 0, 150))
           self.collision_map.add_rect(s_item.get_rect(), s_item)
           items.append(s_item)

        self._incement_wave_size()

        return entities, items