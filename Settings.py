import pygame as pg
import os

def init():
    global FPS
    FPS = 60

    global SCALE
    SCALE = 3

    global INITIAL_WIDTH
    INITIAL_WIDTH = 224 * SCALE

    global INITIAL_HEIGHT
    INITIAL_HEIGHT = 228 * SCALE

    global SCREENRECT
    SCREENRECT = pg.Rect(0, 0, INITIAL_WIDTH, INITIAL_HEIGHT)

    global cwd
    cwd = os.path.split(os.path.abspath(__file__))[0]

    global clock
    clock = pg.time.Clock()
