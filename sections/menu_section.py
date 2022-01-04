
import json
from enum import Enum, auto
from math import sqrt
from typing import final

import numpy as np
import tcod
from actions.actions import SelectLevelAction
from numpy.lib.arraysetops import isin
from tcod import Console

from sections.section import Section


class MenuState(Enum):
    MAIN = auto()
    LEVEL_SELECT = auto()


class MenuSection(Section):
    def __init__(self, engine, x: int, y: int, width: int, height: int, xp_filepath: str = ""):
        self.state = MenuState.MAIN
        self.levels = []
        self.selected_level = 0
        with open ( "data/levels.json" ) as f:
            data = json.load(f)
            for level in data.values():
                self.levels.append(level)
        super().__init__(engine, x, y, width, height, xp_filepath=xp_filepath)      

    def update(self):
        pass
    
    def render(self, console):
        super().render(console)

        temp_console = Console(width=console.width, height=console.height, order="F")

        count = 0
        for level in self.levels:
            if count == self.selected_level:
                temp_console.print(1,count+ 5, "->", (255,255,255))
            temp_console.print(4,count+ 5, level["name"], (255,255,255))
            temp_console.blit(console, src_x=1, src_y=count+ 5, dest_x=4, dest_y=count+ 5, width=25, height=1)
            count += 1

    def mousedown(self,button,x,y):
        pass

    def keydown(self, key):
        if key == tcod.event.K_UP:
            self.selected_level -= 1
            self.selected_level = max(0, self.selected_level)
        elif key == tcod.event.K_DOWN:
            self.selected_level += 1
            self.selected_level = min(len(self.levels) - 1, self.selected_level)
        elif key == tcod.event.K_RETURN:
            SelectLevelAction(self.engine, self.levels[self.selected_level]).perform()