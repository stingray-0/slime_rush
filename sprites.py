import pygame
from settings import WIDTH, HEIGHT, TILE_SIZE
import random
import math
from utils import get_image
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
    def __init__(self, x, y, image, direction):
        super().__init__()
        if direction == "up":
            self.image = image
        elif direction == "down":
            self.image = pygame.transform.flip(image, False, True) # Ceiling
        elif direction == "right":
            self.image = pygame.transform.rotate(image, -90) # Left wall, pointing right
        elif direction == "left":
            self.image = pygame.transform.rotate(image, 90)
            
        self.rect = self.image.get_rect(topleft = (x, y))
        
        if direction == "up":
            self.hitbox = pygame.Rect(x, y + (self.rect.height // 2), self.rect.width, self.rect.height // 2)
        elif direction == "down":
            self.hitbox = pygame.Rect(x, y, self.rect.width, self.rect.height // 2)
        elif direction == "right":
            self.hitbox = pygame.Rect(x, y, self.rect.width // 2, self.rect.height)
        elif direction == "left":
            self.hitbox = pygame.Rect(x + (self.rect.width // 2), y, self.rect.width // 2, self.rect.height)       


class Fungi(pygame.sprite.Sprite):
    animations = {} 

    @classmethod
    def load_animations(cls, sheet):
        base_frames = []
        for i in range(5):
            frame = get_image(sheet, TILE_SIZE*i, 0, TILE_SIZE, TILE_SIZE, TILE_SIZE)
            base_frames.append(frame)
            
        cls.animations["up"] = base_frames
        cls.animations["down"] = [pygame.transform.flip(f, False, True) for f in base_frames]
        cls.animations["right"] = [pygame.transform.rotate(f, -90) for f in base_frames]
        cls.animations["left"] = [pygame.transform.rotate(f, 90) for f in base_frames]
        
    def __init__(self, x, y, direction):
        super().__init__()
        
        self.direction = direction
        
        self.frames = Fungi.animations[direction]
        self.image = self.frames[0] 
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = pygame.Rect(x + 4, y + 4, self.rect.width - 8, self.rect.height - 8)
        self.state = "idle"
        self.animation_timer = 0
    
    def update(self):
        if self.state == "idle":
            self.image = self.frames[0]
        elif self.state == "bounce":
            self.animation_timer += 0.2
            if self.animation_timer < 1:
                self.image = self.frames[1]
            elif self.animation_timer < 2:
                self.image = self.frames[2]
            elif self.animation_timer < 3:
                self.image = self.frames[3]
            elif self.animation_timer < 4:
                self.image = self.frames[4]
            else:
                self.state = "idle"
                self.animation_timer = 0
                
class IceCube(pygame.sprite.Sprite):
    def __init__(self, x, y, image, level, id):
        super().__init__()

        self.base_image = image.copy()
        self.image = self.base_image.copy()
        self.id = id
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = pygame.Rect(0, 0, 36, 36)
        self.hitbox.center = self.rect.center
        
        self.spawn_x = x
        self.spawn_y = y
        self.timer = random.uniform(0, 100)
        self.state = "idle"
        self.level = level

    
    def update(self, player):
        if self.state == "idle":
            self.timer += 0.1
            
            max_dim = max(self.base_image.get_width(), self.base_image.get_height())
            canvas_size = int(max_dim * 2.5) 
            new_image = pygame.Surface((canvas_size, canvas_size), pygame.SRCALPHA)
            center_coords = (canvas_size // 2, canvas_size // 2)

            mask = pygame.mask.from_surface(self.base_image)
            
            glow_color = (94, 215, 255, 100) #pink
            mask_surface = mask.to_surface(setcolor=glow_color, unsetcolor=(0, 0, 0, 0))
            
            pulse_scale = 1.2 + math.sin(self.timer * 2) * 0.1
            new_w = int(self.base_image.get_width() * pulse_scale)
            new_h = int(self.base_image.get_height() * pulse_scale)
            

            glow_surface = pygame.transform.smoothscale(mask_surface, (new_w, new_h))
            glow_rect = glow_surface.get_rect(center=center_coords)
            
            new_image.blit(glow_surface, glow_rect)
            
            cube_rect = self.base_image.get_rect(center=center_coords)
            new_image.blit(self.base_image, cube_rect)
            
            self.image = new_image
            
            bob_offset = math.sin(self.timer) * 5
            self.rect = self.image.get_rect(center=(self.rect.centerx, self.spawn_y + bob_offset))
            self.hitbox.center = self.rect.center
            
        elif self.state == "following":
            follow_idx = player.follow_cubes.index(self)
            target_history_index = (follow_idx + 1) * 15
            
            if target_history_index < len(player.position_history):
                target_pos = player.position_history[target_history_index]
                
                self.rect.centerx += (target_pos[0] - self.rect.centerx) * 0.2
                self.rect.centery += (target_pos[1] - self.rect.centery) * 0.2
                
        elif self.state == "securing":
            self.rect.y -= 5
            self.timer += 1
            if self.timer > 20:
                self.kill()
        
    def reset(self):
        self.state = "idle"
        self.rect.center = (self.spawn_x, self.spawn_y)