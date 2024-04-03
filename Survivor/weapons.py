from base_classes import weapon

#TODO
# add more weapons
# make weapon points centered around player

class machine_gun(weapon):
    def __init__(self, player, screen, frame_set):
        shooting_delay = 5
        min_shooting_delay = 1
        damage = 1
        bullet_force = 25
        super().__init__(player, screen, shooting_delay, damage, min_shooting_delay, frame_set, bullet_force)


class pistol(weapon):
    def __init__(self, player, screen, frame_set):
        shooting_delay = 10
        min_shooting_delay = 8
        damage = 5
        bullet_force = 50
        super().__init__(player, screen, shooting_delay, damage, min_shooting_delay, frame_set, bullet_force)