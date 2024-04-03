from base_classes import item

class speed_buff(item):
    def __init__(self, player, coords, size, screen, color):
        super().__init__(player ,coords, size, screen, color)

        self.strength = 0.1

    def buff_speed(self):
        self.player.speed += self.strength
