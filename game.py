import pygame 
import sys
import random
from math import floor

WIDTH, HEIGHT = 800, 800
TILE_SIZE = 32
all_level = [
    [
        "B                                                                                    G",
        "B                                                                                    G",
        "B                                                                                    G",
        "B                                                                                    G",
        "B                                                                                    G",
        "B                                                                                    G",
        "B                                                                                    G",
        "B                                                                                    G",
        "B                                                  DDDDDDD                           G",
        "B                                                  DDDDDD                            G",
        "B                                                  DDDDDD                            G",
        "B                                                  DDDDDD                            G",
        "B                                                  DDDDD                             G",
        "B                                                  DDDDD                             G",
        "B                                                  DDDDD            DDDDD            G",
        "B                                                DDDDD                               G",
        "B                         DDDD                   DDDD                                G",
        "B                 DDDDD                          DDDD                                G",
        "B                                 DDDDD          DDDD              DDD               G",
        "B                                                DDDD              DDD               G",
        "DDDDDD    DDDDDDDDDD                       DDDDDDDDDDDDD       DDDDDDDDDDD     DDDDDDD",
        "DDDDDD    DDDDDDDDDD                       DDDDDDDDDDDDD       DDDDDDDDDDD     DDDDDDD",
        "DDDDDD    DDDDDDDDDD                       DDDDDDDDDDDDD       DDDDDDDDDDD     DDDDDDD",    
        "DDDDDD    DDDDDDDDDD                       DDDDDDDDDDDDD       DDDDDDDDDDD     DDDDDDD",
        "DDDDDD    DDDDDDDDDD                       DDDDDDDDDDDDD       DDDDDDDDDDD     DDDDDDD",            
        "DDDDDD    DDDDDDDDDD                       DDDDDDDDDDDDD       DDDDDDDDDDD     DDDDDDD",            
        "DDDDDD    DDDDDDDDDD                       DDDDDDDDDDDDD       DDDDDDDDDDD     DDDDDDD",             
    ],
    [ 
        "D                         G",
        "D                         G",
        "D                         G",
        "D                         G",
        "D                         G",
        "D                    DDDDDD",
        "D                        DD",
        "D    DDD                 DD",
        "D    DDD                 DD",
        "D^^^^DDD                 DD",
        "DDDDDDD                  DD",
        "DDDDD            DD      DD",
        "DDDD             DD      DD",
        "DD                       DD",
        "DD                       DD",
        "D                      DDDD",
        "D                      DDDD",
        "D                      DDDD",
        "B                    DDDDDD",
        "B                        DD",
        "B                        DD",
        "DDDDDD    DDDDD          DD",
        "DDDDDD    DDDDD    ^^^^^^DD",
        "DDDDDD^^^^DDDDD^^^^DDDDDDDD",    
        "DDDDDDDDDDDDDDDDDDDDDDDDDDD",
        "DDDDDDDDDDDDDDDDDDDDDDDDDDD",
    ]
]
class Camera:
    def __init__(self, width, height):

        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.bounds = pygame.Rect(0, 0 , width, height)
        
    def set_bounds(self, room_rect):
        self.bounds = room_rect    
        
    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)
    
    def update(self, target):
        x = -target.rect.x + WIDTH // 2
        y = -target.rect.y + HEIGHT // 2
        
        
        x = min(-self.bounds.left, x) # stop if close to left border
        x = max(-(self.bounds.right - WIDTH), x) #stop if close to right border
        y = min(-self.bounds.top, y) #stop if close to top border
        y = max(-(self.bounds.bottom - HEIGHT), y) #stop if close to down border
        
        self.camera = pygame.Rect(x, y, self.width, self.height)

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, image, inner_ur, inner_ul, inner_dr, inner_dl, patch):
        super().__init__()
        self.image = image.copy()
        self.rect = self.image.get_rect(topleft = (x, y))
        if inner_ur:
            self.image.blit(patch, (0, 0))
        if inner_ul:
            ul_patch = pygame.transform.flip(patch, True, False)
            self.image.blit(ul_patch, (0, 0))
        if inner_dr:
            dr_patch = pygame.transform.flip(patch, False, True)
            self.image.blit(dr_patch, (0, 0))
        if inner_dl:
            dl_patch = pygame.transform.flip(patch, True, True)
            self.image.blit(dl_patch, (0, 0))        

class Barrier(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft = (x, y))

class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft = (x, y))
        
