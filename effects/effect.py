import numpy as np

import tile_types

class Effect():
    def __init__(self, engine, x, y, width, height):
        self.engine = engine
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.in_effect = False
        self.lifespan = 10
        self.time_alive = 0
        self.tiles_set = False

    def render(self, console):
        raise NotImplementedError()

    def start(self):
        self.time_alive = 0
        self.tiles_set = False
        self.in_effect = True

    def stop(self):
        self.in_effect = False

    def set_tiles(self, tiles):
        self.tiles_set = True
        self.tiles = tiles.copy()

