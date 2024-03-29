
import copy
import json
from enum import Enum, auto
from math import sqrt

import numpy as np
import tcod
from actions.actions import EscapeAction, SelectLevelAction
from effects.horizontal_wipe_effect import (HorizontalWipeDirection,
                                            HorizontalWipeEffect)
from tcod import Console
from ui.menu_main_ui import MenuMainUI
from ui.menu_options_ui import MenuOptionsUI
from ui.menu_stage_ui import MenuStageUI

from sections.section import Section


class MenuState(Enum):
    MAIN = auto()
    STAGE_SCREEN = auto()
    OPTIONS = auto()


class MenuSection(Section):
    def __init__(self, engine, x: int, y: int, width: int, height: int):
        super().__init__(engine, x, y, width, height)      
        self.state = MenuState.MAIN
        self.stages = []
        self.selected_stage_index = 0
        self.selected_level = 0
        self.button_decoration_index =0

        self.enabled_level_colour = (255,255,255)
        self.disabled_level_colour = (40,40,40)

        self.stage_tiles = []
        levels_path = "game_data/levels_demo.json" if self.engine.is_demo() else "game_data/levels.json"
        with open ( levels_path ) as f:
            data = json.load(f)
            for stage in data["stages"]:
                self.stages.append(stage)
                self.stage_tiles.append(self.load_xp_data(stage["background"]))

        self.stage_ui = MenuStageUI(self, self.tiles["graphic"])

        self.options_tiles = self.load_xp_data("menu_options.xp")
        self.load_tiles("options", self.options_tiles)
        self.options_ui = MenuOptionsUI(self, self.tiles["graphic"])

        main_tiles_path = "menu_main_demo.xp" if self.engine.is_demo() else "menu_main.xp"
        self.main_tiles = self.load_xp_data(main_tiles_path)
        self.load_tiles("main", self.main_tiles)
        self.main_ui = MenuMainUI(self, self.tiles["graphic"], self.engine.is_demo())
        self.ui = self.main_ui

        self.transition_effect = HorizontalWipeEffect(self.engine,0,0,self.width, self.height)
       

    def update(self):
        if "Menu" in self.engine.disabled_ui_sections and not self.transition_effect.in_effect and "notificationDialog" in self.engine.disabled_sections:
            self.engine.enable_ui_section("Menu")
    
    def render(self, console):
        super().render(console)
    
        if self.state == MenuState.STAGE_SCREEN:
            """
            temp_console.print(0,0, "Crowns: " + str(self.engine.get_total_awarded_crowns()), (255,255,255))
            temp_console.blit(console, dest_x=1, dest_y=25, width=25, height=1)
            """

            level_name_pos = copy.copy(self.stages[self.selected_stage_index]["level_names_pos"])
            if self.engine.is_demo():
                level_name_pos[0] += 9
                level_name_pos[1] -= 1
            crowns_awarded_pos = copy.copy(self.stages[self.selected_stage_index]["crowns_awarded_pos"])
            count = 0
            for level in self.stages[self.selected_stage_index]["levels"]:
                level_colour = self.enabled_level_colour if self.can_play_level(count) else self.disabled_level_colour
                level_indicator = "->" if self.can_play_level(count) else " x"

                if count == self.selected_level:
                    console.print(level_name_pos[0] - 3,level_name_pos[1], level_indicator, level_colour)
                
                console.print(level_name_pos[0],level_name_pos[1], level["name"], level_colour)

                if not self.engine.is_demo():
                    crowns_text = str(self.engine.get_awarded_crowns(level["name"])) + "/" + str(level["num_crowns"])
                    console.print(crowns_awarded_pos[0],crowns_awarded_pos[1], crowns_text, level_colour)
                
                level_name_pos[1] += 2
                crowns_awarded_pos[1] += 2
                count += 1

            #Indicate you can move to the next stage when all the levels in a stage are complete
            if not self.engine.is_demo():
                if "levels_completed" in self.engine.save_data and self.engine.save_data["levels_completed"] == self.stages[self.selected_stage_index]["levels"][-1]["number"] and self.stages[self.selected_stage_index]["name"] != "Epilogue":
                    
                    width = 3
                    height = 1

                    w = int(self.button_decoration_index) % width
                    h = int(int(self.button_decoration_index - w) / width)

                    console.print(47 + w, 23 + h, string='*', fg=(255,255,255))

                    self.button_decoration_index += (self.engine.get_delta_time() * width) 
                    self.button_decoration_index %= width * height

        if self.transition_effect.in_effect == True:
            self.transition_effect.render(console)
        elif self.state == MenuState.OPTIONS:
            self.transition_effect.set_tiles(console.tiles_rgb)



    def mousedown(self,button,x,y):
        pass

    def keydown(self, key):
        if self.state == MenuState.STAGE_SCREEN:
            if key == tcod.event.K_UP:
                    self.selected_level -= 1
                    self.selected_level = max(0, self.selected_level)
            elif key == tcod.event.K_DOWN:
                    self.selected_level += 1
                    self.selected_level = min(len(self.stages[self.selected_stage_index]["levels"]) - 1, self.selected_level)
            elif key == tcod.event.K_RIGHT:
                    if self.selected_stage_index < len(self.stages) - 1:
                        self.change_stage(self.selected_stage_index + 1)
            elif key == tcod.event.K_LEFT:
                    self.change_stage(self.selected_stage_index - 1)
            elif key == tcod.event.K_RETURN:
                    self.select_level(self.selected_level)
            elif key == tcod.event.K_BACKSPACE or key == tcod.event.K_ESCAPE:
                self.change_state(MenuState.MAIN)
                self.selected_level = 0
        elif self.state == MenuState.MAIN:
            if key == tcod.event.K_ESCAPE and not self.engine.is_demo():
                EscapeAction(self.engine).perform()
        elif self.state == MenuState.OPTIONS:
            if key == tcod.event.K_ESCAPE:
                self.change_state(MenuState.MAIN)

    def hover_over_level(self, level_index):
        if level_index >= len( self.stages[self.selected_stage_index]["levels"]):
            return

        self.selected_level = level_index

    def select_level(self,level_index):
        if level_index >= len( self.stages[self.selected_stage_index]["levels"]):
            return

        if self.can_play_level(level_index):
            stage = {}
            stage["name"] = self.stages[self.selected_stage_index]["name"]
            stage["ending_music"] = self.stages[self.selected_stage_index]["ending_music"]
            stage["start_music"] = self.stages[self.selected_stage_index]["start_music"]
            stage["start_length"] = self.stages[self.selected_stage_index]["start_length"]
            stage["end_length"] = self.stages[self.selected_stage_index]["end_length"]
            SelectLevelAction(self.engine, stage, self.stages[self.selected_stage_index]["levels"][level_index]).perform()

    def delta_change_stage(self, delta):
        self.change_stage(self.selected_stage_index + delta)

    def change_stage(self, new_stage):
        if new_stage == -1:
            self.change_state(MenuState.MAIN)
            return
        if new_stage >= len(self.stages):
            return

        self.transition_effect.set_tiles(self.tiles["graphic"])

        if new_stage > self.selected_stage_index:
            self.transition_effect.start(HorizontalWipeDirection.LEFT)
        else:
            self.transition_effect.start(HorizontalWipeDirection.RIGHT)

        self.selected_stage_index = new_stage
        self.load_tiles("stage", self.stage_tiles[self.selected_stage_index])
        self.selected_level = 0

        self.ui.tiles = self.tiles["graphic"]
        level_name_pos = copy.copy(self.stages[self.selected_stage_index]["level_names_pos"])
        if self.engine.is_demo():
            level_name_pos[0] += 9
            level_name_pos[1] -= 1
        self.ui.setup_level_buttons(level_name_pos, self.engine.is_demo())

    def change_state(self, new_state):
        if new_state == MenuState.MAIN:

            if self.state != MenuState.OPTIONS:
                self.transition_effect.set_tiles(self.tiles["graphic"])

            self.transition_effect.start(HorizontalWipeDirection.RIGHT)
            self.load_tiles("main", self.main_tiles)
            self.ui = self.main_ui
            
        elif new_state == MenuState.STAGE_SCREEN:
            self.selected_stage_index = 0
            self.transition_effect.set_tiles(self.tiles["graphic"])
            self.load_tiles("stage", self.stage_tiles[self.selected_stage_index])
            self.ui = self.stage_ui
            level_name_pos = copy.copy(self.stages[self.selected_stage_index]["level_names_pos"])
            if self.engine.is_demo():
                level_name_pos[0] += 9
                level_name_pos[1] -= 1
            self.ui.setup_level_buttons(level_name_pos, self.engine.is_demo())

            if self.state == MenuState.MAIN:
                self.transition_effect.start(HorizontalWipeDirection.LEFT)
            else:
                self.transition_effect.start(HorizontalWipeDirection.RIGHT)

        elif new_state == MenuState.OPTIONS:
            self.transition_effect.set_tiles(self.tiles["graphic"])
            self.load_tiles("options", self.options_tiles)
            self.transition_effect.start(HorizontalWipeDirection.RIGHT)
            self.ui = self.options_ui

        self.engine.disable_ui_section("Menu")
        self.state = new_state

    def enter_main(self):
        self.change_state(MenuState.MAIN)

    def enter_stage_select(self):
        self.change_state(MenuState.STAGE_SCREEN)

    def enter_options(self):
        self.change_state(MenuState.OPTIONS)

    def can_play_level(self, level_index):
        if "levels_completed" not in self.engine.save_data:
            if  self.selected_stage_index == 0 and level_index == 0:
                return True
            else:
                return False
        
        return self.engine.save_data["levels_completed"] >= self.stages[self.selected_stage_index]["levels"][level_index]["number"] - 1
