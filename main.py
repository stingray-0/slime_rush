import pygame
import sys
import random
from settings import WIDTH, HEIGHT, TILE_SIZE, all_level
from utils import get_image
from sprites import *
from player import Player

def menu(screen, title_font, instruction_font):
    light_blue = (122, 229, 250)
    dark_blue = (255, 255, 255)
    thickness = 5
    offsets = [
        (-1, -1), (0, -1), (1, -1),
        (-1,  0),          (1,  0),
        (-1,  1), (0,  1), (1,  1)
    ]
    
    for dx, dy in offsets:
        outline_text = title_font.render("SLIME RUSH", True, dark_blue)
        outline_rect = outline_text.get_rect(center=(
            WIDTH//2 + (dx * thickness), 
            HEIGHT//2 - 100 + (dy * thickness)
        ))
        screen.blit(outline_text, outline_rect)
        
    inner_text = title_font.render("SLIME RUSH", True, light_blue)
    inner_rect = inner_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    screen.blit(inner_text, inner_rect)
    
    instruction_text = instruction_font.render("Press ANY KEY to Start", True, (255, 255, 255))
    instruction_rect = instruction_text.get_rect(center = (WIDTH //2, HEIGHT //2 + 150))    
    screen.blit(instruction_text, instruction_rect)


def paused_screen(screen, title_font, normal_font, pause_options, pause_selected, time_frames, player, skull_image):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    paused_text = title_font.render("PAUSED", True, (255, 255, 255))
    paused_rect = paused_text.get_rect(center = (WIDTH // 2, HEIGHT // 2 - 100))
    screen.blit(paused_text, paused_rect)
    
    for i, option in enumerate(pause_options):
        if i == pause_selected:
            text_color = (255, 255, 100)
            display_text = f"> {option} <"
        else:
            text_color = (180, 180, 180)
            display_text = option
        
        text_surface = normal_font.render(display_text, True, text_color)
        text_rect =text_surface.get_rect(center = (WIDTH // 2, HEIGHT // 2 + i*60))
        screen.blit(text_surface, text_rect)
        
    seconds = time_frames // 60
    minutes = seconds // 60
    milliseconds = int(time_frames%60 / 60.0 * 1000)
    timer_text = f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    timer_surface = normal_font.render(timer_text, True, (255, 255, 255))
    screen.blit(timer_surface, (20, 20))
    
    death_text = f"Deaths: {player.death_count}"
    death_surface = normal_font.render(death_text, True, (255, 100, 100))
    screen.blit(death_surface, (WIDTH - death_surface.get_width() - 20, 20))
    death_text = f"Ice Cubes: {len(player.collected_cubes)}"
    death_surface = normal_font.render(death_text, True, (122, 229, 250))
    screen.blit(death_surface, (WIDTH - death_surface.get_width() - 20, 60))


def help_screen(screen, title_font, normal_font):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150)) 
    screen.blit(overlay, (0, 0))
    

    help_title = title_font.render("HOW TO PLAY", True, (255, 255, 255))
    title_rect = help_title.get_rect(center=(WIDTH // 2, 120))
    screen.blit(help_title, title_rect)
    instructions = [
        "ARROW KEYS : Move & Climb",
        "SPACE : Jump & Wall-Jump",
        "X : Dash (Use with arrow keys))",
        "Z (Hold) : Grab Walls",
        "",
        "Avoid Bramble Spikes",
        "Bounce on Fungi to go flying",
        "Collect glowing Ice Cubes!",
        "",
        "Press ESC to Return"
    ]
    
    for i, line in enumerate(instructions):
        if i < 4:
            color = (150, 255, 150) 
        elif "ESC" in line:
            color = (255, 255, 100)
        else:
            color = (220, 220, 220)
        text_surf = normal_font.render(line, True, color)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, 250 + (i * 45)))
        screen.blit(text_surf, text_rect)


def win_screen(screen, title_font, bold_font, player, total_frames, icons):
    seconds = total_frames // 60
    minutes = seconds // 60
    seconds = seconds % 60
    milliseconds = int(((total_frames % 60) / 60.0) * 1000)
    timer_text = f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    
    win_title = title_font.render("RUN COMPLETE!", True, (255, 215, 0)) 
    title_rect = win_title.get_rect(center=(WIDTH // 2, 150))
    screen.blit(win_title, title_rect)
    
    time_surf = bold_font.render( f"Time:                {timer_text}", True, (255, 255, 255))
    death_surf = bold_font.render(f"Deaths:            {player.death_count}", True, (255, 100, 100))
    total_cubes = 0
    for level in all_level:
        total_cubes += level.total_cubes
    cube_surf = bold_font.render( f"Cubes:             {len(player.collected_cubes)} / {total_cubes}", True, (122, 229, 250))

    
    start_y = 300
    spacing = 80
    
    center_x = WIDTH // 2
    icon_x = center_x + 50   
    text_x = center_x - 200  
    
    time_rect = time_surf.get_rect(midleft=(text_x, start_y))
    time_icon_rect = icons[0].get_rect(midright=(icon_x, start_y))
    screen.blit(time_surf, time_rect)
    screen.blit(icons[0], time_icon_rect)
    
    death_rect = death_surf.get_rect(midleft=(text_x, start_y + spacing))
    death_icon_rect = icons[1].get_rect(midright=(icon_x, start_y + spacing))
    screen.blit(death_surf, death_rect)
    screen.blit(icons[1], death_icon_rect)
    
    cube_rect = cube_surf.get_rect(midleft=(text_x, start_y + (spacing * 2)))
    cube_icon_rect = icons[2].get_rect(midright=(icon_x, start_y + (spacing * 2)))
    screen.blit(cube_surf, cube_rect)
    screen.blit(icons[2], cube_icon_rect)
    
    
    
    prompt = bold_font.render("Press ENTER to Return to Menu", True, (180, 180, 180))
    screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, HEIGHT - 150)))

    
def render_level(
    all_sprites,
    player,
    platforms, 
    goals, 
    leave_goals,
    barriers, 
    spikes,
    fungi,
    ice_cubes, 
    tile_images, 
    seed, 
    level_idx
):
    all_sprites.empty()
    platforms.empty()
    goals.empty()
    leave_goals.empty()
    barriers.empty() 
    spikes.empty()
    fungi.empty()
    ice_cubes.empty()
    random.seed(seed)
    level = all_level[level_idx-1].grid
    patch = tile_images["grass"]["patch"][0]
    for row_idx, row in enumerate(level):
        for col_idx, cell in enumerate(row):
            image_list = None
            sprite_type = None
            vertical_flip = False
            horizontal_flip = False
            match cell:
                case " ":
                    continue
                case "G":
                    sprite_type = "goal"
                case "L":
                    sprite_type = "leave_goal"
                case "B":
                    sprite_type = "barrier"
                case "D":
                    bitmask = 0
                    inner_dl = False
                    inner_dr = False
                    inner_ul = False
                    inner_ur = False
                    up = row_idx > 0 and level[row_idx-1][col_idx] == "D"
                    down = row_idx < len(level)-1 and level[row_idx+1][col_idx] == "D"
                    right = col_idx < len(row)-1 and level[row_idx][col_idx+1] == "D"
                    left = col_idx > 0 and level[row_idx][col_idx-1] == "D"

                    if up: bitmask += 1
                    if right: bitmask += 2
                    if down: bitmask += 4
                    if left: bitmask += 8
                        
                    match bitmask:
                        case 0:
                            image_list = tile_images["grass"]["float"]
                        case 1:
                            image_list = tile_images["grass"]["no_bottom"]
                            vertical_flip = True
                        case 2:
                            image_list = tile_images["grass"]["no_right"]
                        case 3:
                            image_list = tile_images["grass"]["left_corner"]
                            vertical_flip = True
                        case 4:
                            image_list = tile_images["grass"]["no_bottom"]
                        case 5:
                            image_list = tile_images["grass"]["left_right"]
                        case 6:
                            image_list = tile_images["grass"]["left_corner"]
                        case 7:
                            image_list = tile_images["grass"]["left_vertical"]
                        case 8:
                            image_list = tile_images["grass"]["no_right"]
                            horizontal_flip = True
                        case 9:
                            image_list = tile_images["grass"]["right_corner"]
                            vertical_flip = True
                        case 10:
                            image_list = tile_images["grass"]["top_bottom"]
                        case 11:
                            image_list = tile_images["grass"]["horizontal"]
                            vertical_flip = True
                        case 12:
                            image_list = tile_images["grass"]["right_corner"]
                        case 13:
                            image_list = tile_images["grass"]["right_vertical"]
                        case 14:
                            image_list = tile_images["grass"]["horizontal"]
                        case 15:
                            image_list = tile_images["dirt"]["normal"]
                    if up and right and level[row_idx-1][col_idx+1] != "D":
                        inner_ur = True
                    if down and right and level[row_idx + 1][col_idx + 1] != "D":
                        inner_dr = True
                    if down and left and level[row_idx + 1][col_idx - 1] != "D":
                        inner_dl = True
                    if up and left and level[row_idx - 1][col_idx - 1] != "D":
                        inner_ul = True
                case "^":
                    sprite_type = "spike"
                    image_list = tile_images["bramble"]["normal"]
                    spike_direction = "up"
                    up_solid = row_idx > 0 and level[row_idx-1][col_idx] == "D"
                    down_solid = row_idx < len(level)-1 and level[row_idx+1][col_idx] == "D"
                    left_solid = col_idx > 0 and level[row_idx][col_idx-1] == "D"
                    right_solid = col_idx < len(row)-1 and level[row_idx][col_idx+1] == "D"
                    if down_solid:
                        spike_direction ="up"
                    elif up_solid:
                        spike_direction = "down"
                    elif left_solid:
                        spike_direction = "right"
                    elif right_solid:
                        spike_direction = "left"
                case "F":
                    sprite_type = "fungi"
                    fungi_direction = "up"
                    up_solid = row_idx > 0 and level[row_idx-1][col_idx] == "D"
                    down_solid = row_idx < len(level)-1 and level[row_idx+1][col_idx] == "D"
                    left_solid = col_idx > 0 and level[row_idx][col_idx-1] == "D"
                    right_solid = col_idx < len(row)-1 and level[row_idx][col_idx+1] == "D"
                    if down_solid:
                        fungi_direction ="up"
                    elif up_solid:
                        fungi_direction = "down"
                    elif left_solid:
                        fungi_direction = "right"
                    elif right_solid:
                        fungi_direction = "left"
                case "C":
                    sprite_type = "ice_cube"
                    image_list = tile_images["ice_cube"]["normal"]
                    cube_id = f"L{level_idx}_X{col_idx}_Y{row_idx}"
                    
            image = None
            if image_list:
                image = random.choice(image_list)
                if horizontal_flip or vertical_flip:    
                    image = pygame.transform.flip(image, horizontal_flip, vertical_flip)
            
            x_pos = col_idx * TILE_SIZE
            y_pos = row_idx * TILE_SIZE
            
            match sprite_type:
                case "spike":
                    new_sprite = Spike(x_pos, y_pos, image, spike_direction)
                    spikes.add(new_sprite)
                case "goal":
                    new_sprite = Goal(x_pos, y_pos)
                    goals.add(new_sprite)
                case "leave_goal":
                    new_sprite = Goal(x_pos, y_pos)
                    leave_goals.add(new_sprite)
                case "barrier":
                    new_sprite = Barrier(x_pos, y_pos)
                    barriers.add(new_sprite)
                case "fungi":
                    new_sprite = Fungi(x_pos, y_pos, fungi_direction)
                    # barriers.add(new_sprite)
                    fungi.add(new_sprite)
                case "ice_cube":
                    banked = cube_id in player.collected_cubes
                    trailing = any(cube.id == cube_id for cube in player.follow_cubes)
                    if not trailing and not banked:
                        new_sprite = IceCube(x_pos, y_pos, image, level_idx, cube_id)
                        ice_cubes.add(new_sprite)
                case _:
                    new_sprite = Platform(x_pos, y_pos, image, inner_ur, inner_ul, inner_dr, inner_dl, patch)
                    platforms.add(new_sprite)
            
            all_sprites.add(new_sprite)
            


def run_game():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    bg_image = pygame.image.load("assets/background.jpg").convert()
    bg_image.set_alpha(200)
    bg_width, bg_height = bg_image.get_size()
    SCALE_FACTOR = HEIGHT / bg_height
    new_width = int(bg_width * SCALE_FACTOR)
    bg_image = pygame.transform.smoothscale(bg_image, (new_width, HEIGHT))
    clock = pygame.time.Clock()

    title_font = pygame.font.Font("assets/fonts/ThaleahFat.ttf", 108)
    bold_font = pygame.font.Font("assets/fonts/ThaleahFat.ttf", 48)
    normal_font = pygame.font.Font("assets/fonts/m5x7.ttf", 48)

    grass_sheet = pygame.image.load("assets/grass_tile.png").convert_alpha()
    bramble_sheet = pygame.image.load("assets/bramble_bush_tile.png").convert_alpha()
    ice_cube_image = pygame.image.load("assets/ice_cube.png").convert_alpha()
    ice_cube_image = pygame.transform.scale(ice_cube_image, (TILE_SIZE*1.5, TILE_SIZE*1.5))
    timer_image = pygame.image.load("assets/timer.png").convert_alpha()
    timer_image = pygame.transform.scale(timer_image, (TILE_SIZE*1.5, TILE_SIZE*1.5))
    skull_image = pygame.image.load("assets/skull.png").convert_alpha()
    skull_image = pygame.transform.scale(skull_image, (TILE_SIZE*1.5, TILE_SIZE*1.5))
    fungi_sheet = pygame.image.load("assets/fungi.png").convert_alpha()
    icons = [
        timer_image,
        skull_image, 
        ice_cube_image
    ]
    
    Fungi.load_animations(fungi_sheet)
    
    tile_images = {
        "grass": {
            "horizontal":[
                get_image(grass_sheet, 32, 0, TILE_SIZE, TILE_SIZE, TILE_SIZE),
                get_image(grass_sheet, 160, 0, TILE_SIZE, TILE_SIZE, TILE_SIZE),
                get_image(grass_sheet, 192, 0, TILE_SIZE, TILE_SIZE, TILE_SIZE),
                get_image(grass_sheet, 224, 0, TILE_SIZE, TILE_SIZE, TILE_SIZE),
            ],
            "left_corner":[
                get_image(grass_sheet, 0, 0, TILE_SIZE, TILE_SIZE, TILE_SIZE),
                get_image(grass_sheet, 128, 0, TILE_SIZE, TILE_SIZE, TILE_SIZE),
            ],
            "right_corner":[
                get_image(grass_sheet, 64, 0, TILE_SIZE, TILE_SIZE, TILE_SIZE),
                get_image(grass_sheet, 256, 0, TILE_SIZE, TILE_SIZE, TILE_SIZE),  
            ],
            "left_vertical":[
                get_image(grass_sheet, 0, 32, TILE_SIZE, TILE_SIZE, TILE_SIZE),
                get_image(grass_sheet, 0, 64, TILE_SIZE, TILE_SIZE, TILE_SIZE),
                get_image(grass_sheet, 128, 32, TILE_SIZE, TILE_SIZE, TILE_SIZE),                    
            ],
            "right_vertical":[
                get_image(grass_sheet, 64, 32, TILE_SIZE, TILE_SIZE, TILE_SIZE),
                get_image(grass_sheet, 64, 64, TILE_SIZE, TILE_SIZE, TILE_SIZE),
                get_image(grass_sheet, 256, 32, TILE_SIZE, TILE_SIZE, TILE_SIZE),
            ],
            "patch":[
                get_image(grass_sheet, 320, 0, TILE_SIZE, TILE_SIZE, TILE_SIZE),
            ],
            "float":[
                get_image(grass_sheet, 320, 64, TILE_SIZE, TILE_SIZE, TILE_SIZE),
            ],
            "top_bottom":[
                get_image(grass_sheet, 32, 128, TILE_SIZE, TILE_SIZE, TILE_SIZE),
                get_image(grass_sheet, 64, 128, TILE_SIZE, TILE_SIZE, TILE_SIZE),
            ],
            "left_right":[
                get_image(grass_sheet, 160, 128, TILE_SIZE, TILE_SIZE, TILE_SIZE),
                get_image(grass_sheet, 160, 160, TILE_SIZE, TILE_SIZE, TILE_SIZE),
            ],
            "no_right":[
                get_image(grass_sheet, 0, 128, TILE_SIZE, TILE_SIZE, TILE_SIZE),
            ],
            "no_bottom":[
                get_image(grass_sheet, 160, 96, TILE_SIZE, TILE_SIZE, TILE_SIZE),
            ],
        },
        "dirt":{
            "normal":[
                get_image(grass_sheet, 32, 32, TILE_SIZE, TILE_SIZE, TILE_SIZE),
                get_image(grass_sheet, 32, 64, TILE_SIZE, TILE_SIZE, TILE_SIZE),
                get_image(grass_sheet, 160, 32, TILE_SIZE, TILE_SIZE, TILE_SIZE),
                get_image(grass_sheet, 192, 32, TILE_SIZE, TILE_SIZE, TILE_SIZE),
                get_image(grass_sheet, 224, 32, TILE_SIZE, TILE_SIZE, TILE_SIZE),
            ],
        },
        "bramble":{
            "normal":[
                get_image(bramble_sheet, 0, 0, TILE_SIZE, TILE_SIZE, TILE_SIZE),
                get_image(bramble_sheet, 32, 0, TILE_SIZE, TILE_SIZE, TILE_SIZE),
                get_image(bramble_sheet, 64, 0, TILE_SIZE, TILE_SIZE, TILE_SIZE),
                get_image(bramble_sheet, 96, 0, TILE_SIZE, TILE_SIZE, TILE_SIZE),
            ]
        },
        "ice_cube":{
            "normal":[
                ice_cube_image
            ],
        },
    }

    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    goals = pygame.sprite.Group()
    leave_goals = pygame.sprite.Group()
    barriers = pygame.sprite.Group()
    spikes = pygame.sprite.Group()
    fungi = pygame.sprite.Group()
    ice_cubes = pygame.sprite.Group()
    camera = Camera(WIDTH, HEIGHT)
    
    current_level =10
    current_room = pygame.Rect(TILE_SIZE, 0, (len(all_level[current_level-1].grid[0])-2)*TILE_SIZE, (len(all_level[current_level-1].grid)-1)*TILE_SIZE) 
    camera.set_bounds(current_room)
    
    player = Player(all_level[current_level-1].forward_spawn[0], all_level[current_level-1].forward_spawn[1])
    render_level(all_sprites, player, platforms, goals, leave_goals, barriers, spikes, fungi, ice_cubes, tile_images, 1, current_level)

    game_state = "MENU"
    pause_options = ["Resume", "Retry", "Restart Run", "Help", "Quit"]
    pause_selected = 0
    running = True
    
    total_frames = 0
    
    while running:
        screen.fill((100, 100, 100))
        screen.blit(bg_image, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if game_state == "MENU":
                    game_state = "PLAYING"
                elif game_state == "PLAYING" and event.key == pygame.K_ESCAPE:
                    game_state = "PAUSED"
                elif game_state == "PAUSED":
                    if event.key == pygame.K_ESCAPE:
                        game_state = "PLAYING"
                    elif event.key == pygame.K_UP:
                        pause_selected = (pause_selected - 1)%len(pause_options)
                    elif event.key == pygame.K_DOWN:
                        pause_selected = (pause_selected + 1)%len(pause_options)
                    elif event.key == pygame.K_RETURN:
                        selected_text = pause_options[pause_selected]
                        if selected_text == "Resume":
                            game_state = "PLAYING"
                        elif selected_text == "Retry":
                            player.die_and_respawn(current_level)
                            game_state = "PLAYING"
                        elif selected_text == "Restart Run":
                            player.death_count = 0
                            total_frames = 0
                            player.collected_cubes.clear()
                            player.follow_cubes.clear()
                            current_level = 1
                            current_room = pygame.Rect(TILE_SIZE, 0, (len(all_level[current_level-1].grid[0])-2)*TILE_SIZE, (len(all_level[current_level-1].grid)-1)*TILE_SIZE) 
                            camera.set_bounds(current_room)
                            
                            render_level(all_sprites, player, platforms, goals, leave_goals, barriers, spikes, fungi, ice_cubes, tile_images, 1, current_level)
                            
                            spawn_x = all_level[current_level-1].forward_spawn[0]
                            spawn_y = all_level[current_level-1].forward_spawn[1]
                            player.next_level(spawn_x, spawn_y)
                            
                            game_state = "PLAYING"
                        elif selected_text == "Help":
                            game_state = "HELP"
                        elif selected_text == "Quit":
                            running = False
                elif game_state == "HELP":
                    if event.key == pygame.K_ESCAPE:
                        game_state = "PAUSED"
                elif game_state == "WIN":
                    if event.key == pygame.K_RETURN:
                        game_state = "MENU"
                        player.death_count = 0
                        total_frames = 0
                        player.collected_cubes.clear()
                        player.follow_cubes.clear()
                        current_level = 1
                        current_room = pygame.Rect(TILE_SIZE, 0, (len(all_level[current_level-1].grid[0])-2)*TILE_SIZE, (len(all_level[current_level-1].grid)-1)*TILE_SIZE) 
                        camera.set_bounds(current_room)
                        
                        render_level(all_sprites, player, platforms, goals, leave_goals, barriers, spikes, fungi, ice_cubes, tile_images, 1, current_level)
                        
                        spawn_x = all_level[current_level-1].forward_spawn[0]
                        spawn_y = all_level[current_level-1].forward_spawn[1]
                        player.next_level(spawn_x, spawn_y)
                        
        if game_state == "MENU":
            menu(screen, title_font, normal_font)
        elif game_state == "WIN":
            win_screen(screen, title_font, bold_font, player, total_frames, icons)
        else:
            if game_state == "PLAYING":
                total_frames += 1
                player.update(platforms, barriers, spikes, fungi, current_level)
                camera.update(player)
                
                for fungus in fungi:
                    fungus.update()
                
                for cube in ice_cubes:
                    cube.update(player)
                    if cube.hitbox.colliderect(player.rect) and cube.state == "idle":
                        cube.state = "following"
                        player.follow_cubes.append(cube)
                        
                    
                # for spike in spikes:
                #     debug_rect = spike.hitbox.move(camera.camera.topleft)
                    
                #     pygame.draw.rect(screen, (255, 0, 0), debug_rect, 2)

                # player_debug = player.hitbox.move(camera.camera.topleft)
                # pygame.draw.rect(screen, (0, 255, 0), player_debug, 2)
                # for cube in ice_cubes:
                #     cube_debug = cube.hitbox.move(camera.camera.topleft)
                #     pygame.draw.rect(screen, (0, 255, 0), cube_debug, 2)
                if pygame.sprite.spritecollide(player, goals, False):
                    if current_level >= len(all_level):
                        game_state = "WIN"
                    else:
                        current_level += 1
                        current_room = pygame.Rect(TILE_SIZE, 0, (len(all_level[current_level-1].grid[0])-2)*TILE_SIZE, (len(all_level[current_level-1].grid)-1)*TILE_SIZE) 
                        camera.set_bounds(current_room)
                        
                        saved_cubes = player.follow_cubes.copy()
                        
                        render_level(all_sprites, player, platforms, goals, leave_goals, barriers, spikes, fungi, ice_cubes, tile_images, 1, current_level)
                        
                        for cube in saved_cubes:
                            ice_cubes.add(cube)
                            all_sprites.add(cube)
                        player.next_level(all_level[current_level-1].forward_spawn[0], all_level[current_level-1].forward_spawn[1])
                if pygame.sprite.spritecollide(player, leave_goals, False):
                    if current_level > 1:
                        current_level -= 1
                    current_room = pygame.Rect(TILE_SIZE, 0, (len(all_level[current_level-1].grid[0])-2)*TILE_SIZE, (len(all_level[current_level-1].grid)-1)*TILE_SIZE) 
                    camera.set_bounds(current_room)
                    
                    saved_cubes = player.follow_cubes.copy()
                    
                    render_level(all_sprites, player, platforms, goals, leave_goals, barriers, spikes, fungi, ice_cubes, tile_images, 1, current_level)
                    
                    for cube in saved_cubes:
                        ice_cubes.add(cube)
                        all_sprites.add(cube)
                    player.next_level(all_level[current_level-1].backward_spawn[0], all_level[current_level-1].backward_spawn[1])

            for sprite in all_sprites:
                screen.blit(sprite.image, camera.apply(sprite))
            player.draw(screen, camera)
        
            if game_state == "PAUSED":
                paused_screen(screen, title_font, normal_font, pause_options, pause_selected, total_frames, player, skull_image)
        
            if game_state == "HELP":
                help_screen(screen, title_font, normal_font)
        pygame.display.flip()
        
        clock.tick(60)
    print(player.collected_cubes)
    print(total_frames)
    pygame.quit()
    sys.exit()




if __name__ == "__main__":
    run_game()