class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft = (x, y))
        self.hitbox = pygame.Rect(x+5, y + (self.rect.height // 2), self.rect.width-10, self.rect.height // 2)        

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        sprite_sheet = pygame.image.load("assets/slime.png").convert_alpha()
        
        self.jump_right_frames = []
        self.jump_left_frames = []
                
        for i in range(8):
            frame = get_image(sprite_sheet, i * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE, TILE_SIZE*1.5)
            self.jump_right_frames.append(frame)
            frame_left = pygame.transform.flip(frame, True, False)
            self.jump_left_frames.append(frame_left)
            
            
        self.dash_frame = {}
        dash_right = []
        dash_up = []
        dash_up_right = []
        for i in range(8, 32):
            frame = get_image(sprite_sheet, i * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE, TILE_SIZE*1.5)
            if i < 16:
                dash_right.append(frame)
            elif i < 24:
                dash_up.append(frame)
            else:
                dash_up_right.append(frame)
        self.dash_frame[(1, 0)] = dash_right
        self.dash_frame[(-1, 0)] = [pygame.transform.flip(img, True, False) for img in dash_right]
        self.dash_frame[(0, -1)] = dash_up
        self.dash_frame[(0, 1)] = [pygame.transform.flip(img, False, True) for img in dash_up]
        self.dash_frame[(1, -1)] = dash_up_right
        self.dash_frame[(1, 1)] = [pygame.transform.flip(img, False, True) for img in dash_up_right]
        self.dash_frame[(-1, -1)] = [pygame.transform.flip(img, True, False) for img in dash_up_right]
        self.dash_frame[(-1, 1)] = [pygame.transform.flip(img, True, True) for img in dash_up_right]
        self.dash_dir = (1, 0)
        
        self.climb_frame_right = []
        self.climb_frame_left = []
        for i in range(32, 35):
            frame = get_image(sprite_sheet, i*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE, TILE_SIZE*1.5)
            self.climb_frame_right.append(frame)
            left_frame = pygame.transform.flip(frame, True, False)
            self.climb_frame_left.append(left_frame)
              
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.2
        self.trail = []
        self.face = "right"
        self.state = "idle"
        
        self.image = self.jump_right_frames[self.current_frame]
        self.rect = self.image.get_rect(topleft = (x,y))
        self.hitbox = pygame.Rect(x+8, y + (self.rect.height * 2/5), self.rect.width-16, self.rect.height *3/5)        


        self.spawn_x = x
        self.spawn_y = y
        self.speed = 5
        self.velocity_x = 0
        
        self.velocity_y = 0
        self.gravity = 0.5
        self.jump = True
        self.jump_speed = 12
        self.coyote_timer = 0
        self.coyote_time = 6
        
        self.dash = False
        self.can_dash = True
        self.dash_friction = 0.85
        self.dash_velocity_x = 0
        self.dash_velocity_y = 0
        self.dash_max_velocity = 25
        
        self.grab = False
        self.climb = False
        self.climb_velocity = 0
        
        self.input_lock = 0
        
    def update(self, platforms, barriers, spikes):
        self.handle_input()
        self.apply_physics(platforms, barriers)
        self.update_animation()
        self.death_check(spikes)
        self.update_trail()
    
    
    def handle_input(self):
        keys = pygame.key.get_pressed()      
        
        if self.input_lock > 0:
            self.input_lock -= 1
            
        #walk
        if not self.dash and self.input_lock == 0:
            self.velocity_x = 0
            if keys[pygame.K_LEFT]:
                self.velocity_x -= self.speed
                self.face = "left"
            if keys[pygame.K_RIGHT]:
                self.velocity_x += self.speed
                self.face = "right"
            
        #dash    
        if keys[pygame.K_x] and not self.dash and self.can_dash:
            self.dash = True
            self.can_dash = False
            self.state = "dashing"
            self.animation_timer = 0
            
            x_dir = 0
            y_dir = 0
            
            if keys[pygame.K_LEFT]: x_dir = -1
            if keys[pygame.K_RIGHT]: x_dir = 1
            if keys[pygame.K_UP]: y_dir = -1
            if keys[pygame.K_DOWN]: y_dir = 1
            if x_dir == 0 and y_dir == 0:
                x_dir = 1 if self.face == "right" else -1
            
            self.dash_dir = (x_dir, y_dir)
            
            if x_dir != 0 and y_dir != 0:
                x_dir *= 0.707
                y_dir *= 0.707
            
            self.dash_velocity_x = x_dir * self.dash_max_velocity
            self.dash_velocity_y = y_dir * self.dash_max_velocity
        #jump
        if keys[pygame.K_SPACE]:    
            if not self.jump and self.velocity_y == 0:
                self.velocity_y = -self.jump_speed
                self.jump = True
            elif not self.jump and self.coyote_timer > 0:
                self.velocity_y = -self.jump_speed
                self.jump = True
                self.coyote_timer = 0
        
        #climb
        self.climb_velocity = 0
        self.grab = keys[pygame.K_z]
        if keys[pygame.K_UP]:
            self.climb_velocity = -3
        elif keys[pygame.K_DOWN]:
            self.climb_velocity = 3
        
        return self.velocity_x
    
    
    def apply_physics(self, platforms, barriers):
        if self.dash:
            self.velocity_x = self.dash_velocity_x
            self.velocity_y = self.dash_velocity_y
            self.dash_velocity_x *= self.dash_friction
            self.dash_velocity_y *= self.dash_friction
            
            if abs(self.dash_velocity_x) <= 2 and abs(self.dash_velocity_y) <= 2:
                self.dash = False
                self.state = "idle"
                if self.velocity_y < 0:
                    self.velocity_y = 0
                elif self.velocity_y > 0:
                    self.velocity_y = 8
            
        
        self.rect.x += self.velocity_x  
        
        #check horizontal collision
        hits = pygame.sprite.spritecollide(self, platforms, False) or pygame.sprite.spritecollide(self, barriers, False)
        for hit in hits:
            if self.velocity_x > 0:
                self.rect.right = hit.rect.left
            elif self.velocity_x < 0:
                self.rect.left = hit.rect.right
            
            if self.dash:
                # self.dash = False
                self.dash_velocity_x = 0
                # if self.velocity_y < 0:
                #     self.velocity_y = -self.jump_speed


        
        #climb
        self.rect.x -= 1
        touch_left = len(pygame.sprite.spritecollide(self, platforms, False)) > 0
        self.rect.x += 2
        touch_right = len(pygame.sprite.spritecollide(self, platforms, False)) > 0
        self.rect.x -= 1
        
        on_wall = touch_right or touch_left
        keys = pygame.key.get_pressed()
        jump_pressed = keys[pygame.K_SPACE]

        if jump_pressed and on_wall:
            #wall bounce
            if self.dash and self.velocity_y < 0:
                self.dash = False
                self.velocity_y = -self.jump_speed 
                self.jump = True
                self.input_lock = 12
                
                if touch_left:
                    self.velocity_x = self.speed
                elif touch_right:
                    self.velocity_x = -self.speed
                    
            #wall jump
            elif self.velocity_y > 0:
                self.climb = False
                self.velocity_y = -self.jump_speed +5
                self.jump = True
                self.input_lock = 10

                if touch_left:
                    self.velocity_x = self.speed+5
                elif touch_right:
                    self.velocity_x = -self.speed-5
        
        
        if on_wall and self.grab and not self.dash:
            self.climb = True
            self.velocity_y = self.climb_velocity
            self.jump = False
            
            if self.climb_velocity < 0:
                wall_dir = 1 if touch_right else -1
                wall_x = self.rect.right + 2 if touch_right else self.rect.left - 2
                
                head_rect = pygame.Rect(wall_x, self.rect.top, 2, 2)
                head_hitting_wall = any(head_rect.colliderect(p.rect) for p in platforms)
                
                if not head_hitting_wall:
                    self.rect.y -= 15 
                    self.velocity_x = wall_dir * self.speed*2
                    self.climb = False
                    self.input_lock = 2
                    
            if self.climb_velocity > 0:
                self.state = "climbing_down"
            elif self.climb_velocity < 0:
                self.state = "climbing_up"
            else:
                self.state = "climbing_idle"
        else:
            self.climb = False

        
        #vertical
        was_falling = self.velocity_y > 0
        
        if not self.climb:
            self.velocity_y += self.gravity
            
        self.rect.y += self.velocity_y
        
        #check vertical collision
        hits = pygame.sprite.spritecollide(self, platforms, False) or pygame.sprite.spritecollide(self, barriers, False)
        for hit in hits:
            if self.velocity_y > 0:
                self.rect.bottom = hit.rect.top
                self.velocity_y = 0 
                self.jump = False
                self.coyote_timer = self.coyote_time
                if self.dash == False:
                    self.can_dash = True
                
                if was_falling:
                    self.state = "landing"
                    self.animation_timer = 0
                    
            elif self.velocity_y < 0:
                self.rect.top = hit.rect.bottom
                self.velocity_y = 0
                self.dash_velocity_y = 0
                self.dash = False
              
                
    def update_animation(self):
        if self.state not in ("landing", "dashing") and not self.climb:
            if self.velocity_y < -2:
                self.state = "jumping"
            elif -2 <= self.velocity_y <= 2 and self.jump:
                self.state = "floating"
            elif self.velocity_y > 2:
                self.state = "falling"
            elif self.velocity_y == 0:
                self.state = "idle"
        
        
        if self.state == "idle":
            self.current_frame = 0
            
        elif self.state == "jumping":
            self.animation_timer += 0.2
            if self.animation_timer < 1:
                self.current_frame = 1 
            else:
                self.current_frame = 2
                
        elif self.state == "floating":
            self.current_frame = 3
            
        elif self.state == "falling":
            self.current_frame = 4 
            
        elif self.state == "landing":
            self.animation_timer += 0.3 
            if self.animation_timer < 1:
                self.current_frame = 5 
            elif self.animation_timer < 2:
                self.current_frame = 6 
            elif self.animation_timer < 3:
                self.current_frame = 7 
            else:
                self.state = "idle"
                self.current_frame = 0
    
        elif self.state == "dashing":
            self.animation_timer += 0.5
            self.current_frame = min(7, floor(self.animation_timer))
        
        
        if self.state == "dashing":
            if self.dash_dir in ((0, 1), (0, -1)) and self.face == "left":
                self.image = pygame.transform.flip(self.dash_frame[self.dash_dir][self.current_frame], True, False)
            else:
                self.image = self.dash_frame[self.dash_dir][self.current_frame]
        elif not self.can_dash and self.state == "falling":
            if self.face == "right":
                self.image = self.dash_frame[(1, 0)][7]
            else:
                self.image = self.dash_frame[(-1, 0)][7]
        elif "climbing" in self.state:
            if self.state == "climbing_up":
                self.current_frame = 1
            elif self.state == "climbing_idle":
                self.current_frame = 0
            else:
                self.current_frame = 2
            if self.face ==  "right":
                self.image = self.climb_frame_right[self.current_frame]
            else:
                self.image = self.climb_frame_left[self.current_frame]
        else:
            if self.face == "right":
                self.image = self.jump_right_frames[self.current_frame]
            else:
                self.image = self.jump_left_frames[self.current_frame]        

        if not self.can_dash:
            tinted_image = self.image.copy()
            
            light_blue_gray = (170, 190, 210, 150)
            mask = pygame.mask.from_surface(tinted_image)
            tint_overlay = mask.to_surface(setcolor=light_blue_gray, unsetcolor=(0,0,0,0))
            
            tinted_image.blit(tint_overlay, (0, 0))
            
            self.image = tinted_image
            
            
        self.hitbox = pygame.Rect(self.rect.x+8, self.rect.y + (self.rect.height * 2/5), self.rect.width-16, self.rect.height *3/5)        


    def death_check(self, spikes):
        if self.rect.y > 800:
            self.die_and_respawn()
        
        for spike in spikes:
            if self.hitbox.colliderect(spike.hitbox):
                self.die_and_respawn()
                break
    
    
    def update_trail(self):
        if self.dash:
            new_ghost = [self.image.copy(), self.rect.copy(), 150]
            self.trail.append(new_ghost)
            
        for ghost in self.trail:
            ghost[2] -= 15
        self.trail = [ghost for ghost in self.trail if ghost[2] > 0]
      
    
    def draw(self, surface, camera):
        for ghost in self.trail:
            ghost_image, ghost_rect, alpha = ghost
            ghost_image.set_alpha(alpha)
            ghost_rect = ghost_rect.move(camera.camera.topleft)
            
            surface.blit(ghost_image, ghost_rect)
            
        surface.blit(self.image, camera.apply(self))
    
                
    def die_and_respawn(self):
        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y
        self.velocity_y = 0
    
    
    def next_level(self, x, y):
        self.spawn_x = x
        self.spawn_y = y
        self.rect = pygame.Rect(x, y, TILE_SIZE*1.5, TILE_SIZE*1.5)
        self.velocity_x = 0
        self.velocity_y = 0
        
def menu(screen, title_font, instruction_font):
    screen.fill((140, 192, 235))
    title_text = title_font.render("PLATFORMER", True, (255, 255, 255))
    title_rect = title_text.get_rect(center = (WIDTH // 2, HEIGHT // 2 - 100))
    
    instruction_text = instruction_font.render("Press ANY KEY to Start", True, (255, 255, 255))
    instruction_rect = instruction_text.get_rect(center = (WIDTH //2, HEIGHT //2 + 150))
    
    screen.blit(title_text, title_rect)
    screen.blit(instruction_text, instruction_rect)

def get_image(sheet, x, y, width, height, scale):
    image = pygame.Surface((width, height), pygame.SRCALPHA)
    image.blit(sheet, (0, 0), (x, y, width, height))
    
    return pygame.transform.scale(image, (scale, scale))

def render_level(all_sprites, platforms, goals, barriers, spikes, tile_images, seed, level_idx):
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
            is_spike = False
            is_goal = False
            is_barrier = False
            vertical_flip = False
            horizontal_flip = False
            match cell:
                case " ":
                    continue
                case "G":
                    is_goal = True
                case "B":
                    is_barrier = True
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
                    image_list = tile_images["bramble"]["normal"]
                    is_spike = True
            if image_list:
                image = random.choice(image_list)
            if horizontal_flip or vertical_flip:    
                image = pygame.transform.flip(image, horizontal_flip, vertical_flip)
            x_pos = col_idx * TILE_SIZE
            y_pos = row_idx * TILE_SIZE
            
            if is_spike:
                new_sprite = Spike(x_pos, y_pos, image)
                spikes.add(new_sprite)
            elif is_goal:
                new_sprite = Goal(x_pos, y_pos)
                goals.add(new_sprite)
            elif is_barrier:
                new_sprite = Barrier(x_pos, y_pos)
                barriers.add(new_sprite)
            else:
                new_sprite = Platform(x_pos, y_pos, image, inner_ur, inner_ul, inner_dr, inner_dl, patch)
                platforms.add(new_sprite)
            
            all_sprites.add(new_sprite)
            


def run_game():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    title_font = pygame.font.Font(None, 108)
    normal_font = pygame.font.Font(None, 48)

    grass_sheet = pygame.image.load("assets/grass_tile.png").convert_alpha()
    bramble_sheet = pygame.image.load("assets/bramble_bush_tile.png").convert_alpha()
    
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
    }

    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    goals = pygame.sprite.Group()
    barriers = pygame.sprite.Group()
    spikes = pygame.sprite.Group() 
    camera = Camera(WIDTH, HEIGHT)
    
    current_level = 1
    current_room = pygame.Rect(TILE_SIZE, 0, (len(all_level[current_level-1][0])-2)*TILE_SIZE, (len(all_level[current_level-1])-2)*TILE_SIZE) 
    camera.set_bounds(current_room)
    
    render_level(all_sprites, platforms, goals, barriers, spikes, tile_images, 1, current_level)

    player = Player(TILE_SIZE*3, TILE_SIZE*18)
    # all_sprites.add(player)
    game_state = "MENU"

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if game_state == "MENU":
                    game_state = "PLAYING"
        if game_state == "MENU":
            menu(screen, title_font, normal_font)
        elif game_state == "PLAYING":
            screen.fill((191, 221, 240))
            player.update(platforms, barriers, spikes)
            camera.update(player)
            for sprite in all_sprites:
                screen.blit(sprite.image, camera.apply(sprite))
            # for spike in spikes:
            #     debug_rect = spike.hitbox.move(camera.camera.topleft)
                
            #     pygame.draw.rect(screen, (255, 0, 0), debug_rect, 2)

            # player_debug = player.hitbox.move(camera.camera.topleft)
            # pygame.draw.rect(screen, (0, 255, 0), player_debug, 2)
            player.draw(screen, camera)
            if pygame.sprite.spritecollide(player, goals, False):
                print("hello")
                current_level += 1
                current_room = pygame.Rect(TILE_SIZE, 0, (len(all_level[current_level-1][0])-2)*TILE_SIZE, (len(all_level[current_level-1])-2)*TILE_SIZE) 
                camera.set_bounds(current_room)
                render_level(all_sprites, platforms, goals, barriers, spikes, tile_images, 1, current_level)
                # all_sprites.add(player)
                player.next_level(TILE_SIZE*3, TILE_SIZE*16)

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
    sys.exit()