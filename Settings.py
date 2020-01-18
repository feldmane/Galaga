import pygame as pg
import os

FPS = 60

SCALE = 3

INITIAL_WIDTH = 224 * SCALE

INITIAL_HEIGHT = 228 * SCALE

SCREENRECT = pg.Rect(0, 0, INITIAL_WIDTH, INITIAL_HEIGHT)

cwd = os.path.split(os.path.abspath(__file__))[0]

clock = pg.time.Clock()
