import pygame
import numpy as np

from spatial_hashing import spatial_hash
from speed_buff_item import speed_buff
from player import player_controller
from wave_spawner import wave_spawner
from base_classes import bullet, experience, hitbox, item, blood
from weapons import machine_gun, pistol

from enemies import chicken, cow
from ui_stuff import button

pygame.init()
pygame.display.init()
pygame.display.set_caption("Surviver stuff")

WIDTH, HEIGHT = 1500,800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60

HASH_MAP_SIZE = 40
CHICKEN_SIZE = (30, 30)
COW_SIZE = (55, 45)
BUTTON_FONT = pygame.font.SysFont("comicsansms", 35)
BUTTON_FONT_COLOR = (200, 200, 200)

def load_transform_image(path, size):
    return pygame.transform.scale(pygame.image.load(path), size).convert_alpha()

def load_frames(ammount, path, size):
    f = {"left": [], "right": []}
    for i in range(1, ammount+1):
        f["left"].append(load_transform_image(f"{path}{i}.png", size))
        f["right"].append(pygame.transform.flip(load_transform_image(f"{path}{i}.png", size), True, False))

    return f

def load_background():
    return pygame.transform.scale(pygame.image.load("assets/background/grass.png"), (WIDTH, HEIGHT)).convert()

BACKGROUND = load_background()
CHICKEN_FRAMES = load_frames(6, "assets/enemies/chicc/chicc_", CHICKEN_SIZE)
COW_FRAMES = load_frames(5, "assets/enemies/cow/cow_", COW_SIZE)

ENEMY_FRAMES = {"chicken": (CHICKEN_FRAMES, CHICKEN_SIZE), "cow": (COW_FRAMES, COW_SIZE)}
PISTOL_FRAMES = load_frames(2, "assets/weapons/glock_", (30, 20))
MACHINEGUN_FRAMES = load_frames(2, "assets/weapons/ak_", (50, 30))

def draw_game(screen, player, entities:list, items, background, ui_font, blood_pool):
    screen.blit(background, (0, 0))

    #pygame.draw.rect(screen, (255, 255, 0), (player.sr_x, player.sr_y, player.sr_width, player.sr_height))
    #pygame.draw.rect(screen, (255, 255, 0), (player.grav_x, player.grav_y, player.grav_width, player.grav_height))
    for b in blood_pool:
        b.draw()

    for item in items:
        item.draw()

    for bullet in player.active_bullets:
        bullet.draw()

    for e in entities:
        e.draw()

    for weapon in player.weapons:
        angle = np.degrees(np.arctan2(weapon.current_target.y - player.y, weapon.current_target.x - player.x))
        weapon.draw_frame(angle)

    player.draw()

    fr = ui_font.render(f"HP: {int(player.hp)} | {player.max_hp}", True, (200, 0, 0))
    screen.blit(fr, (100, 50))
    pygame.display.update()

def draw_buttons(screen, buttons, background, player=None):
    screen.blit(background, (0, 0))

    if player is not None:
        player.draw_frame(player.get_current_frame())

    for btn in buttons:
        btn.draw()

    pygame.display.update()

pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONDOWN])

def check_events(player):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player.move_up = True
            if event.key == pygame.K_DOWN:
                player.move_down = True
            if event.key == pygame.K_LEFT:
                player.move_left = True
            if event.key == pygame.K_RIGHT:
                player.move_right = True
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                player.move_up = False
            if event.key == pygame.K_DOWN:
                player.move_down = False
            if event.key == pygame.K_LEFT:
                player.move_left = False
            if event.key == pygame.K_RIGHT:
                player.move_right = False

def move_entities(player, entities:list, items:list, blood_pool):
    player.move()
    for b in player.active_bullets:
        b.move()
    
    for e in entities:
        e.move_to_player()

    for item in items:
        item.move_to_player()

    for b in blood_pool:
        b.move()

