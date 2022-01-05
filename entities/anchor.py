
from typing import List, Tuple

import tcod
from utils.color import get_random_color

from entities.entity import Entity


class Anchor(Entity):
    def __init__(self, engine, x: int, y: int):
        super().__init__(engine, x, y, chr(0), (0,0,0), (0,0,0))
        self.invisible = True
    

