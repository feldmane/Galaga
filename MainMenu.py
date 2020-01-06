import thorpy

from GameScene import GameScene
from Scenes import *

class MainMenu(Scene):

    def __init__(self):
        self.play_button = thorpy.make_button("Play", func=self.play_button_action)
        self.leaderboard_button = thorpy.make_button("Leaderboard")
        self.quit_button = thorpy.make_button("Quit", func=self.quit_button_action)
        all_buttons = [self.play_button, self.leaderboard_button, self.quit_button]
        self.box = thorpy.Box(elements=all_buttons)
        self.menu = thorpy.Menu(self.box)

        for element in self.menu.get_population():
            element.surface = SceneManager.window

        self.box.set_center((SCREENRECT.w / 2, SCREENRECT.h / 2))
        self.box.blit()
        self.box.update()

    def play_button_action(self):
        SceneManager.window.fill((0, 0, 0))
        self.manager.switch_to_scene(GameScene())

    def quit_button_action(self):
        self.manager.Terminate()

    def handle_events(self, events):
        for event in events:
            self.menu.react(event)

    def update(self):
        pass

    def render(self, window):
        pass
