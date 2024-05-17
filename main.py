import pygame as pg
from settings import *
from player import Player
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
        self.layer1 = pg.image.load('Sprites/Background/Layer_0000_9.png').convert_alpha()
        self.layer1 = pg.transform.scale(self.layer1, (1920, 1075))
        self.layer2 = pg.image.load('Sprites/Background/Layer_0001_8.png').convert_alpha()
        self.layer2 = pg.transform.scale(self.layer2, (1920, 1065))

        # Particle
        self.particle_group = pg.sprite.Group()

        # Player
        self.player1 = pg.sprite.GroupSingle()
        self.player2 = pg.sprite.GroupSingle()
        self.player1_sprite = Player((300, 834), "Character 1")
        self.player1.add(self.player1_sprite)
        self.player2_sprite = Player((700, 854), "Character 2")
        self.player2.add(self.player2_sprite)

        # Movement
        self.attack_twice_count = 0

    def run(self) -> None:
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN or event.type == pg.KEYUP:
                    if event.key == pg.K_ESCAPE:
                        self.running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_q and self.player1_sprite.rect.bottom == 980:
                        self.player1_sprite.attacking = True
                        self.attack_twice_count += 1
                        if self.attack_twice_count % 2 == 0:
                            self.player1_sprite.attack_twice = True
                        else:
                            self.player1_sprite.attack_twice = False
                        #pg.Rect(self.rect.centerx + 40, self.rect.y + 100, self.rect.width - 350, self.rect.height - 100)

            self.clock.tick(60)
                    
            self.screen.fill((0, 0, 0))
            Particle(self.particle_group)

            # display
            self.screen.blit(self.background, (0, -300))
            self.player1.draw(self.screen)
            self.player2.draw(self.screen)

            self.screen.blit(self.layer2, (0, 0))
            self.screen.blit(self.layer1, (0, 0))
            self.particle_group.draw(self.screen)

            # update
            self.particle_group.update()
            self.player1.update()
            self.player2.update()
            self.player1_sprite.attack1()
            self.player1_sprite.attack2()
            pg.display.flip()

        pg.quit()

if __name__ == "__main__":
    main = Main()
    main.run()