def check_entity_collision(player, entities:list, collision_map:spatial_hash, items, blood_pool):
    #check if enemy in player shooting range
    for pc in collision_map.potential_collisions(player.shooting_range.get_rect(), player):
        if player.shooting_range.collides_with(pc):
            if type(pc) is bullet:
                continue

            if issubclass(type(pc), item):
                continue

            for (succes, projectile) in player.shoot(pc):
                if succes:
                    collision_map.add_rect(projectile.get_rect(), projectile)
                    break

    #check enemy collision with other enemies and player bullets
    for e in entities:
        for pc in collision_map.potential_collisions(e.get_rect(), e):
            if issubclass(type(pc), item):
                continue
            
            if type(pc) is bullet:
                if e.collides_with(pc):
                    collision_map.remove_rect(pc.get_rect(), pc)
                    pc.remove_from_pool()

                    e.take_damage(pc.damage)
                    for i in range(int(e.blood_drop*0.5)):
                        blood_pool.append(blood((e.x, e.y), e.screen, blood_pool))
                    
                    e.apply_colision_force(pc.x_vel*pc.impact_force, pc.y_vel*pc.impact_force, pc.mass)
                    if not e.alive:
                        if e in entities:
                            entities.remove(e)
                            for i in range(e.blood_drop):
                                blood_pool.append(blood((e.x, e.y), e.screen, blood_pool))
                            collision_map.remove_rect(e.get_rect(), e)
                            #spawn exp on enemy death
                            for exp in e.experience:
                                collision_map.add_rect(exp.get_rect(), exp)
                                items.append(exp)
                                exp.apply_force(np.random.randint(-5, 5), np.random.randint(-5, 5))
                    
            #apply some force to colliding entities
            e.apply_colision_force(-pc.x_vel*2, -pc.y_vel*2, pc.mass)
            pc.apply_colision_force(e.x_vel, e.y_vel, e.mass)

    #check collision with player
    for pc in collision_map.potential_collisions(player.get_rect(), player):
        if type(pc) is bullet:
                continue
        #if player.collides_with(pc):
        match pc:
            case experience():
                player.take_experience(pc.ammount)
                collision_map.remove_rect(pc.get_rect(), pc)
                items.remove(pc)
            case chicken():
                collision_map.remove_rect(pc.get_rect(), pc)
                entities.remove(pc)
                pc.alive = False
                player.take_damage()
            case cow():
                collision_map.remove_rect(pc.get_rect(), pc)
                entities.remove(pc)
                pc.alive = False
                player.take_damage(3)
            case speed_buff():
                pc.buff_speed()
                collision_map.remove_rect(pc.get_rect(), pc)
                items.remove(pc)
    
    #check collision with player grav field
    for pc in collision_map.potential_collisions(player.grav_field.get_rect(), player):
        if issubclass(type(pc), item):
            pc.gravitate_to_player = True

def refresh_collision_map(collision_map):
    collision_map.reset()
    for e in entities:
        collision_map.add_rect(e.get_rect(), e)
    for b in player.active_bullets:
        collision_map.add_rect(b.get_rect(), b)
    for item in items:
        collision_map.add_rect(item.get_rect(), item)

    return collision_map

def handle_button_events(buttons):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            event_pos = hitbox(event.pos, (1, 1))
            for btn in buttons:
                if btn.collides_with(event_pos):
                    btn.clicked = True

def create_menu(btn_img, btn_size):
    btns = []

    start_btn = button("Start", (WIDTH/2-btn_size[0], HEIGHT/2-btn_size[1]), btn_size, WIN, BUTTON_FONT, BUTTON_FONT_COLOR, btn_img)
    exit_btn = button("Exit", (WIDTH/2-btn_size[0], HEIGHT/2+btn_size[1]), btn_size, WIN, BUTTON_FONT, BUTTON_FONT_COLOR, btn_img)
    
    btns.append(start_btn)
    btns.append(exit_btn)
    return btns

