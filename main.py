import pygame as pg
from settings import *
from particles import Particle
from support import *
from player import Player
from settings import *
from databaseConn import DatabaseConn
from network import Network

class Player2(pg.sprite.Sprite):
    def __init__(self, pos, character) -> None:
        super().__init__()
        self.character = character
        self.posx, self.posy = pos
        self.import_character_assets()
        self.frame_index = 0
        self.animation_speed = 0.19
        self.image = self.animations['Idle'][self.frame_index]
        self.rect = self.image.get_rect(center=(pos))
        self.new_rect = pg.Rect(pos[0] - 20, pos[1], 80, 125)
        self.stop = False

        # player movement
        self.gravity = 0
        self.direction = pg.math.Vector2(0, 0)
        self.ready = True

        # Health Bar
        self.hp = 590
        self.hitted = False

        # player status
        self.status = 'Idle'
        self.facing_right = False
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
    
    def get_status(self) -> None:
        if self.ready:
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
    
    def animation(self) -> None:
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

            if self.status == 'Attack1' or self.status == 'Attack2':
                self.status = 'Idle'
                self.ready = True
        
        image = animation[int(self.frame_index)]
        if self.facing_right:
            self.image = image
        else:
            flipped_image = pg.transform.flip(image, True, False)
            self.image = flipped_image

    def update(self) -> None:
        self.get_status()
        self.animation()

