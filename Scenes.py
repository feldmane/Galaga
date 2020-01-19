import math
import os
import random

import pygame as pg

from Leaderboard import Leaderboard
from GameObjects import *
from Spritesheet import spritesheet
import Settings
from UIElements import *

class SceneManager:

    window = pg.display.set_mode(Settings.SCREENRECT.size)

    def __init__(self):
        self.scene = None

    def switch_to_scene(self, scene):
        pg.Surface.fill(SceneManager.window, pg.Color('black'))
        self.scene = scene
        if self.scene is not None:
            self.scene.manager = self

    def terminate(self):
        self.scene = None

    def run_scene(self):
        while self.scene != None:
            # check to see if user is trying to quit
            if pg.event.get(pg.QUIT):
                self.terminate()
                return

            self.scene.handle_events(pg.event.get())
            if self.scene != None:
                self.scene.update()
                self.scene.render(SceneManager.window)
                pg.display.flip()

            Settings.clock.tick(Settings.FPS)

    def quit(self):
        pg.quit()

class Scene:
    def handle_events(self, events):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def render(self, window):
        raise NotImplementedError

class GameScene(Scene):

    def __init__(self):
        self.max_shots = 2
        self.max_aliens = 20
        self.alien_reload_frames = 30 # min number of frames between alien spawns
        self.alien_odds = 20
        self.max_bombs = 20
        self.bomb_reload_frames = 30
        self.bomb_odds = 20
        self.countdownTime = 3
        self.initialize_game()

    def load_images(self):
        # open sprite file and initialize sprite sheet loader
        file = os.path.join(Settings.cwd, "sprites.png")
        ss = spritesheet(file)

        # load player images
        Player.images = ss.rescale_strip(ss.load_strip(Player.sprite_size, Player.num_sprites, 8), Settings.SCALE)

        # load bullet images
        Bullet.images.clear()
        Bullet.images.append(ss.image_at((365, 219, 3, 8)))
        Bullet.images = ss.rescale_strip(Bullet.images, Settings.SCALE)

        # load bomb images
        Bomb.images.clear()
        Bomb.images.append(ss.image_at((365, 219, 3, 8)))
        Bomb.images = ss.rescale_strip(Bomb.images, Settings.SCALE)

        # load bullet explosion images
        BulletExplosion.images = ss.rescale_strip(ss.images_at(BulletExplosion.sprite_info), Settings.SCALE)

        # Load player explosion images
        PlayerExplosion.images = ss.rescale_strip(ss.images_at(PlayerExplosion.sprite_info), Settings.SCALE)

        # load blue alien
        BlueAlien.images = ss.rescale_strip(ss.images_at(BlueAlien.sprites_info), Settings.SCALE)

    def initialize_game(self):
        self.state = "countdown"
        # load images
        self.load_images()

        # create groups
        self.all = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.bombs = pg.sprite.Group()
        self.aliens = pg.sprite.Group()
        self.player_explosion = pg.sprite.GroupSingle()

        # create containers
        Player.containers = self.all
        Bullet.containers = self.all, self.bullets
        Bomb.containers = self.all, self.bombs
        Alien.containers = self.all, self.aliens
        BulletExplosion.containers = self.all
        PlayerExplosion.containers = self.all, self.player_explosion

        # create player
        self.player = Player()

        # create a score
        self.score = Score()
        self.all.add(self.score)

        # counter to see when alien can spawn
        self.alien_reload = self.alien_reload_frames

        # counter to see when aliens can shoot again
        self.bomb_reload = self.bomb_reload_frames

        # countdown timer
        self.countdownTimer = self.countdownTime

    def handle_events(self, events):
        pass

    def update(self):
        dt = Settings.clock.get_time()

        # check which direction aliens should be moving in
        Alien.elapsed_time += dt
        if Alien.elapsed_time > Alien.animation_time:
            Alien.elapsed_time = 0
            Alien.change_bounce()

        if self.state == "game":
            keystate = pg.key.get_pressed()

            #move player
            direction = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT]
            self.player.move(direction)

            # shoot bullets
            firing = keystate[pg.K_SPACE]
            if firing and not self.player.reloading and len(self.bullets) < self.max_shots:
                Bullet(self.player.get_gun_position())
            self.player.reloading = firing

            # spawn aliens
            if self.alien_reload:
                self.alien_reload -= 1
            elif len(self.aliens) < self.max_aliens and not int(random.random() * self.alien_odds):
                offset = 50
                x = random.randint(offset, Settings.SCREENRECT.w - (2 * offset))
                y = random.randint(offset, Settings.SCREENRECT.h / 2)
                BlueAlien((x, y))
                self.alien_reload = self.alien_reload_frames

            # decide when aliens shoot
            if self.bomb_reload:
                self.bomb_reload -= 1
            elif len(self.bombs) < self.max_bombs and not int(random.random() * self.bomb_odds):
                aliens = self.aliens.sprites()
                if len(aliens) > 0:
                    shooter = random.choice(aliens)
                    Bomb(shooter.get_gun_position())
                self.bomb_reload = self.bomb_reload_frames

            # check for collisions between bullets and aliens
            for alien in pg.sprite.groupcollide(self.aliens, self.bullets, 1, 1).keys():
                self.score.increment_score()
                BulletExplosion(alien.get_center())

            # check for collisions between player and bombs
            for bomb in pg.sprite.spritecollide(self.player, self.bombs, 1):
                self.player.kill()
                PlayerExplosion(self.player.get_center())
                self.leaderboard = Leaderboard()
                self.leaderboard.insert(self.score.get_score(), "ERF")
                self.leaderboard.close()
                self.state = "gameover"

        elif self.state == "countdown":
            self.countdownTimer -= (dt / 1000)
            time = int(math.ceil(self.countdownTimer))
            largeText = pg.font.Font(None, 100)
            textSurf = largeText.render(str(time), True, (255, 255, 255), (0, 0, 0))
            textRect = textSurf.get_rect()
            textRect.center = ((Settings.SCREENRECT.w/2),(Settings.SCREENRECT.h/2))
            if time == 0:
                textSurf = pg.Surface((textRect.w, textRect.h))
                textRect = textSurf.get_rect()
                textRect.center = ((Settings.SCREENRECT.w/2),(Settings.SCREENRECT.h/2))
                self.state = "game"

            SceneManager.window.blit(textSurf, textRect)

        elif self.state == "gameover":
            if (self.player_explosion.sprite == None):
                self.manager.switch_to_scene(MainMenu())

        # update all game objects
        self.all.update()

    def render(self, window):
        self.all.clear(window, pg.Surface(Settings.SCREENRECT.size))
        self.all.draw(window)

