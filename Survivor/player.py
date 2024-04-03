import pygame
from base_classes import drawable, physics_processor, hitbox, bullet, animation_handler

def load_transform_image(path, size):
    return pygame.transform.scale(pygame.image.load(path), size).convert_alpha()

def load_player_frames(size):
    f = {"up": [], "left": [], "right": [], "forward": []}
    for i in range(1, 4):
        f["up"].append(load_transform_image(f"assets/player/up_{i}.png", size))
        f["left"].append(load_transform_image(f"assets/player/left_{i}.png", size))
        f["right"].append(load_transform_image(f"assets/player/right_{i}.png", size))
        f["forward"].append(load_transform_image(f"assets/player/forward_{i}.png", size))

    return f
#TODO.
# make player invincible if he gets it
# center player various fields (grav, range)
# maybe give player a force shield, that prevents enemies from geetting too close

MASS = 30
SPEED = 4
SIZE = (40, 55)
HP = 8
EXP_FOR_LEVELUP = 10
INITIAL_HP_REG = 0.05

class player_controller(drawable, physics_processor, animation_handler):
    def __init__(self, point, screen, bounds):
        drawable.__init__(self, point, SIZE, screen, (0, 200, 0))
        physics_processor.__init__(self, point, MASS, bounds, SIZE)
        self.max_vel = 500
        animation_delay = 8
        frame_set = load_player_frames(SIZE)
        animation_handler.__init__(self, frame_set, frame_set["forward"], animation_delay)

        self.speed = SPEED

        self.max_hp = HP
        self.hp = self.max_hp
        self.hp_reg_delay = 60
        self.current_hp_reg_delay = 0
        self.hp_reg = 0.05
        self.alive = True
        self.active_bullets = []
        self.weapons = []
        self.max_weapons = 6
        self.current_weapon_index = 0
        self.weapon_points = [(40, 40),(60, 0),(40, -40), (-40, -40), (-60, 0), (-40, 40)]

        self.experience_for_levelup = EXP_FOR_LEVELUP
        self.experience = 0
        self.level = 1

        #set in method below
        self.grav_x = 0
        self.grav_y = 0
        self.grav_width = 0
        self.grav_height = 0
        self.grav_field = hitbox((self.grav_x, self.grav_y), (self.width, self.grav_height))

        #set in method below
        self.sr_mult = 1
        self.sr_x = 0
        self.sr_y = 0
        self.sr_width = 0
        self.sr_height = 0
        self.shooting_range = hitbox((self.sr_x, self.sr_y), (self.sr_width, self.sr_height))

        self.has_levelup = False
        self.move_up = False
        self.move_down = False
        self.move_left = False
        self.move_right = False

    def add_weapon(self, weapon):
        if len(self.weapons) >= self.max_weapons:
            return
        
        self.weapons.append(weapon)
        wp = self.weapon_points[self.current_weapon_index]
        weapon.player_offset = (wp[0]+self.width*0.25, wp[1]+self.height*0.25)
        self.current_weapon_index += 1

    def level_up(self):
        self.has_levelup = True
        self.experience = 0
        self.level += 1
        self.experience_for_levelup *= 1.2
        
    def increase_hp(self, ammount):
        self.max_hp += ammount
        self.hp += ammount

    def increase_hp_reg(self, ammount):
        self.hp_reg += ammount

    def take_experience(self, ammount):
        self.experience += ammount

        if self.experience >= self.experience_for_levelup:
            self.level_up()

    def increase_shooting_range(self, ammount=1):
        self.sr_mult += ammount

    def take_damage(self, ammount=1):
        if self.hp > 1:
            self.hp -= ammount
            #print("player took damage, hp: ", self.hp)
            return
        
        print("you ded")
        self.alive = False

    def shoot(self, target):
        for weapon in self.weapons:
            yield weapon.shoot(target)
            
    def set_shootin_range_position(self):
        self.sr_x = self.x - (self.width*1) * self.sr_mult
        self.sr_y = self.y - (self.height*0.75) * self.sr_mult
        self.sr_width = self.width*2*self.sr_mult
        self.sr_height = self.height*1.5*self.sr_mult

        self.shooting_range.width = self.sr_width
        self.shooting_range.height = self.sr_height
        self.shooting_range.x = self.sr_x
        self.shooting_range.y = self.sr_y

    def set_grav_field_pos(self):
        self.grav_x = self.x - self.width*3
        self.grav_y = self.y - self.height*3
        self.grav_width = self.width*8
        self.grav_height = self.height*8

        self.grav_field.width = self.grav_width
        self.grav_field.height = self.grav_height
        self.grav_field.x = self.grav_x
        self.grav_field.y = self.grav_y

    def stop_moving(self):
        self.move_down = False
        self.move_up = False
        self.move_left = False
        self.move_right = False

    def move(self):
        if self.move_left:
            self.set_frame_set("left")
            self.apply_force(-self.speed, 0)
        elif self.move_right:
            self.set_frame_set("right")
            self.apply_force(self.speed, 0)

        if self.move_up:
            self.set_frame_set("up")
            self.apply_force(0, -self.speed)
        elif self.move_down:
            self.set_frame_set("forward")
            self.apply_force(0, self.speed)

        self.set_grav_field_pos()
        self.set_shootin_range_position()

        self.current_hp_reg_delay += 1
        if self.hp < self.max_hp:
            if self.current_hp_reg_delay > self.hp_reg_delay:
                self.hp += self.hp_reg
                self.current_hp_reg_delay = 0

        for weapon in self.weapons:
            weapon.current_shooting_delay += 1
            weapon.x = self.x + weapon.player_offset[0]
            weapon.y = self.y + weapon.player_offset[1]

        

        super().move()

    def draw(self):
        super().draw_frame(self.next_frame())