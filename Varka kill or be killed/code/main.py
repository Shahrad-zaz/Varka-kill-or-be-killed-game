from settings import *
from player import Player
from sprites import *
from random import randint, choice
from pytmx.util_pygame import load_pygame
from groups import Allsprites

class Game:
    def __init__(self):

        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOWS_WIDTH, WINDOWS_HEIGHT))
        pygame.display.set_caption('Kill Or Be Killed')
        icon_image = pygame.image.load("image/icon/icon.ico")
        pygame.display.set_icon(icon_image) 
        self.clock = pygame.time.Clock()
        self.running = True
        self.bullet_index = 0
        
        self.state = 'start_menu'
        self.fullscreen = False
        
        self.score = 0
        self.score_timer = 0

        #Group
        self.all_sprites = Allsprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.sword_sprites = pygame.sprite.Group()
        self.players_sprites = pygame.sprite.Group()

        # sword timer
        self.can_shoot = True
        self.shoot_time = 0
        self.sword_cooldown = 2000

        # enemy timer
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 400)
        self.spawn_position = []

        # audio
        self.shoot_sound1 = pygame.mixer.Sound(join('audio','woosh1.mp3'))
        self.shoot_sound1.set_volume(0.7)

        self.slash1 = pygame.mixer.Sound(join('audio','slash1_0.mp3'))
        self.slash1.set_volume(0.7)

        self.slash2 = pygame.mixer.Sound(join('audio','slash2_0.mp3'))
        self.slash2.set_volume(0.7)

        self.shoot_sound2 = pygame.mixer.Sound(join('audio','woosh2.mp3'))
        self.shoot_sound2.set_volume(0.7)

        self.impact_sound = pygame.mixer.Sound(join('audio','bullet_impact_0.mp3'))
        self.impact_sound.set_volume(0.7)

        self.varka_sound = pygame.mixer.Sound(join('audio','varka.mp3'))
        self.varka_sound.set_volume(0.7)
        
        self.music = pygame.mixer.Sound(join('audio','music.mp3'))
        self.music.set_volume(0.7)
        self.music.play(loops=-1)
        # setup
        self.load_images()
        self.setup()

    def reset_game(self):
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.bullet_sprites.empty()
        self.enemy_sprites.empty()
        self.sword_sprites.empty()
        self.players_sprites.empty()
        self.spawn_position.clear()
        
        self.score = 0
        self.score_timer = 0
        self.can_shoot = True
        self.setup()
        self.state = 'playing'

    def draw_text(self, text, size, color, pos):
        font = pygame.font.Font(None, size)
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_frect(center=pos)
        self.display_surface.blit(text_surf, text_rect)
        return text_rect

    def draw_start_menu(self, mouse_clicked):
        scale_size = (WINDOWS_WIDTH // 8, WINDOWS_HEIGHT // 8)
        small = pygame.transform.smoothscale(self.display_surface, scale_size)
        blurred = pygame.transform.smoothscale(small, (WINDOWS_WIDTH, WINDOWS_HEIGHT))
        self.display_surface.blit(blurred, (0, 0))

        controls = [
            "W  to go up",
            "A  to go left",
            "S  to go down",
            "D  to go right",
            "Left click to shoot",
            "Right click to change elements",
            "F11 to go fullscreen",
            "ESC to pause the game"
        ]
        y_offset = 20
        font = pygame.font.Font(None, 36)
        for text in controls:
            surf = font.render(text, True, 'white')
            self.display_surface.blit(surf, (20, y_offset))
            y_offset += 30

        self.draw_text('Kill Or Be Killed', 100, 'white', (WINDOWS_WIDTH/2, WINDOWS_HEIGHT/3))
        start_rect = self.draw_text('Start Game', 60, 'white', (WINDOWS_WIDTH/2, WINDOWS_HEIGHT/2))
        
        if mouse_clicked and start_rect.collidepoint(pygame.mouse.get_pos()):
            self.state = 'playing'

    def draw_pause_screen(self, mouse_clicked):
        scale_size = (WINDOWS_WIDTH // 8, WINDOWS_HEIGHT // 8)
        small = pygame.transform.smoothscale(self.display_surface, scale_size)
        blurred = pygame.transform.smoothscale(small, (WINDOWS_WIDTH, WINDOWS_HEIGHT))
        self.display_surface.blit(blurred, (0, 0))

        overlay = pygame.Surface((WINDOWS_WIDTH, WINDOWS_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.display_surface.blit(overlay, (0,0))
        self.draw_text('PAUSED', 100, 'white', (WINDOWS_WIDTH/2, WINDOWS_HEIGHT/3))
        resume_rect = self.draw_text('Resume (ESC)', 60, 'white', (WINDOWS_WIDTH/2, WINDOWS_HEIGHT/2))
        
        if mouse_clicked and resume_rect.collidepoint(pygame.mouse.get_pos()):
            self.state = 'playing'

    def draw_game_over_screen(self, mouse_clicked):
        scale_size = (WINDOWS_WIDTH // 8, WINDOWS_HEIGHT // 8)
        small = pygame.transform.smoothscale(self.display_surface, scale_size)
        blurred = pygame.transform.smoothscale(small, (WINDOWS_WIDTH, WINDOWS_HEIGHT))
        self.display_surface.blit(blurred, (0, 0))

        overlay = pygame.Surface((WINDOWS_WIDTH, WINDOWS_HEIGHT), pygame.SRCALPHA)
        overlay.fill((139, 0, 0, 100))
        self.display_surface.blit(overlay, (0,0))

        self.draw_text('YOU DIED', 120, 'black', (WINDOWS_WIDTH/2, WINDOWS_HEIGHT/3))
        self.draw_text(f'Final Score: {int(self.score)}', 60, 'white', (WINDOWS_WIDTH/2, WINDOWS_HEIGHT/2 - 40))
        retry_rect = self.draw_text('Retry', 50, 'white', (WINDOWS_WIDTH/2, WINDOWS_HEIGHT/2 + 30))
        quit_rect = self.draw_text('Close Game', 50, 'white', (WINDOWS_WIDTH/2, WINDOWS_HEIGHT/2 + 100))
        
        if mouse_clicked:
            if retry_rect.collidepoint(pygame.mouse.get_pos()):
                self.reset_game()
            elif quit_rect.collidepoint(pygame.mouse.get_pos()):
                self.running = False

    def load_images(self):
        self.bullet_surfs = [pygame.image.load(join('image', 'sword', 'sword3.png')).convert_alpha(),
                             pygame.image.load(join('image', 'sword', 'sword4.png')).convert_alpha(),
                             pygame.image.load(join('image', 'sword', 'sword5.png')).convert_alpha(),
                             pygame.image.load(join('image', 'sword', 'sword6.png')).convert_alpha(),
                             pygame.image.load(join('image', 'sword', 'sword7.png')).convert_alpha()]

        folders = list(walk(join('image','enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('image', 'enemies', folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)

    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            bullet_sound = randint(0,1)
            if bullet_sound == 0:
                self.shoot_sound1.play()
            else:
                self.shoot_sound2.play()
            pos = self.sword.rect.center + self.sword.player_direction 
            Bullet(self.bullet_surfs[self.bullet_index], pos, self.sword.player_direction, (self.all_sprites,self.bullet_sprites))
            self.bullet_index = (self.bullet_index + 1) % len(self.bullet_surfs)
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def sword_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.sword_cooldown:
                self.can_shoot = True
    
    def setup(self):
        map = load_pygame(join('data', 'maps', 'world.tmx'))

        for obj in map.get_layer_by_name('Collisions'):
            collisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)),self.collision_sprites)

        for x,y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x*TILE_SIZE,y*TILE_SIZE),image,self.all_sprites)

        for obj in map.get_layer_by_name('Objects'):
            collisionSprite((obj.x, obj.y),obj.image,(self.all_sprites,self.collision_sprites))


        for marker in map.get_layer_by_name('Entities'):
            if marker.name == 'Player':
                self.player = Player((marker.x, marker.y), (self.all_sprites,self.players_sprites), self.collision_sprites)
                self.sword = Sword(self.player, (self.all_sprites, self.sword_sprites))
            else:
                self.spawn_position.append((marker.x, marker.y))

    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                self.collision_sprites_list = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if self.collision_sprites_list:
                    for sprite in self.collision_sprites_list:
                        sprite.destroy()
                        self.score += 50

    def sword_collision(self):
            killed_enemies = pygame.sprite.spritecollide(self.sword, self.enemy_sprites, True, pygame.sprite.collide_mask)
            if killed_enemies:
                self.score += len(killed_enemies) * 50
                varka_sound_persantage = randint(1,10)
                sword_sound_persantage = randint(0,2)
                if sword_sound_persantage == 0:
                    self.impact_sound.play()
                elif sword_sound_persantage ==1:
                    self.slash1.play()
                elif sword_sound_persantage ==2:
                    self.slash2.play()
                else:
                    pass

                if varka_sound_persantage == 1:
                    self.varka_sound.play()

    def player_collision(self):
        if pygame.sprite.spritecollide(self.player,self.enemy_sprites, True, pygame.sprite.collide_mask):
            self.state = 'game_over'

    def run(self):
        while self.running:
            # dt 
            dt = self.clock.tick() / 1000

            mouse_clicked = False

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.fullscreen = not self.fullscreen
                        if self.fullscreen:
                            self.display_surface = pygame.display.set_mode((WINDOWS_WIDTH, WINDOWS_HEIGHT), pygame.FULLSCREEN)
                        else:
                            self.display_surface = pygame.display.set_mode((WINDOWS_WIDTH, WINDOWS_HEIGHT))
                    
                    if event.key == pygame.K_ESCAPE:
                        if self.state == 'playing':
                            self.state = 'paused'
                        elif self.state == 'paused':
                            self.state = 'playing'

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_clicked = True
                    if event.button == 3 and self.state == 'playing':
                        self.bullet_index = (self.bullet_index + 1) % len(self.bullet_surfs)
                        
                if event.type == self.enemy_event and self.state == 'playing':
                    valid_spawns = []
                    player_pos = pygame.Vector2(self.player.rect.center)
                    for pos in self.spawn_position:
                        if player_pos.distance_to(pygame.Vector2(pos)) > 640:
                            valid_spawns.append(pos)
                    
                    if valid_spawns:
                        Enemy(choice(valid_spawns), choice(list(self.enemy_frames.values())),(self.all_sprites,self.enemy_sprites), self.player, self.collision_sprites ,self.impact_sound)

            if self.state == 'playing':
                # update score time
                self.score_timer += dt
                if self.score_timer >= 1:
                    self.score += 100
                    self.score_timer -= 1

                # update
                self.sword_timer()
                self.input()
                self.all_sprites.update(dt)
                self.bullet_collision()
                self.sword_collision()
                self.player_collision()

            # draw game background for all states
            self.display_surface.fill("black")
            self.all_sprites.draw(self.player.rect.center)
            
            # draw score when playing
            if self.state == 'playing':
                score_surf = pygame.font.Font(None, 40).render(f'Score: {int(self.score)}', True, 'white')
                score_rect = score_surf.get_frect(topright=(WINDOWS_WIDTH - 20, 20))
                self.display_surface.blit(score_surf, score_rect)

            if self.state == 'start_menu':
                self.draw_start_menu(mouse_clicked)
            elif self.state == 'paused':
                self.draw_pause_screen(mouse_clicked)
            elif self.state == 'game_over':
                self.draw_game_over_screen(mouse_clicked)

            pygame.display.update()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()