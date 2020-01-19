import pygame as pg

import Settings

class UIElement:

    def handle_input(self):
        pass

    def update(self):
        pass

    def render(self, window):
        pass

class Text(UIElement):

    def __init__(self, text, center):
        self.x = center[0]
        self.y = center[1]
        self.text = text
        self.color = Settings.WHITE
        self.background = Settings.BLACK
        self.font_style = None
        self.font_size = 22
        self.font = pg.font.Font(self.font_style, self.font_size)
        self.update_surface()

    def render(self, window):
        window.blit(self.surface, self.rect)

    def set_center(self, center):
        self.x = center[0]
        self.y = center[1]
        self.update_surface()

    def set_text(self, text):
        self.text = text
        self.update_surface()

    def set_color(self, color):
        self.color = color
        self.update_surface()

    def set_background(self, background):
        self.background = background
        self.update_surface()

    def set_font_size(self, font_size):
        self.font_size = font_size
        self.font = pg.font.Font(self.font_style, self.font_size)
        self.update_surface()

    def update_surface(self):
        self.surface = self.font.render(self.text, True, self.color, self.background)
        self.rect = self.surface.get_rect(center=(self.x, self.y))


class Button(UIElement):

    def __init__(self, text, center, func=None):
        self.filling = Settings.BLACK
        self.filling_hover = Settings.BLACK
        self.text_color = Settings.WHITE
        self.text_color_hover = self.text_color

        self.text = Text(text, center)
        self.text.set_background(self.filling)

        self.surface = pg.Surface((self.text.rect.w, self.text.rect.h))
        self.rect = self.surface.get_rect()
        self.rect.center = center

        self.func = func
        self.pressed = False

    def set_topleft(self, pos):
        self.rect.topleft = pos
        self.text.set_center(self.rect.center)

    def set_filling(self, color):
        self.filling = color

    def set_filling_hover(self, color):
        self.filling_hover = color

    def set_text_color(self, color):
        self.text_color = color

    def set_text_color_hover(self, color):
        self.text_color_hover = color

    def handle_input(self):
        if self.rect.collidepoint(pg.mouse.get_pos()):
            self.surface.fill(self.filling_hover)
            self.text.set_color(self.text_color_hover)
            self.text.set_background(self.filling_hover)
            if pg.mouse.get_pressed()[0]:
                self.pressed = True
            if not pg.mouse.get_pressed()[0] and self.pressed:
                self.pressed = False
                if self.func != None:
                    self.func()
        else:
            self.surface.fill(self.filling)
            self.text.set_color(self.text_color)
            self.text.set_background(self.filling)

    def render(self, window):
        window.blit(self.surface, self.rect)
        self.text.render(window)
