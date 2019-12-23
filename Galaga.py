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
    sprite_size = (16, 55, 16, 16) #x, y, x offset, y offset
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
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=pos)

    def update(self):
        self.rect.move_ip(0, self.velocity)
        if self.rect.top <= 0:
            self.kill()

class Galaga:

    def __init__(self):
        self.initialize_game()
        self.game_over = False
        self.max_shots = 2

    def load_images(self):
        #load player images
        file = os.path.join(cwd, "sprites.png")
        ss = spritesheet(file)
        Player.images = ss.rescale_strip(ss.load_strip(Player.sprite_size, Player.num_sprites, 8), SCALE)

        #load bullet images
        Bullet.images.append(ss.image_at((365, 219, 3, 8)))
        Bullet.images = ss.rescale_strip(Bullet.images, SCALE)


    def initialize_game(self):
        #initialize pygame
        pg.init()

        self.clock = pg.time.Clock()

        #initialize game window
        self.window = pg.display.set_mode(SCREENRECT.size)

        #load images
        self.load_images()

        #create groups
        self.all = pg.sprite.Group()
        self.bullets = pg.sprite.Group()

        #create containers
        Player.containers = self.all
        Bullet.containers = self.all, self.bullets

        #create player
        self.player = Player()

    def run(self):
        # main game loop
        while not self.game_over:
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

            # update all game objects
            self.all.update()

            # draw all game objects
            self.all.clear(self.window, pg.Surface(SCREENRECT.size))
            self.all.draw(self.window)
            pg.display.update()

            #set FPS
            self.clock.tick(FPS)



def main():
    game = Galaga()
    game.run()

if __name__ == "__main__":
    main()
