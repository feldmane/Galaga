import pygame as pg
from Scenes import *

class Player(pg.sprite.Sprite):

    velocity = 3
    sprite_size = (16, 55, 16, 16) # x, y, x offset, y offset
    num_sprites = 8
    images = []

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[-1]
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        self.rect.bottom = INITIAL_HEIGHT - 30
        self.reloading = 0

    def move(self, direction):
        self.rect.move_ip(direction * self.velocity, 0)
        self.rect = self.rect.clamp(SCREENRECT)

    def get_gun_position(self):
        return self.rect.midtop

class Bullet(pg.sprite.Sprite):

    velocity = -10
    images = []

    def __init__(self, pos):
        """
        Initializes a bullet (from the player).
        Args:
            pos: midbottom of the bullet
        """
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=pos)

    def update(self):
        self.rect.move_ip(0, self.velocity)
        if self.rect.top <= 0:
            self.kill()

class Bomb(pg.sprite.Sprite):

    velocity = 5
    images = []

    def __init__(self, pos):
        """
        Initializes a bomb (from an alien).
        Args:
            pos: midtop of the bomb
        """
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = pg.transform.rotate(self.images[0], 180)
        self.rect = self.image.get_rect(midtop=pos)

    def update(self):
        self.rect.move_ip(0, self.velocity)
        if self.rect.bottom > SCREENRECT.h:
            self.kill()

class Alien(pg.sprite.Sprite):

    velocity = 1
    bounce = 1 # 1 for out, -1 for in
    images = []
    elapsed_time = 0 # time in milliseconds since last bounce switch
    animation_time = 500 # time in milliseconds for animation

    def __init__(self, pos):
        """
        Initializes an alien.
        Args:
            pos: center of alien (x, y)
        """
        pg.sprite.Sprite.__init__(self, self.containers)
        self.initial_pos = pos
        self.image = self.images[-1]
        self.rect = self.image.get_rect(center=pos)
        self.waiting = True

    def _waiting(self):
        if self.bounce > 0:
            self.image = self.images[-1]
        else:
            self.image = self.images[-2]

        dir = self.bounce * self.velocity
        if self.rect.centerx < (SCREENRECT.w / 2):
            self.rect.move_ip(-dir, -dir)
        else:
            self.rect.move_ip(dir, -dir)

    def _dive(self):
        raise NotImplementedError

    def update(self):
        if self.waiting:
            self._waiting()
        else:
            self._dive()

    def get_center(self):
        return self.rect.center

    def get_gun_position(self):
        return self.rect.midbottom

    def change_bounce():
        Alien.bounce = -Alien.bounce

class BlueAlien(Alien):

    sprites_info = [ \
    (19, 177, 10, 13), \
    (42, 178, 12, 11), \
    (65, 176, 13, 14), \
    (90, 177, 13, 13), \
    (113, 176, 14, 13), \
    (139, 177, 11, 12), \
    (162, 178, 13, 10), \
    (188, 178, 9, 10)]

class BulletExplosion(pg.sprite.Sprite):

    sprite_info = [ \
    (211, 202, 7, 8), \
    (234, 200, 12, 13), \
    (256, 199, 16, 16), \
    (283, 193, 27, 28), \
    (321, 191, 31, 32)]
    images = []

    def_animation_time = 50

    def __init__(self, pos):
        """
        Initializes a bullet explosion.
        Args:
            pos: the center of the explosion
        """
        pg.sprite.Sprite.__init__(self, self.containers)
        self.elapsed_time = 0
        self.animation_time = self.def_animation_time
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.elapsed_time += SceneManager.clock.get_time()
        if self.elapsed_time > self.animation_time:
            self.index += 1
            if self.index == len(self.images):
                self.kill()
            else:
                self.image = self.images[self.index]
                self.rect = self.image.get_rect(center=self.rect.center)
                self.elapsed_time = 0

class Score(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.font = pg.font.Font(None, 40)
        self.font.set_italic(1)
        self.color = pg.Color("white")
        self.score = 0
        self.displayed_score = -1
        self.update()
        self.rect = self.image.get_rect().move((10, SCREENRECT.h - 35))

    def update(self):
        if self.displayed_score != self.score:
            self.displayed_score = self.score
            msg = "%d" % self.score
            self.image = self.font.render(msg, 0, self.color)

    def increment_score(self):
        self.score += 1

    def get_score(self):
        return self.score
