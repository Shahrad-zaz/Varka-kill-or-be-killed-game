from settings import *
from math import atan2,degrees

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.ground = True

class collisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf

        self.rect = self.image.get_frect(topleft = pos)

class Sword(pygame.sprite.Sprite):

    def __init__(self, player,groups):
        # player
        self.player = player
        self.distance = 100
        self.player_direction = pygame.Vector2()

        # sprite setup
        super().__init__(groups)
        self.sword_surf = pygame.image.load(join('image','sword','sword2.png')).convert_alpha()
        self.image = self.sword_surf
        self.rect = self.image.get_frect(center = self.player.rect.center + self.player_direction * self.distance)

    def get_direction(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WINDOWS_WIDTH / 2, WINDOWS_HEIGHT / 2)
        self.player_direction = (mouse_pos - player_pos).normalize()
        
    def rotate_sword(self):
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 180
        if self.player_direction.x > 0:
            self.image = pygame.transform.rotozoom(self.sword_surf, angle, 1.15)
            self.rect = self.image.get_frect(center = self.rect.center)

        else:
            self.image = pygame.transform.rotozoom(self.sword_surf, angle, 1.15)
            self.rect = self.image.get_frect(center = self.rect.center)
            
        
    def update(self, _):
        self.get_direction()
        self.rotate_sword()
        self.rect.center = self.player.rect.center + self.player_direction * self.distance

class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups):
        super().__init__(groups)
        self.direction = direction
        self.speed = 1200
        self.spawn_time = pygame.time.get_ticks()
        self.life_time = 1500
        angle1 = degrees(atan2(self.direction.x, self.direction.y)) - 90
        self.image = pygame.transform.rotozoom(surf, angle1, 1)
        self.rect = self.image.get_frect(center = pos)

    def update(self,dt):
        self.rect.center += self.direction * self.speed * dt

        if pygame.time.get_ticks() - self.spawn_time >= self.life_time:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites, sound):
        super().__init__(groups)
        self.player = player
        self.sound = sound
        # image 
        self.frames , self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]
        self.animation_speed = 6

        # rect
        self.rect = self.image.get_frect(center = pos)
        self.hitbox_rect = self.rect.inflate(-10,-20)
        self.collision_sprites = collision_sprites
        self.diraction = pygame.Vector2()
        self.speed = 150

        # timer
        self.death_time = 0
        self.death_duration=100

    def sound_death(self):
        self.sound.play()
    
    def animate(self,dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

    def move(self,dt):
        # get direction
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        self.direction = (player_pos - enemy_pos).normalize()

        # update the rect position + collision
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top     

    def destroy(self):
        # start timer
        self.death_time = pygame.time.get_ticks()
        # change the image
        surf = pygame.mask.from_surface(self.frames[0]).to_surface()
        surf.set_colorkey("black")
        self.image = surf
    def death_timer(self):
        if pygame.time.get_ticks() - self.death_time>= self.death_duration:
            self.kill()

    def update(self, dt):
        if self.death_time == 0:
            self.move(dt)
            self.animate(dt)
        else:
            # self.sound_death()
            self.death_timer()
            