class MainMenu(Scene):

    def __init__(self):
        self.UIElements = []
        self.title = Text("Galaga", (Settings.SCREENRECT.w / 2, 70))
        self.title.set_font_size(50)
        self.UIElements.append(self.title)

        offset = 20
        button_text_color_hover = pg.Color('red')
        self.play_button = Button("Play", (Settings.SCREENRECT.w / 2, Settings.SCREENRECT.h / 2), func=self.play_button_action)
        self.play_button.set_text_color_hover(button_text_color_hover)
        self.UIElements.append(self.play_button)

        leaderboard_button_pos = (Settings.SCREENRECT.w / 2, self.play_button.rect.bottom + offset)
        self.leaderboard_button = Button("Leaderboard", leaderboard_button_pos, func=self.leaderboard_button_action)
        self.leaderboard_button.set_text_color_hover(button_text_color_hover)
        self.UIElements.append(self.leaderboard_button)

        quit_button_pos = (Settings.SCREENRECT.w / 2, self.leaderboard_button.rect.bottom + offset)
        self.quit_button = Button("Quit", quit_button_pos, func=self.quit_button_action)
        self.quit_button.set_text_color_hover(button_text_color_hover)
        self.UIElements.append(self.quit_button)

        self.textBox = TextBox((100, 100), 100)
        self.UIElements.append(self.textBox)

    def play_button_action(self):
        self.manager.switch_to_scene(GameScene())

    def leaderboard_button_action(self):
        self.manager.switch_to_scene(LeaderboardScene())

    def quit_button_action(self):
        self.manager.terminate()

    def handle_events(self, events):
        for element in self.UIElements:
            element.handle_events(events)

    def update(self):
        pass

    def render(self, window):
        for element in self.UIElements:
            element.render(window)

class LeaderboardScene(Scene):

    def __init__(self):
        self.leaderboard = Leaderboard()
        self.UIElements = []

        self.back_button = Button("Back", (0, 0), func=self.back_button_action)
        self.back_button.set_text_color_hover(pg.Color('red'))
        self.back_button.set_topleft((5, 5))
        self.UIElements.append(self.back_button)

        self.title = Text("Leaderboard", (Settings.SCREENRECT.w / 2, 70))
        self.title.set_font_size(50)
        self.UIElements.append(self.title)

        scores = self.leaderboard.get_scores()
        i = 0
        initial_height = 200
        offset = 40
        while i < len(scores) and scores[i][0] != -1:
            text = "{} - {}".format(scores[i][1], scores[i][0])
            entry = Text(text, (Settings.SCREENRECT.w / 2, initial_height + (offset * i)))
            entry.set_font_size(36)
            self.UIElements.append(entry)
            i += 1

    def back_button_action(self):
        self.leaderboard.close()
        self.manager.switch_to_scene(MainMenu())

    def handle_events(self, events):
        for element in self.UIElements:
            element.handle_events(events)

    def update(self):
        pass

    def render(self, window):
        for element in self.UIElements:
            element.render(window)
