import pygame as pg
from settings import *
from random import randint, uniform
from particles import Particle

class Main():
    def __init__(self) -> None:
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.FULLSCREEN)
        self.clock = pg.time.Clock()
        self.running = True

        # Background
        self.background = pg.image.load('Sprites/Background/Background.png').convert_alpha()
        self.background = pg.transform.scale(self.background, (1920, 1400))

        # Particle
        self.particle_group = pg.sprite.Group()
    
    def run(self) -> None:
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN or event.type == pg.KEYUP:
                    if event.key == pg.K_ESCAPE:
                        self.running = False
        
            self.clock.tick(60)
                    
            self.screen.fill((0, 0, 0))
            Particle(self.particle_group)

            # display
            self.screen.blit(self.background, (0, -300))
            self.particle_group.draw(self.screen)

            # update
            self.particle_group.update()
            pg.display.flip()

        pg.quit()

if __name__ == "__main__":
    main = Main()
    main.run()

