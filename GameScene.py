import os
import random

import pygame as pg

from GameObjects import *
from Scenes import *
from Spritesheet import spritesheet

class GameScene(Scene):

    def __init__(self):
        self.max_shots = 2
        self.max_aliens = 20
        self.alien_reload_frames = 30 # min number of frames between alien spawns
        self.alien_odds = 60
        self.max_bombs = 20
        self.bomb_reload_frames = 30
        self.bomb_odds = 20
        self.initialize_game()

    def load_images(self):
        # open sprite file and initialize sprite sheet loader
        file = os.path.join(cwd, "sprites.png")
        ss = spritesheet(file)

        # load player images
        Player.images = ss.rescale_strip(ss.load_strip(Player.sprite_size, Player.num_sprites, 8), SCALE)

        # load bullet images
        Bullet.images.append(ss.image_at((365, 219, 3, 8)))
        Bullet.images = ss.rescale_strip(Bullet.images, SCALE)

        # load bomb images
        Bomb.images.append(ss.image_at((365, 219, 3, 8)))
        Bomb.images = ss.rescale_strip(Bomb.images, SCALE)

        # load bullet explosion images
        BulletExplosion.images = ss.rescale_strip(ss.images_at(BulletExplosion.sprite_info), SCALE)

        # load blue alien
        BlueAlien.images = ss.rescale_strip(ss.images_at(BlueAlien.sprites_info), SCALE)

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
        dt = SceneManager.clock.tick(FPS)

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
            x = random.randint(offset, SCREENRECT.w - (2 * offset))
            y = random.randint(offset, SCREENRECT.h / 2)
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
        self.all.clear(window, pg.Surface(SCREENRECT.size))
        self.all.draw(window)
        pg.display.update()
