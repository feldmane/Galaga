import pygame as pg

import Settings

class UIElement:

    def handle_events(self, events):
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
        self.color = pg.Color('white')
        self.background = pg.Color('black')
        self.font_style = None
        self.font_size = 22
        self.font = pg.font.Font(self.font_style, self.font_size)
        self.update_surface()

    def set_center(self, center):
        self.x = center[0]
        self.y = center[1]
        self.update_surface()

    def set_midleft(self, midleft):
        self.x = midleft[0] + (self.rect.w / 2)
        self.y = midleft[1]
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

    def render(self, window):
        window.blit(self.surface, self.rect)

class Button(UIElement):

    def __init__(self, rect, text=None, func=None):
        self.color = pg.Color('black')
        self.color_hover = pg.Color('black')

        self.text_color = pg.Color('white')
        self.text_color_hover = self.text_color
        self.font_style = None
        self.font_size = 22
        self.font = pg.font.Font(self.font_style, self.font_size)

        self.rect = pg.Rect(rect)
        self.surface = pg.Surface(self.rect.size)
        self.surface.fill(self.color)

        self.text = text
        self.text_surface = self.font.render(self.text, False, self.text_color, self.color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

        self.func = func
        self.pressed = False

    def set_filling(self, color):
        self.filling = color

    def set_filling_hover(self, color):
        self.filling_hover = color

    def set_text_color(self, color):
        self.text_color = color

    def set_text_color_hover(self, color):
        self.text_color_hover = color

    def is_over(self, pos):
        return self.rect.collidepoint(pos)

    def handle_events(self, events):
        for event in events:
            if event.type == pg.MOUSEMOTION:
                if self.is_over(event.pos):
                    self.surface.fill(self.color_hover)
                    self.text_surface = self.font.render(self.text, False, self.text_color_hover, self.color_hover)
                else:
                    self.surface.fill(self.color)
                    self.text_surface = self.font.render(self.text, False, self.text_color, self.color)

            if event.type == pg.MOUSEBUTTONDOWN:
                if self.is_over(event.pos) and event.button == 1:
                    self.pressed = True

            if event.type == pg.MOUSEBUTTONUP:
                if self.is_over(event.pos) and event.button == 1 and self.pressed:
                    if self.func != None:
                        self.func()
                self.pressed = False

    def render(self, window):
        window.blit(self.surface, self.rect)
        window.blit(self.text_surface, self.text_rect)

class TextBox(UIElement):

    def __init__(self, center, width, func=None, empty_text="TextBox..."):
        self.filling = pg.Color('gray45')
        self.filling_selected = pg.Color('lightgrey')
        self.text_color = pg.Color('white')
        self.text_color_empty = pg.Color('gray94')

        self.text = Text(empty_text, center)
        self.text.set_background(self.filling)

        self.surface = pg.Surface((width, self.text.rect.h))
        self.rect = self.surface.get_rect()
        self.rect.center = center

        self.text.set_midleft(self.rect.midleft)

        self.func = func
        self.selected = False
        self.actual_text = ""
        self.empty_text = empty_text

    def get_text(self):
        return self.actual_text

    def update_text(self, text):
        self.text.set_text(text)
        self.text.set_midleft(self.rect.midleft)

    def is_over(self, pos):
        return self.rect.collidepoint(pos)

    def handle_events(self, events):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                self.selected = self.is_over(event.pos) and event.button == 1

            if event.type == pg.KEYDOWN:
                if self.selected:
                    if event.key == pg.K_RETURN:
                        if self.func != None:
                            self.func()
                    elif event.key == pg.K_BACKSPACE:
                        self.actual_text = self.actual_text[:-1]
                    else:
                        self.actual_text += event.unicode

        if self.actual_text == "":
            self.update_text(self.empty_text)
        else:
            self.update_text(self.actual_text)

        if self.selected:
            self.surface.fill(self.filling_selected)
            self.text.set_background(self.filling_selected)
        else:
            self.surface.fill(self.filling)
            self.text.set_background(self.filling)

    def render(self, window):
        window.blit(self.surface, self.rect)
        self.text.render(window)
