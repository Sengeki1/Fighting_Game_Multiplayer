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
        self.ratio = 1
        self.font = pg.font.Font('Font/Pixeltype.ttf', 90)
        self.font2 = pg.font.Font('Font/Pixeltype.ttf', 160)

        # Background
        self.background = pg.image.load('Sprites/Background/Background.png').convert_alpha()
        self.background = pg.transform.scale(self.background, (1920, 1400))
        self.layer1 = pg.image.load('Sprites/Background/Layer_0000_9.png').convert_alpha()
        self.layer1 = pg.transform.scale(self.layer1, (1920, 1075))
        self.layer2 = pg.image.load('Sprites/Background/Layer_0001_8.png').convert_alpha()
        self.layer2 = pg.transform.scale(self.layer2, (1920, 1065))

        # Particle
        self.particle_group = pg.sprite.Group()
        self.hitbox = pg.Rect(0, 0, 0, 0)

        # Player
        self.player1 = pg.sprite.GroupSingle()
        self.player2 = pg.sprite.GroupSingle()
        self.player1_sprite = Player((300, 834), "Character 1")
        self.player1.add(self.player1_sprite)
        self.player2_sprite = Player((700, 854), "Character 2")
        self.player2.add(self.player2_sprite)

    def run(self) -> None:
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN or event.type == pg.KEYUP:
                    if event.key == pg.K_ESCAPE:
                        self.running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_q and self.player1_sprite.ready:
                        self.player1_sprite.attack() # pressed once
                    if event.key == pg.K_e and self.player1_sprite.ready:
                        self.player1_sprite.attack()

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

            # health bar
            ## Player1
            player_1 = self.font.render(f'Player 1', False, (255, 255, 255))
            player_1_rect = player_1.get_rect(center = (230, 45))
            self.screen.blit(player_1, player_1_rect)
            pg.draw.rect(self.screen, "black", (100, 75, 600, 50))
            pg.draw.rect(self.screen, "red", (105, 80, 590, 40))
            pg.draw.rect(self.screen, "green", (105, 80, 590 * self.ratio, 40))

            ## Player 2
            player_2 = self.font.render(f'Player 2', False, (255, 255, 255))
            player_2_rect = player_2.get_rect(center = (1335, 45))
            self.screen.blit(player_2, player_2_rect)
            pg.draw.rect(self.screen, "black", (1200, 75, 600, 50))
            pg.draw.rect(self.screen, "red", (1205, 80, 590, 40))
            pg.draw.rect(self.screen, "green", (1205, 80, 590 * self.ratio, 40))

            player_2 = self.font2.render(f'VS', False, (255, 255, 255))
            player_2_rect = player_2.get_rect(center = (950, 120))
            self.screen.blit(player_2, player_2_rect)

            # update
            self.particle_group.update()
            self.player1.update()
            self.player2.update()

            # if not self.player1_sprite.ready:
            #     pg.draw.rect(self.screen, (0, 255, 0), self.player1_sprite.hitbox)

            pg.display.flip()

        pg.quit()

if __name__ == "__main__":
    main = Main()
    main.run()

