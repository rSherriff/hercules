
import json
from enum import Enum, auto
from math import sqrt
from typing import final

import numpy as np
import tcod
from numpy.lib.arraysetops import isin
from tcod import Console

from sections.section import Section


class HeaderSection(Section):
    def __init__(self, engine, x: int, y: int, width: int, height: int, xp_filepath: str = ""):
        super().__init__(engine, x, y, width, height, xp_filepath=xp_filepath)      

    def update(self):
        pass
    
    def render(self, console):
        super().render(console)

    def mousedown(self,button,x,y):
        pass

    def keydown(self, key):
        pass