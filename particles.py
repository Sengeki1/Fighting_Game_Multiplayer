import pygame as pg
from random import randint
from settings import *

class Particle(pg.sprite.Sprite):
    def __init__(self, groups) -> None:
        super().__init__(groups)   

        self.pos = (randint(0, 3000), 100)
        self.color = (31, 67, 47)
        self.speed = 5

        self.create_surface()

    def create_surface(self) -> None:
        self.image = pg.Surface((50, 50)).convert_alpha()
        self.image.set_colorkey("black")
        pg.draw.circle(self.image, self.color, center=(25, 25), radius=4, draw_top_left=True)
        self.rect = self.image.get_rect(center=(self.pos))
    
    def check_pos(self) -> None:
        if self.rect.y > SCREEN_HEIGHT:
            self.kill()

    def move(self) -> None:
        self.rect.x += self.speed * -1
        self.rect.y += self.speed

    def update(self) -> None:
        self.move()
        self.check_pos()