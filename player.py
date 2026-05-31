import pygame
from utils import get_image
from settings import TILE_SIZE
from math import floor

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
        self.hitbox_y_offset = 0
        
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
        
        self.collected_cubes = []
        self.follow_cubes = []
        self.position_history = []
        self.is_grounded = False
        self.grounded_timer = 0
        
        self.death_count = 0
        
    def update(self, platforms, barriers, spikes, fungi, level):
        self.handle_input()
        self.apply_physics(platforms, barriers, fungi)
        self.update_animation()
        self.death_check(spikes, level)
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
    
    
    def apply_physics(self, platforms, barriers, fungi):
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
                self.dash_velocity_x = 0



        
        #climb
        self.rect.x -= 1
        self.touch_left = len(pygame.sprite.spritecollide(self, platforms, False)) > 0
        self.rect.x += 2
        self.touch_right = len(pygame.sprite.spritecollide(self, platforms, False)) > 0
        self.rect.x -= 1
        
        on_wall = self.touch_right or self.touch_left
        keys = pygame.key.get_pressed()
        jump_pressed = keys[pygame.K_SPACE]

        if jump_pressed and on_wall:
            #wall bounce
            if self.dash and self.velocity_y < 0:
                self.dash = False
                self.velocity_y = -self.jump_speed 
                self.jump = True
                self.input_lock = 12
                
                if self.touch_left:
                    self.velocity_x = self.speed
                elif self.touch_right:
                    self.velocity_x = -self.speed
                    
            #wall jump
            elif self.velocity_y > 0:
                self.climb = False
                self.velocity_y = -self.jump_speed+3
                self.jump = True
                self.input_lock = 10

                if self.touch_left:
                    self.velocity_x = self.speed+7
                elif self.touch_right:
                    self.velocity_x = -self.speed-7
        
        
        if on_wall and self.grab and not self.dash:
            self.climb = True
            self.velocity_y = self.climb_velocity
            self.jump = False
            
            if self.climb_velocity < 0:
                wall_dir = 1 if self.touch_right else -1
                wall_x = self.rect.right + 2 if self.touch_right else self.rect.left - 2
                
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
        self.is_grounded = False
        
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
                self.is_grounded = True
                
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
                
        #fungi stuff
        
        fungi_hits = pygame.sprite.spritecollide(self, fungi, False)
        for fungus in fungi_hits:
            if fungus.direction == "up":
                self.velocity_y = -15
            elif fungus.direction == "down":
                self.velocity_y = 15
            elif fungus.direction == "right":
                self.velocity_x = 15
                self.input_lock = 15
            elif fungus.direction == "left":
                self.velocity_x = -15
                self.input_lock = 10
            self.jump = True
            self.dash = False
            self.can_dash = True
            fungus.state = "bounce"
        
        
        #ice cube stuff
        self.position_history.insert(0, self.rect.center)
        if len(self.position_history) > 100: # We only need to remember the last 100 frames
            self.position_history.pop()
                
        #grounded timer
        if self.is_grounded and not self.dash:
            self.grounded_timer += 1
        else:
            self.grounded_timer = 0
        
        if self.grounded_timer >= 30 and len(self.follow_cubes) > 0:
            for cube in self.follow_cubes:
                cube.state = "securing"
                cube.timer = 0
                self.collected_cubes.append(cube.id)
            self.follow_cubes.clear()
        
              
                
    def update_animation(self):
        self.hitbox_y_offset = 0
        
        if self.state not in ("landing", "dashing") and not self.climb:
            if self.velocity_y < -2:
                self.state = "jumping"
                self.hitbox_y_offset = -5
            elif -2 <= self.velocity_y <= 2 and self.jump:
                self.state = "floating"
                self.hitbox_y_offset = -10
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
            if self.touch_right:
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
            
            # light_blue_gray = (170, 190, 210, 150)
            cooldown_color = (255, 247, 197, 130)
            mask = pygame.mask.from_surface(tinted_image)
            tint_overlay = mask.to_surface(setcolor= cooldown_color, unsetcolor=(0,0,0,0))
            
            tinted_image.blit(tint_overlay, (0, 0))
            
            self.image = tinted_image
            
            
        self.hitbox = pygame.Rect(self.rect.x+8, self.rect.y + (self.rect.height * 2/5) + self.hitbox_y_offset, self.rect.width-16, self.rect.height *3/5)        


    def death_check(self, spikes, cur_level):
        if self.rect.y > 800:
            self.die_and_respawn(cur_level)
        
        for spike in spikes:
            if self.hitbox.colliderect(spike.hitbox):
                self.die_and_respawn(cur_level)
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
    
                
    def die_and_respawn(self, cur_level):
        self.death_count += 1
        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y
        self.input_lock = 20
        self.dash_velocity_x = 0
        self.dash_velocity_y = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.dash = False
        self.state = "idle"
        for cube in self.follow_cubes:
            cube.reset()
            if cube.level != cur_level:
                cube.kill()
        self.follow_cubes.clear()
        self.position_history.clear()
        
    
    
    def next_level(self, x, y):
        self.spawn_x = x
        self.spawn_y = y
        self.rect = pygame.Rect(x, y, TILE_SIZE*1.5, TILE_SIZE*1.5)
        self.velocity_x = 0
        self.velocity_y = 0
        self.dash_velocity_x = 0
        self.dash_velocity_y = 0
        self.dash = False
        self.state = "idle"
        self.grounded_timer = 0
        
        self.position_history.clear() 
        
        for cube in self.follow_cubes:
            cube.rect.center = self.rect.center