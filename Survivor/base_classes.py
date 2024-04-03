import pygame
import numpy as np

#TODO:
# make bullets fly at specific speed, regardless of target position
class point():
    def __init__(self, point):
        self.x, self.y = point

class drawable(point):
    def __init__(self, coords, size, screen, color):
        point.__init__(self, coords)
        self.width, self.height = size
        self.screen = screen
        self.color = color

    def draw(self):
        pygame.draw.rect(self.screen, self.color, (self.x, self.y, self.width, self.height))
        
    def draw_frame(self, frame, angle = 0):
        if angle != 0:
            frame = pygame.transform.rotate(frame, 360-angle)
        self.screen.blit(frame, (self.x, self.y))

class hitbox(point):
    def __init__(self, coords, size):
        point.__init__(self, coords)
        self.width, self.height = size

    def get_rect(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def collides_with(self, other_hitbox):
        if self.x < other_hitbox.x + other_hitbox.width and self.x + self.width > other_hitbox.x:
            return self.y < other_hitbox.y + other_hitbox.height and self.y + self.height > other_hitbox.y
        return False

    def on_bounds_bottom(self, bounds):
        return self.y + self.height >= bounds[1]
    
    def out_of_bounds(self, bounds):
        return self.x < 5 or self.x + self.width > bounds[0]-self.width or self.y < 5 or self.y + self.height > bounds[1]-self.height

class physics_processor(hitbox):
    def __init__(self, point, mass, bounds, size, bouncy = False):
        super().__init__(point, size)
        self.mass = mass * 0.01
        self.bounds = bounds
        self.bouncy = bouncy

        self.max_vel = np.random.randint(10, 30)
        self.x_vel, self.y_vel = 0, 0
        self.vel_dec = 1-(0.9 * self.mass)


    def apply_force(self, force_x, force_y = 0):
        if self.x_vel < self.max_vel and self.x_vel > -self.max_vel:
            self.x_vel += force_x
        if self.y_vel < self.max_vel and self.y_vel > -self.max_vel:
            self.y_vel += force_y

    def apply_colision_force(self, x_vel, y_vel, mass):
         coll_force = (((x_vel*0.2)*(mass))*np.random.rand(), ((y_vel*0.2)*(mass))*np.random.rand())

         self.apply_force(coll_force[0], coll_force[1])
  
    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

        #reset pos to bounds
        #without this, the entity sometimes gets off screen, even with reversed veloticy
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > self.bounds[0]:
            self.x = self.bounds[0] - self.width

        if self.y < 0:
            self.y = 0
        elif self.y + self.height > self.bounds[1]:
            self.y = self.bounds[1] - self.height

        #bounce off of screen bounds
        if self.bouncy:
            if self.x <= 0 or self.x + self.width >= self.bounds[0]:
                 self.x_vel = -self.x_vel
            if self.y <= 0:
                self.y_vel = -self.y_vel
            if self.y + self.height >= self.bounds[1]:
                self.y_vel = -self.y_vel
        
        #make velocity go down over time
        self.x_vel *= self.vel_dec
        self.y_vel *= self.vel_dec

class animation_handler():
    def __init__(self, frame_set, start_set, delay, concurrent_frame = None):
        self.frame_set = frame_set
        self.frames = start_set
        self.concurrent_frame = concurrent_frame
        self.length = 0

        self.delay = delay
        self.current_frame = 0
        self.current_delay = 0

    def get_current_frame(self):
        return self.frames[self.current_frame]

    def next_frame(self):
        if self.current_delay < self.delay:
            self.current_delay += 1
            return self.frames[self.current_frame]
        
        self.current_delay = 0
        self.current_frame += 1
        if self.current_frame > len(self.frames)-1:
            self.current_frame = 0
        return self.frames[self.current_frame]
    
    def set_frame_set(self, set_name):
        self.frames = self.frame_set[set_name]
        self.length = len(self.frames)

class enemy(drawable, physics_processor, animation_handler):
    def __init__(self, point, size, mass, screen, bounds, player, frame_set, hp = 5, color=(200, 0, 0), exp_drop = 2, exp_value = 1, blood_drop = 2):
        drawable.__init__(self, point, size, screen, color)
        physics_processor.__init__(self, point, mass, bounds, size)
        animation_handler.__init__(self, frame_set, frame_set["left"], 5)
        self.player = player
        self.alive = True
        self.hp = hp
        self.blood_drop = blood_drop
        self.experience = []
        self.rand_move_offset = 0.3
        for i in range(exp_drop):
            exp = experience(player, (self.x, self.y), screen, exp_value)
            self.experience.append(exp)

    def move_to_player(self):
        if self.x < self.player.x:
            if self.frames != self.frame_set["left"]:
                self.set_frame_set("left")
            self.apply_force(self.speed, 0)
            self.apply_force(np.random.uniform(-self.rand_move_offset, self.rand_move_offset), 0)
        elif self.x > self.player.x:
            if self.frames != self.frame_set["right"]:
                self.set_frame_set("right")
            self.apply_force(-self.speed, 0)
            self.apply_force(np.random.uniform(-self.rand_move_offset, self.rand_move_offset), 0)
        if self.y < self.player.y:
            self.apply_force(0, self.speed)
            self.apply_force(0, np.random.uniform(-self.rand_move_offset, self.rand_move_offset))
        elif self.y > self.player.y:
            self.apply_force(0, -self.speed)
            self.apply_force(0, np.random.uniform(-self.rand_move_offset, self.rand_move_offset))

        super().move()

    def take_damage(self, ammount=1):
        if self.hp > 1:
            self.hp -= ammount
            return
        
        for i in range(len(self.experience)):
            self.experience[i].x = self.x + (i * 5)*np.random.rand()
            self.experience[i].y = self.y + (i * 5)*np.random.rand()
        
        self.alive = False

    def draw(self):
        super().draw_frame(self.next_frame())

#TODO
# add check for changing set lengths


class item(drawable, physics_processor):
    def __init__(self, player, coords, size, screen, color, gravitate_to_player = False):
        drawable.__init__(self, coords, size, screen, color)
        physics_processor.__init__(self, coords, 10, screen.get_size(), size)
        self.player = player
        self.gravitate_to_player = gravitate_to_player

        self.speed = 0.5

    def add_to_inventory(self):
        self.player.inventory.append(self)

    def move_to_player(self):
        if not self.gravitate_to_player:
            super().move()
            return
        
        if self.x < self.player.x:
            self.apply_force(self.speed, 0)
        elif self.x > self.player.x:
            self.apply_force(-self.speed, 0)
        if self.y < self.player.y:
            self.apply_force(0, self.speed)
        elif self.y > self.player.y:
            self.apply_force(0, -self.speed)

        super().move()

class experience(item):
    def __init__(self, player, coords, screen, ammount):
        size = (6, 6)
        super().__init__(player, coords, size, screen, (255, 255, 0), False)
        self.ammount = ammount

        self.mass = 1 + np.random.rand()
        self.speed = 1

    def move(self):
        super().move_to_player()

class blood(physics_processor, drawable):
    def __init__(self, coords, screen, containing_list):
        coords = (coords[0]+np.random.uniform(-1, 1), coords[1]+np.random.uniform(-1, 1))
        size = (3, 3)
        color = (255, 0, 0)
        drawable.__init__(self, coords, size, screen, color)
        physics_processor.__init__(self, coords, 20, screen.get_size(), size)

        self.containing_list = containing_list
        self.speed = 1 + np.random.rand()
        spread = 3+np.random.rand()
        self.color_dec = np.random.randint(1, 5)
        self.apply_force(np.random.randint(-spread, spread), np.random.randint(-spread, spread))

    def decay_color(self):
        r = self.color[0]
        r-=self.color_dec
        self.color=(r, 0, 0)

    def move(self):
        self.decay_color()
        if self.color[0] < 100:
            self.containing_list.remove(self)
            return

        super().move()

class bullet(drawable, physics_processor):
    def __init__(self, player, coords, screen, target, damage, impact_force):
        size = (4, 4)
        color = (255, 186, 52)
        drawable.__init__(self, coords, size, screen, color)
        physics_processor.__init__(self, coords, 90, screen.get_size(), size)
        self.player = player
        self.target = target
        self.bound = screen.get_size()
        self.impact_force = impact_force
        self.damage = damage

        self.target_dead = False
        self.x_vel = 0
        self.y_vel = 0

        self.last_x_vel, self.lasty_vel = 0, 0
        self.speed = 0.04
        self.vel_set = False
    
    def remove_from_pool(self):
        self.player.active_bullets.remove(self)

    def move(self):
        if self.out_of_bounds(self.bound):
            self.remove_from_pool()
            return
       
        if self.vel_set:
            self.apply_force(self.last_x_vel, self.last_y_vel)
            super().move()
            return

        tar_pos = self.target.x+self.target.width*0.5, self.target.y+self.target.height*0.5
        x_t = tar_pos[0] - self.x
        y_t = tar_pos[1] - self.y
        self.apply_force(x_t*self.speed, y_t*self.speed)
       
        self.last_x_vel = self.x_vel
        self.last_y_vel = self.y_vel

        self.vel_set = True
        super().move()

class weapon(drawable):
    def __init__(self, player, screen, shooting_delay, damage, min_shooting_delay, frame_set, impact_force):
        self.player = player
        self.screen = screen
        self.frame_set = frame_set
        self.impact_force = impact_force
        drawable.__init__(self, (0,0), (15,15), screen, (200, 0, 255)) 
        self.damage = damage
        self.player_offset = (0, 0)
        self.shooting_delay = shooting_delay
        self.current_shooting_delay = 0
        self.min_shooting_delay = min_shooting_delay
        self.current_target = point((0,0))
        self.frame = frame_set["right"][0]
        self.shooting = False
        self.shooting_animation_counter = 0
        self.shooting_animation_length = 4

    def shoot(self, target):
        if self.current_shooting_delay < self.shooting_delay:
            return (False, None)
        
        self.current_frame = 0
        self.current_target = target
        self.current_shooting_delay = 0
        b = bullet(self.player, (self.x+self.width*0.5, self.y+self.height*0.5), self.screen, target, self.damage, self.impact_force)
        self.player.active_bullets.append(b)
        self.shooting = True
        return (True, b)
    
    def dec_shooting_delay(self):
        if self.shooting_delay > self.min_shooting_delay:
            self.shooting_delay -= 1

    def draw_frame(self, angle):
        if self.shooting:
            self.shooting_animation_counter += 1
            self.frame = self.frame_set["right"][1]
            if self.shooting_animation_counter >= self.shooting_animation_length:
                self.shooting = False
                self.shooting_animation_counter = 0
                self.frame = self.frame_set["right"][0]
        super().draw_frame(self.frame, angle)



