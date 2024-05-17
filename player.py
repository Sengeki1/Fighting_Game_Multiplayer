import pygame as pg
from support import import_folder

class Player(pg.sprite.Sprite):
    def __init__(self, pos, character) -> None:
        super().__init__()
        self.character = character
        self.import_character_assets()
        self.frame_index = 0
        self.animation_speed = 0.05
        self.image = self.animations['Idle'][self.frame_index] 
        self.rect = self.image.get_rect(center = pos)

        # player movement
        self.gravity = 0
        self.direction = pg.math.Vector2(0, 0)
        self.attacking = False
        self.attack_twice = False
        self.finishAttack = False

        # player status
        self.status = 'idle'
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
            if key[pg.K_RIGHT]:
                self.rect.x += 7
                self.facing_right = True
                self.direction.x = 1

                if self.attacking:
                    self.rect.x -= 7
                
            elif key[pg.K_LEFT]:
                self.rect.x -= 7 
                self.facing_right = False
                self.direction.x = -1

                if self.attacking:
                    self.rect.x += 7

            else:
                self.rect.x += 0
                self.direction.x = 0
                
            if key[pg.K_SPACE] and self.rect.bottom == 980:
                self.gravity = -20
                self.direction.y = -16
    
    def attack1(self):
        if self.attacking:
            animation = self.animations['Attack1']
            
            self.frame_index += self.animation_speed
            if self.frame_index >= len(animation):
                self.frame_index = 0
                self.attacking = False
                self.finishAttack = True
            
            image = animation[int(self.frame_index)]
            if self.facing_right:
                self.image = image
            else:
                flipped_image = pg.transform.flip(image, True, False)
                self.image = flipped_image

    def attack2(self):
        if self.attacking:
            if self.attack_twice and self.finishAttack:
                animation = self.animations['Attack2']
                
                self.frame_index += self.animation_speed
                if self.frame_index >= len(animation):
                    self.frame_index = 0
                    self.attacking = False
                    self.attack_twice = False
                    self.finishAttack = False

                image = animation[int(self.frame_index)]
                if self.facing_right:
                    self.image = image
                else:
                    flipped_image = pg.transform.flip(image, True, False)
                    self.image = flipped_image

    def apply_gravity(self) -> None:
        self.gravity += 0.8
        self.rect.y += self.gravity 
        self.direction.y += 0.8
        
        if self.rect.bottom >= 980:
            self.rect.bottom = 980
            self.direction.y = 0
        
    def get_status(self) -> None:
        if self.direction.y < 0:
            self.status = "Jump"
        elif self.direction.y > 0:
            self.status = "Fall"
        else:
            if self.direction.x != 0:
                self.status = "Run"
            else:
                self.status = "Idle"

    def update(self) -> None:
        self.apply_gravity()
        self.input()
        self.get_status()
        self.animation()