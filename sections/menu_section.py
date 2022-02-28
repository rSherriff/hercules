
import json
from enum import Enum, auto
from math import sqrt

import numpy as np
import tcod
from actions.actions import SelectLevelAction, EscapeAction
from tcod import Console
from ui.menu_main_ui import MenuMainUI
from effects.horizontal_wipe_effect import HorizontalWipeDirection, HorizontalWipeEffect

from sections.section import Section


class MenuState(Enum):
    MAIN = auto()
    STAGE_SELECT = auto()
    LEVEL_SELECT = auto()


class MenuSection(Section):
    def __init__(self, engine, x: int, y: int, width: int, height: int):
        super().__init__(engine, x, y, width, height)      
        self.state = MenuState.MAIN
        self.stages = {}
        self.selected_stage = None
        self.selected_stage_index = 0
        self.selected_level = 0


        self.main_tiles = self.load_xp_data("menu_main.xp")
        self.stage_tiles = self.load_xp_data("menu_stage.xp")
        self.level_tiles = self.load_xp_data("menu_level.xp")
        self.load_tiles("main", self.main_tiles)

        self.main_ui = MenuMainUI(self, self.tiles["graphic"])
        self.ui = self.main_ui
        self.transition_effect = HorizontalWipeEffect(self.engine,0,0,self.width, self.height)
        with open ( "game_data/levels.json" ) as f:
            data = json.load(f)
            for stage in data["stages"]:
                self.stages[stage["name"]] = stage

    def update(self):
        pass
    
    def render(self, console):
        super().render(console)

        temp_console = Console(width=console.width, height=console.height, order="F")
    
        if self.state == MenuState.STAGE_SELECT:
            temp_console.print(0,0, "Crowns: " + str(self.engine.get_total_awarded_crowns()), (255,255,255))
            temp_console.blit(console, dest_x=1, dest_y=25, width=25, height=1)
            count = 0
            for stage in self.stages.values():
                if count == self.selected_stage_index:
                    temp_console.print(1,count+ 5, "->", (255,255,255))
                temp_console.print(4,count+ 5, stage["name"],(255,255,255))
                temp_console.blit(console, src_x=1, src_y=count+ 5, dest_x=4, dest_y=count+ 15, width=40, height=1)
                count += 1
        elif self.state == MenuState.LEVEL_SELECT:
            temp_console.print(0,0, "Crowns: " + str(self.engine.get_total_awarded_crowns()), (255,255,255))
            temp_console.blit(console, dest_x=1, dest_y=25, width=25, height=1)
            count = 0
            for level in self.stages[self.selected_stage]["levels"]:
                if count == self.selected_level:
                    temp_console.print(1,count+ 5, "->", (255,255,255))
                temp_console.print(4,count+ 5, level["name"] + " " + str(self.engine.get_awarded_crowns(level["name"])) + "/" + str(level["num_crowns"]), (255,255,255))
                temp_console.blit(console, src_x=1, src_y=count+ 5, dest_x=4, dest_y=count+ 15, width=40, height=1)
                count += 1

        if self.transition_effect.in_effect == True:
            self.transition_effect.render(console)


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
                self.change_state(MenuState.LEVEL_SELECT)
            elif self.state == MenuState.LEVEL_SELECT:
                stage = {}
                stage["name"] = self.selected_stage
                stage["ending_music"] = self.stages[self.selected_stage]["ending_music"]
                stage["start_music"] = self.stages[self.selected_stage]["start_music"]
                stage["start_length"] = self.stages[self.selected_stage]["start_length"]
                stage["end_length"] = self.stages[self.selected_stage]["end_length"]
                SelectLevelAction(self.engine, stage, self.stages[self.selected_stage]["levels"][self.selected_level]).perform()
        elif key == tcod.event.K_BACKSPACE:
            if self.state == MenuState.STAGE_SELECT:
                self.change_state(MenuState.MAIN)
            elif self.state == MenuState.LEVEL_SELECT:
                self.change_state(MenuState.STAGE_SELECT)
            self.selected_level = 0
        elif key == tcod.event.K_ESCAPE:
            EscapeAction(self.engine).perform()

    def change_state(self, new_state):
        if new_state == MenuState.MAIN:
            self.transition_effect.set_tiles(self.tiles["graphic"])
            self.load_tiles("main", self.main_tiles)
            self.transition_effect.start(HorizontalWipeDirection.RIGHT)
            self.ui = self.main_ui
        elif new_state == MenuState.STAGE_SELECT:
            self.transition_effect.set_tiles(self.tiles["graphic"])
            self.load_tiles("stage", self.stage_tiles)
            self.ui = None

            if self.state == MenuState.MAIN:
                self.transition_effect.start(HorizontalWipeDirection.LEFT)
            else:
                self.transition_effect.start(HorizontalWipeDirection.RIGHT)
                
        elif new_state == MenuState.LEVEL_SELECT:
            self.transition_effect.set_tiles(self.tiles["graphic"])
            self.load_tiles("level", self.level_tiles)
            self.ui = None
            self.transition_effect.start(HorizontalWipeDirection.LEFT)

        self.state = new_state

    def enter_stage_select(self):
        self.change_state(MenuState.STAGE_SELECT)