class Main():
    def __init__(self) -> None:
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pg.time.Clock()
        self.running = True
        self.game_active = False
        self.scoreA = 0
        self.scoreB = 0
        self.countdown_time = 15
        self.frame_index = 0
        self.data = 0
        self.authenticated = False
        self.message = ""
        self.logged = 0
        self.text1 = ''
        self.text2 = ''
        self.clicked1 = False
        self.clicked2 = False

        # Audio
        music = pg.mixer.Sound('Sound/MysticalForest1.wav')
        music.set_volume(0.1)
        music.play(loops = -1)

        # Network
        self.n = None
        self.player_data = None
        self.databaseServer = DatabaseConn()

        # Hitboxes
        self.hitbox = pg.Rect(0, 0, 0, 0)
        self.player1_hitbox = pg.Rect(0, 0, 0, 0)
        self.player2_hitbox = pg.Rect(0, 0, 0, 0)

        # Font
        self.ratio = 1
        self.normal_font = pg.font.Font('Font/Pixeltype.ttf', 40)
        self.font = pg.font.Font('Font/Pixeltype.ttf', 90)
        self.font2 = pg.font.Font('Font/Pixeltype.ttf', 160)
        self.font3 = pg.font.Font('Font/Pixeltype.ttf', 400)
        self.restart_surf = self.font2.render('Restart', False, (255, 255, 255))
        self.restart_rect = self.restart_surf.get_rect(center = (950, 550))

        # init
        self.init_timer = 100
        self.init_message = True

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
        self.p2 = pg.sprite.GroupSingle()
        self.player1_sprite = None
        self.init_player2_stats = None
        self.player2 = None

    def reset_player_positions(self):
        self.player1_sprite.rect.x = self.player_data['player_data']['position'][0] - 300
        self.player2.rect.x = self.init_player2_stats['position'][0]
        self.player1_sprite.new_rect.x = self.player1_sprite.rect.centerx - 30

    def reset_flags(self):
        self.frame_index = 0
        self.player1_sprite.lose = False
        self.player2.lose = False
        self.player1_sprite.stop = False
        self.player2.stop = False

    def reset_hitted_status(self):
        self.player2.hitted = False
        self.player1_sprite.hitted = False
        self.player2.status = "Idle"
        self.player1_sprite.status = "Idle"
        self.player1_sprite.stop = True
        self.player2.stop = True

    def handle_win_condition(self):
        if self.player2.lose or self.player1_sprite.lose:
            winning_player = "Player 1" if self.player2.lose else "Player 2"
            losing_player_sprite = self.player1_sprite if self.player2.lose else self.player2
            win_message = self.font2.render(f'{winning_player} Wins!', False, (255, 255, 255))
            win_message_rect = win_message.get_rect(center=(950, 550))
            self.screen.blit(win_message, win_message_rect)

            death_animation = import_folder(f'Sprites/{losing_player_sprite.character}/Death', losing_player_sprite.character)
            self.frame_index += 0.18
            if self.frame_index >= len(death_animation):
                self.frame_index = len(death_animation) - 1

            image = death_animation[int(self.frame_index)]
            losing_player_sprite.image = image

            self.data = self.n.send({"timer": True})
            if "start_timer" in self.data:
                timer = self.data["start_timer"]
                if timer <= 0:
                    if self.player2.lose:
                        self.scoreB += 1
                    else:
                        self.scoreA += 1

                    self.init_timer = 100
                    self.reset_player_positions()
                    self.reset_flags()

                else:
                    self.timer_text = self.font.render(f'Time left: {timer / 10}', False, (255, 255, 255))
                    timer_rect = self.timer_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
                    self.screen.blit(self.timer_text, timer_rect)
                    self.reset_hitted_status()
            else:
                # Handle potential error or missing data
                print("Error: Timer data not received.")

    def check_hitbox(self): ### fixed show hitbox
        if not self.player2.ready:
            if self.player2.facing_right:
                self.player2_hitbox = pg.Rect(self.player2.new_rect.centerx + 20, self.player2.new_rect.y - 30, 150, 170)
            else:
                self.player2_hitbox = pg.Rect(self.player2.new_rect.centerx - 170, self.player2.new_rect.y - 30, 150, 170)
            # pg.draw.rect(self.screen, (0, 255, 0), self.player2_hitbox)
        if not self.player1_sprite.ready:
            if self.player1_sprite.facing_right:
                self.player1_hitbox = pg.Rect(self.player1_sprite.new_rect.centerx + 20, self.player1_sprite.new_rect.y - 30, 150, 170)
            else:
                self.player1_hitbox = pg.Rect(self.player1_sprite.new_rect.centerx - 170, self.player1_sprite.new_rect.y - 30, 150, 170)
            # pg.draw.rect(self.screen, (0, 255, 0), self.player1_hitbox)

    def run(self) -> None:
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN or event.type == pg.KEYUP:
                    if event.key == pg.K_ESCAPE:
                        self.running = False
                elif (event.type == pg.MOUSEBUTTONUP):
                    mouse_position = pg.mouse.get_pos()             # Location of the mouse-click
                    if self.click_Rect_1.collidepoint(mouse_position):
                        self.clicked1 = True
                    else:
                        self.clicked1 = False
                    if self.click_Rect_2.collidepoint(mouse_position):
                        self.clicked2 = True
                    else:
                        self.clicked2 = False
                
                if self.clicked1 or self.clicked2:
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_RETURN:
                            package = self.databaseServer.send({"username": self.text1, "password": self.text2})
                            self.text1 = ''
                            self.text2 = ''
                            self.clicked1 = False
                            self.clicked2 = False

                            if "authentication" in package:
                                self.authenticated = package["authentication"]
                                
                        elif event.key == pg.K_BACKSPACE:
                            if self.clicked1:
                                self.text1 = self.text1[:-1]
                            if self.clicked2:
                                self.text2 = self.text2[:-1]
                        else:
                            if len(self.text1) < 18 and self.clicked1:
                                self.text1 += event.unicode
                            if len(self.text2) < 18 and self.clicked2:
                                self.text2 += event.unicode

                if self.game_active == False:
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_RETURN:
                            self.game_active = True
                            self.init_timer = 100

            ####### LOGIN & REGISTER ###############
            if self.authenticated:
                self.screen.fill((0, 0, 0))

                self.databaseServer.send({"stop": True})

                self.n = Network()

                self.player_data = self.n.getP()
                self.message = self.player_data['message']

                self.player1_sprite = Player(
                    (self.player_data['player_data']['position'][0], self.player_data['player_data']['position'][1]),
                    self.player_data['player_data']['character'])
                self.player1.add(self.player1_sprite)

                self.init_player2_stats = self.n.send(self.player1_sprite.get_data())
                self.player2 = Player2((self.init_player2_stats['position'][0], self.init_player2_stats['position'][1]),
                                       self.init_player2_stats['character'])
                self.p2.add(self.player2)

                self.message = self.font.render(f'Press <Enter> to start!', False, (255, 255, 255))
                self.message_rect = self.message.get_rect(center = (960, 300))
                self.screen.blit(self.message, self.message_rect)

                self.keybinds = self.font.render(f'Keybinds:', False, (255, 255, 255))
                self.keybinds_rect = self.keybinds.get_rect(center = (960, 450))
                self.screen.blit(self.keybinds, self.keybinds_rect)

                self.key_tutorial1 = self.font.render(f'Press <Q> to perform Attack 1!', False, (255, 255, 255))
                self.key_tutorial1_rect = self.key_tutorial1.get_rect(center = (960, 550))
                self.screen.blit(self.key_tutorial1, self.key_tutorial1_rect)

                self.key_tutorial2 = self.font.render(f'Press <E> to perform Attack 2!', False, (255, 255, 255))
                self.key_tutorial2_rect = self.key_tutorial2.get_rect(center = (960, 650))
                self.screen.blit(self.key_tutorial2, self.key_tutorial2_rect)

                self.key_tutorial3= self.font.render(f'Press <LSHIFT> to perform a Dash!', False, (255, 255, 255))
                self.key_tutorial3_rect = self.key_tutorial3.get_rect(center = (960, 750))
                self.screen.blit(self.key_tutorial3, self.key_tutorial3_rect)

                self.final_message= self.font.render(f'Enjoy<3', False, (255, 255, 255))
                self.final_message_rect = self.final_message.get_rect(center = (960, 1000))
                self.screen.blit(self.final_message, self.final_message_rect)

                if self.message == "START":
                    self.logged = 1

            if self.authenticated == False:
                self.screen.fill((0, 0, 0))
                pg.draw.rect(self.screen, "white", ((SCREEN_WIDTH / 2) - 200, (SCREEN_HEIGHT / 2) - 300, 400, 600))

                # User
                pg.draw.rect(self.screen, "gray", ((SCREEN_WIDTH / 2) - 150, (SCREEN_HEIGHT / 2) - 100, 300, 50))
                self.click_Rect_1 = pg.draw.rect(self.screen, "white", ((SCREEN_WIDTH / 2) - 145, (SCREEN_HEIGHT / 2) - 95, 290, 40))
                self.username = self.normal_font.render(f'Username', False, (255, 0, 0))
                self.username_rect = self.username.get_rect(topleft=((SCREEN_WIDTH / 2) - 150, (SCREEN_HEIGHT / 2) - 130))
                self.screen.blit(self.username, self.username_rect)

                # Password
                pg.draw.rect(self.screen, "gray", ((SCREEN_WIDTH / 2) - 150, (SCREEN_HEIGHT / 2) + 50, 300, 50))
                self.click_Rect_2 = pg.draw.rect(self.screen, "white", ((SCREEN_WIDTH / 2) - 145, (SCREEN_HEIGHT / 2) + 55, 290, 40))
                self.password = self.normal_font.render(f'Password', False, (255, 0, 0))
                self.password_rect = self.password.get_rect(topleft=((SCREEN_WIDTH / 2) - 150, (SCREEN_HEIGHT / 2) + 20))
                self.screen.blit(self.password, self.password_rect)

                txt_surface = self.normal_font.render(self.text1, True, (0, 255, 0))
                self.screen.blit(txt_surface, self.click_Rect_1)

                txt_surface_2 = self.normal_font.render(self.text2, True, (0, 255, 0))
                self.screen.blit(txt_surface_2, self.click_Rect_2)

            if self.game_active and self.logged == 1:

                self.clock.tick(60)

                self.player2_sprite = self.n.send(self.player1_sprite.get_data())
                
                if "start_timer" not in self.player2_sprite:
                    self.player2.rect.centerx = self.player2_sprite['new_rect'].centerx
                    self.player2.rect.midbottom = self.player2_sprite['new_rect'].midbottom
                    self.player2.new_rect = self.player2_sprite['new_rect']
                    self.player2.status = self.player2_sprite['status']
                    self.player2.ready = self.player2_sprite['ready']
                    self.player2.hp = self.player2_sprite['hp']
                    self.player2.direction.x = self.player2_sprite['direction'][0]
                    self.player2.direction.y = self.player2_sprite['direction'][1]
                    self.player2.facing_right = self.player2_sprite['facing_right']
                    self.player2.gravity = self.player2_sprite['gravity']
                    self.player2.frame_index = self.player2_sprite['frame_index']
                    self.player2.hitted = self.player2_sprite['hitted']
                    self.player2.lose = self.player2_sprite['lose']

                self.screen.fill((0, 0, 0))
                Particle(self.particle_group)

                # display
                self.screen.blit(self.background, (0, -300))
                self.player1.draw(self.screen)
                self.p2.draw(self.screen)

                self.screen.blit(self.layer2, (0, 0))
                self.screen.blit(self.layer1, (0, 0))
                self.particle_group.draw(self.screen)

                # update
                self.particle_group.update()
                self.player1.update()
                self.p2.update()

                # Health #### Fixed 
                ## Player1
                player_1 = self.font.render(f'Player 1', False, (255, 255, 255))
                player_1_rect = player_1.get_rect(center = (230, 45))
                self.screen.blit(player_1, player_1_rect)
                pg.draw.rect(self.screen, "black", (100, 75, 600, 50))
                pg.draw.rect(self.screen, "red", (105, 80, 590, 40))
                pg.draw.rect(self.screen, "green", (105, 80, self.player2.hp, 40))
        
                ## Player 2
                player_2 = self.font.render(f'Player 2', False, (255, 255, 255))
                player_2_rect = player_2.get_rect(center = (1335, 45))
                self.screen.blit(player_2, player_2_rect)
                pg.draw.rect(self.screen, "black", (1200, 75, 600, 50))
                pg.draw.rect(self.screen, "red", (1205, 80, 590, 40))
                pg.draw.rect(self.screen, "green", (1205, 80, self.player1_sprite.hp, 40))

                vs = self.font2.render(f'VS', False, (255, 255, 255))
                vs_rect = vs.get_rect(center = (950, 120))
                self.screen.blit(vs, vs_rect)

                # Hitboxes ### Fixed
                # pg.draw.rect(self.screen, (255, 0, 0), self.player1_sprite.new_rect)
                # pg.draw.rect(self.screen, (255, 0, 0), self.player2.new_rect)
                self.check_hitbox()

                # Collision ### Fixed
                if self.player1_hitbox.colliderect(self.player2.new_rect) and self.player1_sprite.ready:
                    self.player1_sprite.hitted = True
                elif self.player2_hitbox.colliderect(self.player1_sprite.new_rect) and self.player2.ready:
                    self.player2.hitted = True

                # Score ### Fixed
                if self.scoreA < 3 and self.scoreA > 0:
                    if self.scoreA == 1:
                        pg.draw.rect(self.screen, (255, 255, 0), (130, 130, 25, 25), 0, 25)
                    else:
                        if self.scoreA == 2:
                            pg.draw.rect(self.screen, (255, 255, 0), (130, 130, 25, 25), 0, 25)
                            pg.draw.rect(self.screen, (255, 255, 0), (180, 130, 25, 25), 0, 25)
                if self.scoreB < 3 and self.scoreB > 0:
                    if self.scoreB == 1:
                        pg.draw.rect(self.screen, (255, 255, 0), (1220, 130, 25, 25), 0, 25)
                    else:
                        if self.scoreB == 2:
                            pg.draw.rect(self.screen, (255, 255, 0), (1220, 130, 25, 25), 0, 25)
                            pg.draw.rect(self.screen, (255, 255, 0), (1270, 130, 25, 25), 0, 25)
                
                self.handle_win_condition()

                if self.scoreA == 3 or self.scoreB == 3:  
                    self.player1_sprite.rect.x = self.player_data['player_data']['position'][0] - 300
                    self.player2.rect.x = self.init_player2_stats['position'][0]
                    self.player1_sprite.new_rect.x = self.player1_sprite.rect.centerx - 40

                    self.player1_sprite.get_health()
                    self.player2.get_health()
                    
                    self.player1_sprite.lose = False
                    self.player2.lose = False
                    self.init_timer = 100
                    self.frame_index = 0

                    self.scoreA = 0
                    self.scoreB = 0

                    self.game_active = False

                if self.init_timer > 0:
                    self.init_timer -= 1

                    message = self.font3.render(f'FIGHT', False, (255, 255, 255))
                    message_rect = message.get_rect(center = (950, 590))
                    self.screen.blit(message, message_rect)

                    self.player1_sprite.get_health()
                    self.player2.get_health()

                else:
                    self.screen.fill((0, 0, 0))
                    self.screen.blit(self.restart_surf, self.restart_rect)

                    self.player1_sprite.get_health()
                    self.player2.get_health()

            pg.display.update()

        pg.quit()


if __name__ == "__main__":
    main = Main()
    main.run()

