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

    def set_midleft(self, midleft):
        self.x = midleft[0] + (self.rect.w / 2)
        self.y = midleft[1]

    def set_text(self, text):
        self.text = text

    def set_color(self, color):
        self.color = color

    def set_background(self, background):
        self.background = background

    def set_font_size(self, font_size):
        self.font_size = font_size
        self.font = pg.font.Font(self.font_style, self.font_size)

    def update_surface(self):
        self.surface = self.font.render(self.text, True, self.color, self.background)
        self.rect = self.surface.get_rect(center=(self.x, self.y))

    def update(self):
        self.update_surface()

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
        self.over = False

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
                self.over = self.is_over(event.pos)

            if event.type == pg.MOUSEBUTTONDOWN:
                if self.is_over(event.pos) and event.button == 1:
                    self.pressed = True

            if event.type == pg.MOUSEBUTTONUP:
                if self.is_over(event.pos) and event.button == 1 and self.pressed:
                    if self.func != None:
                        self.func()
                self.pressed = False

    def render(self, window):
        if self.over:
            self.surface.fill(self.color_hover)
            self.text_surface = self.font.render(self.text, False, self.text_color_hover)
        else:
            self.surface.fill(self.color)
            self.text_surface = self.font.render(self.text, False, self.text_color)
        window.blit(self.surface, self.rect)
        window.blit(self.text_surface, self.text_rect)

class TextBox(UIElement):

    def __init__(self, rect, func=None, empty_text="TextBox..."):
        self.color = pg.Color('red')
        self.color_selected = pg.Color('blue')
        self.outline_color = pg.Color('white')
        self.outline_color_selected = pg.Color('white')
        self.outline_width = 2
        self.text_color = pg.Color('white')
        self.text_color_empty = pg.Color('gray94')

        self.font_style = None
        self.font_size = 22
        self.font = pg.font.Font(self.font_style, self.font_size)

        self.rect = pg.Rect(rect)
        self.surface = pg.Surface(self.rect.size)

        self.func = func
        self.selected = False
        self.actual_text = ""
        self.empty_text = empty_text
        self.displayed_text = None

        self.text_surface = self.font.render(self.empty_text, False, self.text_color_empty)
        self.text_rect = self.text_surface.get_rect(x=self.rect.x + 2, centery=self.rect.centery)
        self.text_area = None

        self.blink = True
        self.blink_speed = 530
        self.recent_blink = 0

    def get_text(self):
        return self.actual_text

    def is_over(self, pos):
        return self.rect.collidepoint(pos)

    def handle_blink(self):
        if (pg.time.get_ticks() - self.recent_blink > self.blink_speed):
            self.blink = not self.blink
            self.recent_blink = pg.time.get_ticks()

    def handle_events(self, events):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                self.selected = self.is_over(event.pos) and event.button == 1

            if event.type == pg.KEYDOWN and self.selected:
                if event.key == pg.K_RETURN:
                    if self.func != None:
                        self.func()
                elif event.key == pg.K_BACKSPACE:
                    self.actual_text = self.actual_text[:-1]
                else:
                    self.actual_text += event.unicode

    def update(self):
        text = None
        if len(self.actual_text) != 0 or self.selected:
            text = self.actual_text
        else:
            text = self.empty_text

        if text != self.displayed_text:
            self.displayed_text = text
            self.text_surface = self.font.render(text, False, self.text_color)
            self.text_rect = self.text_surface.get_rect(x=self.rect.x + 2, centery=self.rect.centery)
            offset = self.outline_width + 4
            if self.text_rect.w > self.rect.w - offset:
                start = self.text_rect.w - (self.rect.w - offset)
                self.text_area = pg.Rect(start, 0, self.rect.w - offset, self.text_rect.h)
            else:
                self.text_area = self.text_surface.get_rect()

        self.handle_blink()

    def render(self, window):
        outline = self.rect.inflate(self.outline_width*2, self.outline_width*2)
        if self.selected:
            window.fill(self.outline_color_selected, rect=outline)
            self.surface.fill(self.color_selected)
        else:
            window.fill(self.outline_color, rect=outline)
            self.surface.fill(self.color)

        window.blit(self.surface, self.rect)
        window.blit(self.text_surface, self.text_rect, self.text_area)
        if self.blink and self.selected:
            curse = self.text_area.copy()
            curse.topleft = self.text_rect.topleft
            window.fill(self.text_color, (curse.right+1, curse.y, 2, curse.h))
