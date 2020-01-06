import pygame as pg

import Settings
Settings.init()

from Scenes import *

def main():
    pg.init()
    game = SceneManager()
    game.switch_to_scene(MainMenu())
    game.run_scene()

if __name__ == "__main__":
    main()