def create_lvlup_menu(btn_img, btn_size):
    btns = []

    increase_sr = button("Shooting Range", (WIDTH/2-btn_size[0], HEIGHT/2-btn_size[1]), btn_size, WIN, BUTTON_FONT, BUTTON_FONT_COLOR, btn_img)
    increase_hp = button("HP", (WIDTH/2-btn_size[0] + (btn_size[0]+20), (HEIGHT/2-btn_size[1])), btn_size, WIN, BUTTON_FONT, BUTTON_FONT_COLOR, btn_img)
    increase_hp_reg = button("HP Regen", (WIDTH/2-btn_size[0] + (btn_size[0]+20)*2, (HEIGHT/2-btn_size[1])), btn_size, WIN, BUTTON_FONT, BUTTON_FONT_COLOR, btn_img)
    dec_shooting_delay = button("Decrease Shooting Delay", (WIDTH/2-btn_size[0] + (btn_size[0]+20)*3, (HEIGHT/2-btn_size[1])), btn_size, WIN, BUTTON_FONT, BUTTON_FONT_COLOR, btn_img)

    btns.append(increase_sr)
    btns.append(increase_hp)
    btns.append(increase_hp_reg)
    btns.append(dec_shooting_delay)
    return btns

def draw_lvlup_menu(screen, player, background):
    btn_size = (200, 300)
    btn_img = load_transform_image("assets/ui/Sprite sheets/buttons/image_1.png", btn_size)

    lvl_up_btns = create_lvlup_menu(btn_img, btn_size)
    player.stop_moving()
    while player.has_levelup:
        draw_buttons(screen, lvl_up_btns, background, player)
        handle_button_events(lvl_up_btns)
        if lvl_up_btns[0].clicked:
            player.increase_shooting_range(0.5)
            player.has_levelup = False
        elif lvl_up_btns[1].clicked:
            player.increase_hp(3)
            player.has_levelup = False
        elif lvl_up_btns[2].clicked:
            player.increase_hp_reg(0.1)
            player.has_levelup = False
        elif lvl_up_btns[3].clicked:
            for weapon in player.weapons:
                weapon.dec_shooting_delay()
            player.has_levelup = False

if __name__ == "__main__":
    while 1:
        screen = WIN
        fps = FPS
        background = BACKGROUND
        ui_font = BUTTON_FONT
        btn_size = (200, 100)
        btn_img = load_transform_image("assets/ui/Sprite sheets/buttons/image_1.png", btn_size)

        buttons = create_menu(btn_img, btn_size)
        
        #main menu loop
        while not buttons[0].clicked:
            draw_buttons(screen, buttons, background)
            handle_button_events(buttons)
            if buttons[1].clicked:
                pygame.quit()
                quit()

        collision_map = spatial_hash(HASH_MAP_SIZE)
        player = player_controller((WIDTH/2, HEIGHT/2), screen, (WIDTH, HEIGHT))
        player.increase_shooting_range(5)
        
        collision_map.add_rect(player.get_rect(), player)
        collision_map.add_rect(player.grav_field.get_rect(), player)
        collision_map.add_rect(player.shooting_range.get_rect(), player)

        spawner = wave_spawner(player, collision_map, screen, ENEMY_FRAMES)
        entities, items = spawner.spawn_wave()

        clock = pygame.time.Clock()
        skip_coll_check = False
        blood_pool = []
        #game loop
        while player.alive:
            check_events(player)

            if skip_coll_check:
                collision_map = refresh_collision_map(collision_map)

                #this checks for collisions every second frame
                check_entity_collision(player, entities, collision_map, items, blood_pool)

            move_entities(player, entities, items, blood_pool)

            draw_game(screen, player, entities, items, background, ui_font, blood_pool)

            if len(entities) == 0:
                entities, new_items = spawner.spawn_wave()
                items.extend(new_items)
                if len(entities) != 0: #replace this by shop menu
                    # rw = np.random.randint(0, 11)
                    # if rw > 8:
                    #     player.add_weapon(machine_gun(player, screen, MACHINEGUN_FRAMES))
                    # else:
                        player.add_weapon(pistol(player, screen, PISTOL_FRAMES))

            if player.has_levelup:
                draw_lvlup_menu(screen, player, background)
              
            skip_coll_check = not skip_coll_check
            clock.tick(fps)
    
