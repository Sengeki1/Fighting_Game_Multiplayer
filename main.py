import pygame as pg
from settings import *
from particles import Particle
from support import *
from player import Player
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

    # def get_health(self):
    #     self.hp = 590

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
    
    # def apply_gravity(self) -> None:
    #     self.gravity += 0.8
    #     self.rect.y += self.gravity 
    #     self.new_rect.y += self.gravity
    #     self.direction.y += 0.8
        
    #     if self.rect.bottom >= 980:
    #         self.rect.bottom = 980
    #         self.new_rect.bottom = 980
    #         self.direction.y = 0

    # def get_status(self) -> None:
    #     if not self.ready:
    #         if self.status != 'Attack1' or self.frame_index >= len(self.animations['Attack1']) - 1:
    #             if self.status != 'Attack2' or self.frame_index >= len(self.animations['Attack2']) - 1:
    #                 self.ready = True
    #                 self.hitted = False

    #     else:
    #         if self.stop == False:
    #             if self.direction.y < 0:
    #                 self.status = "Jump"
    #             elif self.direction.y > 0:
    #                 self.status = "Fall"
    #             else:
    #                 if self.direction.x != 0:
    #                     self.status = "Run"
    #                 else:
    #                     self.status = "Idle"

    def update(self) -> None:
        # self.apply_gravity()
        # self.get_status()
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

        # Network
        self.n = Network()
        self.player_data = self.n.getP()
        self.message = self.player_data['message']

        # Hitboxes
        self.hitbox = pg.Rect(0, 0, 0, 0)
        self.player1_hitbox = pg.Rect(0, 0, 0, 0)
        self.player2_hitbox = pg.Rect(0, 0, 0, 0)

        # Font
        self.ratio = 1
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
        self.player1_sprite = Player((self.player_data['player_data']['position'][0], self.player_data['player_data']['position'][1]), self.player_data['player_data']['character'])
        self.player1.add(self.player1_sprite)
        
        self.init_player2_stats = self.n.send(self.player1_sprite.get_data())
        self.player2 = Player2((self.init_player2_stats['position'][0], self.init_player2_stats['position'][1]), self.init_player2_stats['character'])
        self.p2.add(self.player2)

    def check_hitbox(self): ### fixed show hitbox
        if not self.player2_sprite['ready']:
            if self.player2_sprite['facing_right']:
                self.player2_hitbox = pg.Rect(self.player2_sprite['new_rect'].centerx + 20, self.player2_sprite['new_rect'].y - 30, 150, 170)
            else:
                self.player2_hitbox = pg.Rect(self.player2_sprite['new_rect'].centerx - 170, self.player2_sprite['new_rect'].y - 30, 150, 170)
            pg.draw.rect(self.screen, (0, 255, 0), self.player2_hitbox)
        if not self.player1_sprite.ready:
            if self.player1_sprite.facing_right:
                self.player1_hitbox = pg.Rect(self.player1_sprite.new_rect.centerx + 20, self.player1_sprite.new_rect.y - 30, 150, 170)
            else:
                self.player1_hitbox = pg.Rect(self.player1_sprite.new_rect.centerx - 170, self.player1_sprite.new_rect.y - 30, 150, 170)
            pg.draw.rect(self.screen, (0, 255, 0), self.player1_hitbox)

    def run(self) -> None:
        if self.message == "START":
            global start_ticks
            start_ticks = pg.time.get_ticks() # Get the current time in milliseconds
            while self.running:

                self.current_ticks = pg.time.get_ticks()
                self.clock.tick(60)

                self.player2_sprite = self.n.send(self.player1_sprite.get_data())

                self.player2.rect.centerx = self.player2_sprite['new_rect'].centerx
                self.player2.rect.midbottom = self.player2_sprite['new_rect'].midbottom
                self.player2.status = self.player2_sprite['status']
                self.player2.ready = self.player2_sprite['ready']
                self.player2.stop = self.player2_sprite['stop']
                self.player2.direction.x = self.player2_sprite['direction'][0]
                self.player2.direction.y = self.player2_sprite['direction'][1]
                self.player2.facing_right = self.player2_sprite['facing_right']
                self.player2.gravity = self.player2_sprite['gravity']

                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.running = False
                    elif event.type == pg.KEYDOWN or event.type == pg.KEYUP:
                        if event.key == pg.K_ESCAPE:
                            self.running = False

                    if self.game_active == False:
                        if event.type == pg.KEYDOWN:
                            if event.key == pg.K_RETURN:
                                self.game_active = True
                                self.init_timer = 100
                                self.init_message = False

                if self.game_active:

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
                    pg.draw.rect(self.screen, "green", (105, 80, self.player2_sprite['hp'], 40))
            
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
                    #pg.draw.rect(self.screen, (255, 0, 0), self.player1_sprite.new_rect)
                    #pg.draw.rect(self.screen, (255, 0, 0), self.player2_sprite['new_rect'])
                    self.check_hitbox()

                    # Collision ### Fixed
                    if self.player1_hitbox.colliderect(self.player2_sprite['new_rect']) and self.player1_sprite.ready:
                        self.player1_sprite.hitted = True
                    elif self.player2_hitbox.colliderect(self.player1_sprite.new_rect) and self.player2_sprite['ready']:
                        self.player2_sprite['hitted'] = True

                    # Score ### Fixed
                    if self.scoreA < 3 and self.scoreA > 0:
                        ### SCORE MUST BE A LIST OF 3 ELEMENT TRUE OR FALSE AND SET IT INSIDE THE LOSE LOGIC WHEN A PLAYER WINS
                        if self.scoreA == 1:
                            pg.draw.rect(self.screen, (255, 255, 0), (130, 130, 25, 25), 0, 25)
                        elif self.scoreA == 2:
                            pg.draw.rect(self.screen, (255, 255, 0), (130, 130, 25, 25), 0, 25)
                            pg.draw.rect(self.screen, (255, 255, 0), (180, 130, 25, 25), 0, 25)
                    if self.scoreB < 3 and self.scoreB > 0:
                        if self.scoreB == 1:
                            pg.draw.rect(self.screen, (255, 255, 0), (1220, 130, 25, 25), 0, 25)
                        elif self.scoreB == 2:
                            pg.draw.rect(self.screen, (255, 255, 0), (1220, 130, 25, 25), 0, 25)
                            pg.draw.rect(self.screen, (255, 255, 0), (1270, 130, 25, 25), 0, 25)
                    
                    # Win ### Fixed ish ( FIX TIMER)
                    if self.player2_sprite['lose']:
                        win_message = self.font2.render(f'Player 2 Wins!', False, (255, 255, 255))
                        win_message_rect = win_message.get_rect(center = (950, 550))
                        self.screen.blit(win_message, win_message_rect)

                        death_animation = import_folder(f'Sprites/{self.player1_sprite.character}/Death', self.player1_sprite.character)
                        self.frame_index += 0.18
                        if self.frame_index >= len(death_animation):
                            self.frame_index = len(death_animation) - 1

                        image = death_animation[int(self.frame_index)]
                        self.player1_sprite.image = image

                        # Calculate the elapsed time
                        milliseconds_passed = pg.time.get_ticks() - start_ticks
                        seconds_passed = milliseconds_passed // 1000
                        time_left = self.countdown_time - seconds_passed

                        # Render the countdown timer
                        timer_text = self.font.render(f'Time left: {time_left}', False, (255, 255, 255))
                        timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
                        self.screen.blit(timer_text, timer_rect)
                        
                        if time_left > 1:
                            self.player2_sprite['hitted'] = False
                            self.player1_sprite.hitted = False
                            self.player1_sprite.stop = True
                            self.player2_sprite['stop'] = True
                            self.player2_sprite['status'] = "Idle"
                        else:
                            self.scoreA += 1
                            self.player2_sprite['stop'] = False
                            self.player1_sprite.stop = False
                            self.player2_sprite['lose'] = False
                            self.player1_sprite.lose = False
                            self.player1_sprite.rect.x = self.player_data['player_data']['position'][0] - 300
                            self.player2_sprite['rect'].x = self.init_player2_stats['position'][0]
                            self.init_timer = 100
                            self.player1_sprite.new_rect.x = self.player1_sprite.rect.centerx - 30
                            self.frame_index = 0

                            reset_timer()

                    elif self.player1_sprite.lose:
                        win_message = self.font2.render(f'Player 1 Wins!', False, (255, 255, 255))
                        win_message_rect = win_message.get_rect(center = (950, 550))
                        self.screen.blit(win_message, win_message_rect)

                        death_animation = import_folder(f'Sprites/{self.player2_sprite.character}/Death', self.player1_sprite.character)
                        self.frame_index += 0.18
                        if self.frame_index >= len(death_animation):
                            self.frame_index = len(death_animation) - 1

                        image = death_animation[int(self.frame_index)]
                        self.player1_sprite.image = image
                        
                        # Calculate the elapsed time
                        milliseconds_passed = pg.time.get_ticks() - start_ticks
                        seconds_passed = milliseconds_passed // 1000
                        time_left = self.countdown_time - seconds_passed

                        # Render the countdown timer
                        timer_text = self.font.render(f'Time left: {time_left}', False, (255, 255, 255))
                        timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
                        self.screen.blit(timer_text, timer_rect)

                        if time_left > 1:
                            self.player2_sprite['hitted']= False
                            self.player1_sprite.hitted = False
                            self.player2_sprite['stop'] = True
                            self.player1_sprite.stop = True
                            self.player1_sprite.status = "Idle"
                        else:
                            self.scoreB += 1
                            self.player2_sprite['stop'] = False
                            self.player1_sprite.stop = False
                            self.player2_sprite['lose'] = False
                            self.player1_sprite.lose = False
                            self.player1_sprite.rect.x = self.player_data['player_data']['position'][0] - 300
                            self.player2_sprite['rect'].x = self.init_player2_stats['position'][0] + 405
                            self.init_timer = 100
                            self.player1_sprite.new_rect.x = self.player1_sprite.rect.centerx - 40
                            self.frame_index = 0

                            reset_timer()

                    if self.scoreA == 3 or self.scoreB == 3:  
                        # self.scoreA = 0
                        # self.scoreB = 0
                        # self.player1_sprite.rect.x = self.player_data['player_data']['position'][0] - 300
                        # self.player2_sprite['rect'].x = self.init_player2_stats['position'][0]
                        # self.player1_sprite.new_rect.x = self.player1_sprite.rect.centerx - 40

                        # self.player1_sprite.get_health()
                        # self.player2_sprite['hp'] = 590
                        
                        # ### test
                        # self.player1_sprite.lose = False
                        # self.player2_sprite['lose'] = False
                        # self.player1_sprite.secs = 500
                        # self.init_timer = 100
                        # self.player1_sprite.stop = False
                        # self.player2_sprite['stop'] = False
                        # self.frame_index = 0
                        # ###

                        self.game_active = False

                    if self.init_timer >= 0:
                        self.init_timer -= 1

                        message = self.font3.render(f'FIGHT', False, (255, 255, 255))
                        message_rect = message.get_rect(center = (950, 590))
                        self.screen.blit(message, message_rect)

                        self.player1_sprite.get_health()
                        self.player2_sprite['hp'] = 590
                    
                else:
                    if self.init_message:
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

                    else:
                        # self.screen.fill((0, 0, 0))
                        # self.screen.blit(self.restart_surf, self.restart_rect)

                        # self.player1_sprite.get_health()
                        # self.player2_sprite['hp'] = 590
                        self.running = False

                pg.display.update()

            pg.quit()

def reset_timer():
    global start_ticks
    start_ticks = pg.time.get_ticks()

if __name__ == "__main__":
    main = Main()
    main.run()

