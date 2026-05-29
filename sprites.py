import pygame
from settings import WIDTH, HEIGHT
import random
import math
from itertools import count

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

# class IceCube(pygame.sprite.Sprite):
#     def __init__(self, x, y, image):
#         super().__init__()
#         self.image = image.copy()
#         self.rect = self.image.get_rect(topleft = (x, y))
#         self.base_y = y
#         self.timer = random.uniform(0, 100)
        
#     def update(self):
#         self.timer += 0.1
        
#         bob_offset = math.sin(self.timer)*5
#         self.rect.y = self.base_y + bob_offset
        
#         canvas_size = max(self.rect.width, self.rect.height)*1.5
#         new_image = pygame.Surface((canvas_size, canvas_size), pygame.SRCALPHA)
        
#         pulse_radius = int(15 + math.sin(self.timer*2)*3)
#         glow_color = (255, 100, 150, 80)
        
#         pygame.draw.circle(new_image, glow_color, (canvas_size//2, canvas_size//2), pulse_radius)
#         cube_rect = self.image.get_rect(center=(canvas_size//2, canvas_size//2))
#         new_image.blit(self.image, cube_rect)
        
#         self.image = new_image

class IceCube(pygame.sprite.Sprite):
    _id_generator = count(1)
    def __init__(self, x, y, image):
        super().__init__()

        self.base_image = image.copy()
        self.image = self.base_image.copy()
        self.id = next(self._id_generator) 

        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = pygame.Rect(0, 0, 36, 36)
        self.hitbox.center = self.rect.center
        
        self.base_y = y
        self.timer = random.uniform(0, 100)

    
    def update(self):
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
        self.rect = self.image.get_rect(center=(self.rect.centerx, self.base_y + bob_offset))
        self.hitbox.center = self.rect.center