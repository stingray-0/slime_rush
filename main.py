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


def render_level(all_sprites, platforms, goals, barriers, spikes, ice_cubes, tile_images, seed, level_idx):
    all_sprites.empty()
    platforms.empty()
    goals.empty()
    barriers.empty() 
    spikes.empty()
    random.seed(seed)
    level = all_level[level_idx-1]
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
                case "B":
                    sprite_type = "barrier"
                case "C":
                    sprite_type = "ice_cube"
                    image_list = tile_images["ice_cube"]["normal"]
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
            if image_list:
                image = random.choice(image_list)
            if horizontal_flip or vertical_flip:    
                image = pygame.transform.flip(image, horizontal_flip, vertical_flip)
            x_pos = col_idx * TILE_SIZE
            y_pos = row_idx * TILE_SIZE
            
            match sprite_type:
                case "spike":
                    new_sprite = Spike(x_pos, y_pos, image)
                    spikes.add(new_sprite)
                case "goal":
                    new_sprite = Goal(x_pos, y_pos)
                    goals.add(new_sprite)
                case "barrier":
                    new_sprite = Barrier(x_pos, y_pos)
                    barriers.add(new_sprite)
                case "ice_cube":
                    new_sprite = IceCube(x_pos, y_pos, image)
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

    title_font = pygame.font.Font(None, 108)
    normal_font = pygame.font.Font(None, 48)

    grass_sheet = pygame.image.load("assets/grass_tile.png").convert_alpha()
    bramble_sheet = pygame.image.load("assets/bramble_bush_tile.png").convert_alpha()
    ice_cube_sheet = pygame.image.load("assets/ice_cube.png").convert_alpha()
    
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
                get_image(ice_cube_sheet, 0, 0, TILE_SIZE, TILE_SIZE, TILE_SIZE*1.5)
            ],
        },
    }

    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    goals = pygame.sprite.Group()
    barriers = pygame.sprite.Group()
    spikes = pygame.sprite.Group()
    ice_cubes = pygame.sprite.Group()
    camera = Camera(WIDTH, HEIGHT)
    
    current_level = 2
    collected_cubes = []
    current_room = pygame.Rect(TILE_SIZE, 0, (len(all_level[current_level-1][0])-2)*TILE_SIZE, (len(all_level[current_level-1])-1)*TILE_SIZE) 
    camera.set_bounds(current_room)
    
    render_level(all_sprites, platforms, goals, barriers, spikes, ice_cubes, tile_images, 1, current_level)

    player = Player(TILE_SIZE*3, TILE_SIZE*18)
    # all_sprites.add(player)
    game_state = "MENU"

    running = True
    while running:
        screen.fill((100, 100, 100))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if game_state == "MENU":
                    game_state = "PLAYING"
        if game_state == "MENU":
            screen.blit(bg_image, (0, 0))
            menu(screen, title_font, normal_font)
        elif game_state == "PLAYING":
            screen.blit(bg_image, (0, 0))
            player.update(platforms, barriers, spikes)
            camera.update(player)
            for cube in ice_cubes:
                cube.update()
                if cube.hitbox.colliderect(player.rect):
                    collected_cubes.append(cube.id)
                    cube.kill()
            for sprite in all_sprites:
                screen.blit(sprite.image, camera.apply(sprite))
            # for spike in spikes:
            #     debug_rect = spike.hitbox.move(camera.camera.topleft)
                
            #     pygame.draw.rect(screen, (255, 0, 0), debug_rect, 2)

            # player_debug = player.hitbox.move(camera.camera.topleft)
            # pygame.draw.rect(screen, (0, 255, 0), player_debug, 2)
            # for cube in ice_cubes:
            #     cube_debug = cube.hitbox.move(camera.camera.topleft)
            #     pygame.draw.rect(screen, (0, 255, 0), cube_debug, 2)
            player.draw(screen, camera)
            if pygame.sprite.spritecollide(player, goals, False):
                print("hello")
                current_level += 1
                current_room = pygame.Rect(TILE_SIZE, 0, (len(all_level[current_level-1][0])-2)*TILE_SIZE, (len(all_level[current_level-1])-1)*TILE_SIZE) 
                camera.set_bounds(current_room)
                render_level(all_sprites, platforms, goals, barriers, spikes, ice_cubes, tile_images, 1, current_level)
                # all_sprites.add(player)
                player.next_level(TILE_SIZE*3, TILE_SIZE*16)

        pygame.display.flip()
        clock.tick(60)
    print(collected_cubes)
    pygame.quit()
    sys.exit()




if __name__ == "__main__":
    run_game()
