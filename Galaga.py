import pygame as pg

from Scenes import SceneManager
from GameScene import GameScene
from MainMenu import MainMenu

def main():
    pg.init()
    game = SceneManager()
    game.switch_to_scene(MainMenu())
    game.run_scene()

if __name__ == "__main__":
    main()
