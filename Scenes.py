import os
import random

import pygame as pg
import thorpy

from Leaderboard import Leaderboard
from GameObjects import *
from Spritesheet import spritesheet
import Settings

class SceneManager:

    window = pg.display.set_mode(Settings.SCREENRECT.size)

    def __init__(self):
        self.scene = None

    def switch_to_scene(self, scene):
        self.scene = scene
        if self.scene is not None:
            self.scene.manager = self

    def terminate(self):
        self.scene = None
        pg.quit()

    def run_scene(self):
        while self.scene != None:
            # check to see if user is trying to quit
            if pg.event.get(pg.QUIT):
                self.terminate()
                return

            self.scene.handle_events(pg.event.get())
            self.scene.update()
            self.scene.render(SceneManager.window)

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
        self.initialize_game()

    def load_images(self):
        # open sprite file and initialize sprite sheet loader
        file = os.path.join(Settings.cwd, "sprites.png")
        ss = spritesheet(file)

        # load player images
        Player.images = ss.rescale_strip(ss.load_strip(Player.sprite_size, Player.num_sprites, 8), Settings.SCALE)

        # load bullet images
        Bullet.images.append(ss.image_at((365, 219, 3, 8)))
        Bullet.images = ss.rescale_strip(Bullet.images, Settings.SCALE)

        # load bomb images
        Bomb.images.append(ss.image_at((365, 219, 3, 8)))
        Bomb.images = ss.rescale_strip(Bomb.images, Settings.SCALE)

        # load bullet explosion images
        BulletExplosion.images = ss.rescale_strip(ss.images_at(BulletExplosion.sprite_info), Settings.SCALE)

        # load blue alien
        BlueAlien.images = ss.rescale_strip(ss.images_at(BlueAlien.sprites_info), Settings.SCALE)

    def initialize_game(self):
        # load images
        self.load_images()

        # create groups
        self.all = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.bombs = pg.sprite.Group()
        self.aliens = pg.sprite.Group()

        # create containers
        Player.containers = self.all
        Bullet.containers = self.all, self.bullets
        Bomb.containers = self.all, self.bombs
        Alien.containers = self.all, self.aliens
        BulletExplosion.containers = self.all

        # create player
        self.player = Player()

        # create a score
        self.score = Score()
        self.all.add(self.score)

        # counter to see when alien can spawn
        self.alien_reload = self.alien_reload_frames

        # counter to see when aliens can shoot again
        self.bomb_reload = self.bomb_reload_frames

    def handle_events(self, events):
        pass

    def update(self):
        dt = Settings.clock.get_time()

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

        # check which direction aliens should be moving in
        Alien.elapsed_time += dt
        if Alien.elapsed_time > Alien.animation_time:
            Alien.elapsed_time = 0
            Alien.change_bounce()

        # check for collisions between bullets and aliens
        for alien in pg.sprite.groupcollide(self.aliens, self.bullets, 1, 1).keys():
            self.score.increment_score()
            BulletExplosion(alien.get_center())

        # check for collisions between
        for bomb in pg.sprite.spritecollide(self.player, self.bombs, 1):
            self.manager.switch_to_scene(None)

        # update all game objects
        self.all.update()

    def render(self, window):
        self.all.clear(window, pg.Surface(Settings.SCREENRECT.size))
        self.all.draw(window)
        pg.display.update()

class MainMenu(Scene):

    def __init__(self):
        self.play_button = thorpy.make_button("Play", func=self.play_button_action)
        self.leaderboard_button = thorpy.make_button("Leaderboard", func=self.leaderboard_button_action)
        self.quit_button = thorpy.make_button("Quit", func=self.quit_button_action)
        all_buttons = [self.play_button, self.leaderboard_button, self.quit_button]
        self.box = thorpy.Box(elements=all_buttons)
        self.menu = thorpy.Menu(self.box)

        for element in self.menu.get_population():
            element.surface = SceneManager.window

        self.box.set_center((Settings.SCREENRECT.w / 2, Settings.SCREENRECT.h / 2))
        self.box.blit()
        self.box.update()

    def play_button_action(self):
        SceneManager.window.fill((0, 0, 0))
        self.manager.switch_to_scene(GameScene())

    def leaderboard_button_action(self):
        SceneManager.window.fill((0, 0, 0))
        self.manager.switch_to_scene(LeaderboardScene())

    def quit_button_action(self):
        self.manager.Terminate()

    def handle_events(self, events):
        for event in events:
            self.menu.react(event)

    def update(self):
        pass

    def render(self, window):
        pass

class LeaderboardScene(Scene):

    def __init__(self):
        self.Leaderboard = Leaderboard()
        self.back_button = thorpy.make_button("back", func=self.back_button_action)

        self.box = thorpy.Box(elements=[self.back_button])
        self.menu = thorpy.Menu(self.box)

        for element in self.menu.get_population():
            element.surface = SceneManager.window

        self.box.blit()
        self.box.update()

    def back_button_action(self):
        SceneManager.window.fill((0, 0, 0))
        self.Leaderboard.close()
        self.manager.switch_to_scene(MainMenu())

    def handle_events(self, events):
        for event in events:
            self.menu.react(event)

    def update(self):
        pass

    def render(self, window):
        pass