import pygame as pg
import os

FPS = 60
SCALE = 3
INITIAL_WIDTH = 224 * SCALE
INITIAL_HEIGHT = 228 * SCALE
SCREENRECT = pg.Rect(0, 0, INITIAL_WIDTH, INITIAL_HEIGHT)

cwd = os.path.split(os.path.abspath(__file__))[0]

class SceneManager:

    window = pg.display.set_mode(SCREENRECT.size)
    clock = pg.time.Clock()

    def __init__(self):
        self.scene = None

    def switch_to_scene(self, scene):
        self.scene = scene
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


    def quit(self):
        pg.quit()

class Scene:
    def handle_events(self, events):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def render(self, window):
        raise NotImplementedError
