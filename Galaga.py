import os
import pygame as pg
from Spritesheet import spritesheet

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
        pg.sprite.Sprite.__init__(self)
        self.image = Player.images[-1]
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        print(self.rect.w)
        self.rect.bottom = INITIAL_HEIGHT - 30


    def move(self, direction):
        self.rect.move_ip(direction * self.velocity, 0)
        self.rect = self.rect.clamp(SCREENRECT)


class Galaga:

    def __init__(self):
        self.initialize_game()
        self.game_over = False

    def initialize_game(self):
        #initialize pygame
        pg.init()

        self.clock = pg.time.Clock()

        #initialize game window
        self.window = pg.display.set_mode(SCREENRECT.size)

        #load player images
        file = os.path.join(cwd, "sprites.png")
        ss = spritesheet(file)
        Player.images = ss.rescale_strip(ss.load_strip(Player.sprite_size, Player.num_sprites, 8), SCALE)

        #create groups
        self.all = pg.sprite.Group()

        #create player
        self.player = Player()
        self.all.add(self.player)

    def run(self):
        # main game loop
        while not self.game_over:
            #handle events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return

            #handle user input
            keystate = pg.key.get_pressed()

            direction = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT]
            self.player.move(direction)

            #draw all game objects
            self.all.clear(self.window, pg.Surface(SCREENRECT.size))
            self.all.draw(self.window)
            pg.display.update()



def main():
    game = Galaga()
    game.run()

if __name__ == "__main__":
    main()
