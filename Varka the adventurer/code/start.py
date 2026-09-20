from settings import *

class Game:
    def __init__(self):
        pygame.display_surface = pygame.display.set_mode((WINDOWS_WIDTH, WINDOWS_HEIGHT))
        pygame.display.set_caption('Kill Or Be Killed')
        icon_image = pygame.image.load("image/icone/icon.ico")
        pygame.display.set_icon(icon_image) 
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            # dt 
            dt = self.clock.tick()/1000

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False


            # update



            # draw
            pygame.display.update()


        pygame.quit()