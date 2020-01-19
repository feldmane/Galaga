import pygame as pg

from Scenes import *

def main():
    pg.init()
    game = SceneManager()
    game.switch_to_scene(MainMenu())
    game.run_scene()
    game.quit()

if __name__ == "__main__":
    main()
