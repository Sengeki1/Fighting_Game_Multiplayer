import pygame as pg
from support import import_folder

class Player(pg.sprite.Sprite):
    def __init__(self, pos, character) -> None:
        super().__init__()
        self.character = character
        self.posx, self.posy = pos
        self.import_character_assets()
        self.frame_index = 0
        self.animation_speed = 0.19
        self.image = self.animations['Idle'][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.new_rect = pg.Rect(pos[0] - 20, pos[1], 80, 125)

        # player movement
        self.gravity = 0
        self.direction = pg.math.Vector2(0, 0)
        self.ready = True
        self.attack_time = 0
        self.attack_cooldown = 600
        self.q = 0
        self.e = 0

        # Health Bar
        self.hp = 590
        self.hitted = False

        # player status
        self.status = 'Idle'
        self.facing_right = True
        self.lose = False

    def get_damage(self, amount):
        if self.hp <= 0:
            self.hp = 0
            self.lose = True
        elif self.hp > 0:
            self.hp -= amount
            self.lose = False
    
    def get_health(self):
        self.hp = 590

    def import_character_assets(self) -> None:
        character_path = f"Sprites/{self.character}/"
        self.animations = {
            'Attack1': [], 'Attack2': [], 
            'Death': [], 'Fall': [], 'Idle': [], 
            'Jump': [], 'Run': []
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
        if self.lose == False:
            key = pg.key.get_pressed()
            if key[pg.K_SPACE] and self.rect.bottom == 980:
                self.gravity = -20
                self.direction.y = -16

                if not self.ready:
                    self.gravity += 20

            if key[pg.K_d] and self.rect.right < 2000:
                if self.ready:
                    self.rect.x += 7
                    self.new_rect.x += 7
                    self.facing_right = True
                    self.direction.x = 1

                    if key[pg.K_LSHIFT]:
                        self.rect.x += 4
                        self.new_rect.x += 4
                        self.animation_speed = 0.20
                else:
                    self.rect.x += 3
                    self.new_rect.x += 3
                    self.facing_right = True
                    self.direction.x = 1

                
            elif key[pg.K_a] and self.rect.left > -100:
                if self.ready:
                    self.rect.x -= 7 
                    self.new_rect.x -= 7
                    self.facing_right = False
                    self.direction.x = -1

                    if key[pg.K_LSHIFT]:
                        self.rect.x -= 4
                        self.new_rect.x -= 4
                        self.animation_speed = 0.20
                else:
                    self.rect.x -= 3
                    self.new_rect.x -= 3
                    self.facing_right = False
                    self.direction.x = -1
                
            else:
                self.rect.x += 0
                self.new_rect.x += 0
                self.direction.x = 0

            if key[pg.K_q]:
                self.q = 1
                self.attack()
            elif key[pg.K_e]:
                self.e = 1
                self.attack()
    
    def attack(self):
        if self.hitted:
            self.hitted = False
            self.get_damage(15)
        self.ready = False
        self.attack_time = pg.time.get_ticks()
        if self.q == 1:
            self.status = 'Attack1'
            self.q = 0
        elif self.e == 1:
            self.status = 'Attack2'
            self.e = 0

    def apply_gravity(self) -> None:
        self.gravity += 0.8
        self.rect.y += self.gravity 
        self.new_rect.y += self.gravity
        self.direction.y += 0.8
        
        if self.rect.bottom >= 980:
            self.rect.bottom = 980
            self.new_rect.bottom = 980
            self.direction.y = 0
        
    def get_status(self) -> None:
        if not self.ready:
            if self.status != 'Attack1' or self.frame_index >= len(self.animations['Attack1']) - 1:
                if self.status != 'Attack2' or self.frame_index >= len(self.animations['Attack2']) - 1:
                    self.ready = True
                    self.hitted = False

        else:
            if self.lose == False:
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
                self.hitted = False
    
    def get_data(self):
        return {
            'position': (self.posx, self.posy),
            'hp': self.hp,
            'rect': self.rect,
            'status': self.status,
            'facing_right': self.facing_right,
            'ready': self.ready,
            'lose': self.lose,
            'hitted': self.hitted,
            'new_rect': self.new_rect,
            'character': self.character,
            'frame_index': self.frame_index,
            'direction': self.direction,
            'gravity': self.gravity,
        }
    
    def update_data(self, data):
        self.facing_right = data['facing_right']
        self.status = data['status']
        self.rect.x, self.rect.y = data['position']
        self.rect = data['rect']
        self.new_rect = data['new_rect']
        self.hp = data['hp']
        self.ready = data['ready']
        self.lose = data['lose']
        self.hitted = data['hitted']
        self.frame_index = data['frame_index']
        self.character = data['character']
        self.direction = data['direction']
        self.gravity = data['gravity']

    def update(self) -> None:
        self.apply_gravity()
        self.input()
        self.get_status()
        self.animation()
        self.recharge()