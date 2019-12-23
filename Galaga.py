import os
import pygame as pg
from Spritesheet import spritesheet

FPS = 60
SCALE = 3
INITIAL_WIDTH = 224 * SCALE
INITIAL_HEIGHT = 228 * SCALE
SCREENRECT = pg.Rect(0, 0, INITIAL_WIDTH, INITIAL_HEIGHT)

cwd = os.path.split(os.path.abspath(__file__))[0]

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
        Initializes a bullet.
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

class Alien(pg.sprite.Sprite):

    velocity = 1
    bounce = 1 # 1 for out, -1 for in
    images = []
    elapsed_time = 0 # time in milliseconds since last bounce switch
    animation_time = 1000 # time in milliseconds for animation

    def __init__(self, pos):
        """
        Initializes an alien.
        Args:
            pos: center corner of alien (x, y)
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
        self.elapsed_time += Galaga.clock.get_time()
        if self.elapsed_time > self.animation_time:
            self.index += 1
            if self.index == len(self.images):
                self.kill()
            else:
                self.image = self.images[self.index]
                self.rect = self.image.get_rect(center=self.rect.center)
                self.elapsed_time = 0



class Galaga:

    def __init__(self):
        self.initialize_game()
        self.game_over = False
        self.max_shots = 2

    def load_images(self):
        # open sprite file and initialize sprite sheet loader
        file = os.path.join(cwd, "sprites.png")
        ss = spritesheet(file)

        # load player images
        Player.images = ss.rescale_strip(ss.load_strip(Player.sprite_size, Player.num_sprites, 8), SCALE)

        # load bullet images
        Bullet.images.append(ss.image_at((365, 219, 3, 8)))
        Bullet.images = ss.rescale_strip(Bullet.images, SCALE)

        # load bullet explosion images
        BulletExplosion.images = ss.rescale_strip(ss.images_at(BulletExplosion.sprite_info), SCALE)

        # load blue alien
        BlueAlien.images = ss.rescale_strip(ss.images_at(BlueAlien.sprites_info), SCALE)

    def initialize_game(self):
        #initialize pygame
        pg.init()

        Galaga.clock = pg.time.Clock()

        # initialize game window
        self.window = pg.display.set_mode(SCREENRECT.size)

        # load images
        self.load_images()

        # create groups
        self.all = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.aliens = pg.sprite.Group()

        # create containers
        Player.containers = self.all
        Bullet.containers = self.all, self.bullets
        Alien.containers = self.all, self.aliens
        BulletExplosion.containers = self.all

        # create player
        self.player = Player()

        # create aliens for testing
        BlueAlien((SCREENRECT.w / 2 - 30, SCREENRECT.h / 2))
        BlueAlien((SCREENRECT.w / 2 + 30, SCREENRECT.h / 2))

    def run(self):
        # main game loop
        while not self.game_over:
            # manage time
            dt = self.clock.tick(FPS)

            # handle events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return

            # handle user input
            keystate = pg.key.get_pressed()

            # move player
            direction = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT]
            self.player.move(direction)

            # shoot bullets
            firing = keystate[pg.K_SPACE]
            if firing and not self.player.reloading and len(self.bullets) < self.max_shots:
                Bullet(self.player.get_gun_position())
            self.player.reloading = firing

            # check which direction aliens should be moving in
            Alien.elapsed_time += dt
            if Alien.elapsed_time > Alien.animation_time:
                Alien.elapsed_time = 0
                Alien.change_bounce()

            # check for collisions between bullets and aliens
            for alien in pg.sprite.groupcollide(self.aliens, self.bullets, 1, 1).keys():
                BulletExplosion(alien.get_center())

            # update all game objects
            self.all.update()

            # draw all game objects
            self.all.clear(self.window, pg.Surface(SCREENRECT.size))
            self.all.draw(self.window)
            pg.display.update()

    def quit(self):
        pg.quit()

def main():
    game = Galaga()
    game.run()
    game.quit()

if __name__ == "__main__":
    main()
