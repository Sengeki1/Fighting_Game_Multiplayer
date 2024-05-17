import pygame as pg
from support import import_folder

class Player(pg.sprite.Sprite):
    def __init__(self, pos, character) -> None:
        super().__init__()
        self.character = character
        self.import_character_assets()
        self.frame_index = 0
        self.animation_speed = 0.19
        self.image = self.animations['Idle'][self.frame_index] 
        self.rect = self.image.get_rect(center = pos)

        # player movement
        self.gravity = 0
        self.direction = pg.math.Vector2(0, 0)
        self.ready = True
        self.attack_time = 0
        self.attack_cooldown = 600
        self.q = 0
        self.e = 0

        # player status
        self.status = 'Idle'
        self.facing_right = True

    def import_character_assets(self) -> None:
        character_path = f"Sprites/{self.character}/"
        self.animations = {
            'Attack1': [], 'Attack2': [], 
            'Death': [], 'Fall': [], 'Idle': [], 
            'Jump': [], 'Run': [], 'Take Hit': []
        }

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path, self.character)
    
    def animation(self) -> None:
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
        
        image = animation[int(self.frame_index)]
        if self.facing_right:
            self.image = image
        else:
            flipped_image = pg.transform.flip(image, True, False)
            self.image = flipped_image

    def input(self) -> None:
        key = pg.key.get_pressed()
        if self.character == "Character 1":
            if key[pg.K_SPACE] and self.rect.bottom == 980:
                self.gravity = -20
                self.direction.y = -16

                if not self.ready:
                    self.gravity += 20

            if key[pg.K_RIGHT]:
                if self.ready:
                    self.rect.x += 7
                    self.facing_right = True
                    self.direction.x = 1
                else:
                    self.rect.x += 3
                    self.facing_right = True
                    self.direction.x = 1

                
            elif key[pg.K_LEFT]:
                if self.ready:
                    self.rect.x -= 7 
                    self.facing_right = False
                    self.direction.x = -1
                else:
                    self.rect.x -= 3
                    self.facing_right = False
                    self.direction.x = -1
                
            else:
                self.rect.x += 0
                self.direction.x = 0

            if key[pg.K_q]:
                self.q = 1
                self.attack()
            elif key[pg.K_e]:
                self.e = 1
                self.attack()
    
    def attack(self):
        self.ready = False
        self.attack_time = pg.time.get_ticks()
        if self.q == 1:
            self.status = 'Attack1'
            self.q = 0
        elif self.e == 1:
            self.status = 'Attack2'
            self.e = 0
        
        if self.facing_right:
            self.hitbox = pg.Rect(self.rect.centerx + 40, self.rect.y + 130, self.rect.width - 350, self.rect.height - 130)
        else:
            self.hitbox = pg.Rect(self.rect.centerx - 200, self.rect.y + 130, self.rect.width - 350, self.rect.height - 130)

    def apply_gravity(self) -> None:
        self.gravity += 0.8
        self.rect.y += self.gravity 
        self.direction.y += 0.8
        
        if self.rect.bottom >= 980:
            self.rect.bottom = 980
            self.direction.y = 0
        
    def get_status(self) -> None:
        if not self.ready:
            if self.status != 'Attack1' or self.frame_index >= len(self.animations['Attack1']) - 1:
                if self.status != 'Attack2' or self.frame_index >= len(self.animations['Attack1']) - 1:
                    self.ready = True

        if self.ready == False:
            if self.q == 1:
                self.status = 'Attack1'
                self.q = 0
            elif self.e == 1:
                self.status = 'Attack2'
                self.e = 0
        else:
            if self.direction.y < 0:
                self.status = "Jump"
            elif self.direction.y > 0:
                self.status = "Fall"
            else:
                if self.direction.x != 0:
                    self.status = "Run"
                else:
                    self.status = "Idle"

    def recharge(self):
        if self.ready == False:
            current_time = pg.time.get_ticks()
            if current_time - self.attack_time >= self.attack_cooldown:
                self.ready = True

    def update(self) -> None:
        self.apply_gravity()
        self.input()
        self.get_status()
        self.animation()
        self.recharge()