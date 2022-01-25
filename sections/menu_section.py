
import json
from enum import Enum, auto
from math import sqrt

import numpy as np
import tcod
from actions.actions import SelectLevelAction, EscapeAction
from tcod import Console

from sections.section import Section


class MenuState(Enum):
    MAIN = auto()
    STAGE_SELECT = auto()
    LEVEL_SELECT = auto()


class MenuSection(Section):
    def __init__(self, engine, x: int, y: int, width: int, height: int, xp_filepath: str = ""):
        self.state = MenuState.STAGE_SELECT
        self.stages = {}
        self.selected_stage = None
        self.selected_stage_index = 0
        self.selected_level = 0
        with open ( "game_data/levels.json" ) as f:
            data = json.load(f)
            for stage in data["stages"]:
                self.stages[stage["name"]] = stage

        super().__init__(engine, x, y, width, height, xp_filepath=xp_filepath)      

    def update(self):
        pass
    
    def render(self, console):
        super().render(console)

        temp_console = Console(width=console.width, height=console.height, order="F")

        if self.state == MenuState.STAGE_SELECT:
            count = 0
            for stage in self.stages.values():
                if count == self.selected_stage_index:
                    temp_console.print(1,count+ 5, "->", (255,255,255))
                temp_console.print(4,count+ 5, stage["name"],(255,255,255))
                temp_console.blit(console, src_x=1, src_y=count+ 5, dest_x=4, dest_y=count+ 5, width=40, height=1)
                count += 1
        elif self.state == MenuState.LEVEL_SELECT:
            count = 0
            for level in self.stages[self.selected_stage]["levels"]:
                if count == self.selected_level:
                    temp_console.print(1,count+ 5, "->", (255,255,255))
                temp_console.print(4,count+ 5, level["name"] + " " + str(self.engine.get_awarded_crowns(level["name"])) + "/" + str(level["num_crowns"]), (255,255,255))
                temp_console.blit(console, src_x=1, src_y=count+ 5, dest_x=4, dest_y=count+ 5, width=40, height=1)
                count += 1

        temp_console.print(0,0, "Crowns: " + str(self.engine.get_total_awarded_crowns()), (255,255,255))
        temp_console.blit(console, dest_x=1, dest_y=1, width=25, height=1)

    def mousedown(self,button,x,y):
        pass

    def keydown(self, key):
        if key == tcod.event.K_UP:
            if self.state == MenuState.STAGE_SELECT:
                self.selected_stage_index -= 1
                self.selected_stage_index = max(0, self.selected_stage_index)
            elif self.state == MenuState.LEVEL_SELECT:
                self.selected_level -= 1
                self.selected_level = max(0, self.selected_level)
        elif key == tcod.event.K_DOWN:
            if self.state == MenuState.STAGE_SELECT:
                self.selected_stage_index += 1
                self.selected_stage_index = min(len(self.stages) - 1, self.selected_stage_index)
            elif self.state == MenuState.LEVEL_SELECT:
                self.selected_level += 1
                self.selected_level = min(len(self.stages[self.selected_stage]["levels"]) - 1, self.selected_level)
        elif key == tcod.event.K_RETURN:
            if self.state == MenuState.STAGE_SELECT:
                self.selected_stage = list(self.stages.values())[self.selected_stage_index]["name"]
                self.state = MenuState.LEVEL_SELECT
            elif self.state == MenuState.LEVEL_SELECT:
                SelectLevelAction(self.engine, self.stages[self.selected_stage]["levels"][self.selected_level]).perform()
        elif key == tcod.event.K_BACKSPACE:
            self.state = MenuState.STAGE_SELECT
        elif key == tcod.event.K_ESCAPE:
            EscapeAction(self.engine).perform()