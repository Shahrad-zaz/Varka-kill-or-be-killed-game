from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.load_images()
        self.state , self.frame_index = 'down', 0
        self.image = pygame.image.load(join('image','player','down','0.png')).convert_alpha()
        self.rect = self.image.get_frect(center = pos)
        self.hitbox = self.rect.inflate(-20,-90)
        # movement
        self.speed = 400
        self.direction = pygame.Vector2()
        self.collision_sprites = collision_sprites

    def load_images(self):
        self.frame = {'left': [], 'right': [], 'up': [], 'down': []}

        for state in self.frame.keys():
            for folder_path, subfolders, file_names in walk(join('image','player', state)):
                if file_names:
                    for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
                        full_path = join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.frame[state].append(surf)
                        self.frame[state].append(surf)

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction

    def move(self,dt):
        self.hitbox.x +=self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox.y +=self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if self.hitbox.colliderect(sprite.rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox.left = sprite.rect.right
                elif direction == 'vertical':
                    if self.direction.y < 0: self.hitbox.top = sprite.rect.bottom
                    if self.direction.y > 0: self.hitbox.bottom = sprite.rect.top

    def animate(self, dt):
        # get state
        if self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'
        if self.direction.y != 0:
            self.state = 'down' if self.direction.y > 0 else 'up'

        # animate
        self.frame_index = self.frame_index + 10 * dt if self.direction else 0
        self.image = self.frame[self.state][int(self.frame_index) % len(self.frame[self.state])]
    
    def update(self,dt ):
        self.input()
        self.move(dt)
        self.animate(dt)