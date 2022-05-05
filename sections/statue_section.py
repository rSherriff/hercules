
import copy
import enum
import random
from enum import Enum, auto
from math import sqrt
from threading import Timer

import numpy as np
import tcod
from actions.actions import (EndMusicQueueAction, LevelCompleteAction,
                             LevelLeaveAction, OpenConfirmationDialog,
                             QueueMusicAction)
from data.statue_summary import StatueSummary
from effects.brick_wall_effect import BrickWallDirection, BrickWallEffect
from effects.horizontal_move_effect import (HorizontalMoveDirection,
                                            HorizontalMoveEffect)
from effects.vertical_move_effect import (VerticalMoveDirection,
                                          VerticalMoveEffect)
from effects.vertical_wipe_effect import (VerticalWipeDirection,
                                          VerticalWipeEffect)
from entities.anchor import Anchor
from entities.blocker import Blocker
from entities.material import BlockMaterial, Material, StatueMaterial
from pygame import mixer
from tcod import Console
from ui.statue_ended_ui import StatueEndedUI
from utils.color import black, spot_line, blend_colour, blend_colour_with_alpha
from utils.utils import translate_range

from sections.section import Section


class StatueState(Enum):
    NONE = auto()
    INACTIVE = auto()
    LOAD_HEADER = auto()
    LOAD_FOOTER = auto()
    LOAD_SIDES = auto()
    LOAD_MATERIAL = auto()
    LOAD_TEXT = auto()
    IN_PROGRESS = auto()
    ENDING = auto()
    ENDED = auto()

class SpottingLineType(Enum):
    FREE = auto()
    EIGHT_POINTS = auto()

class StatueSection(Section):
    def __init__(self, engine, x: int, y: int, width: int, height: int, xp_filepath: str = ""):
        super().__init__(engine, x, y, width, height, xp_filepath=xp_filepath)      

        self.max_spotted_material_tiles = 3
        self.index_into_render = 1 
        self.state_speed = 10
        self.reset()              

        self.update_graph()

        self.statue_ended_ui = StatueEndedUI(self)

        self.left_click_sound = self.validate_sound('Sounds/left_click.ogg')
        self.right_click_sound = self.validate_sound('Sounds/right_click.ogg')
        self.fault_sound = self.validate_sound('Sounds/fault.ogg')
        self.curtain_sound =  self.validate_sound('Sounds/curtains.ogg')

        self.spotting_line_type = SpottingLineType.EIGHT_POINTS

    def reset(self):
        self.mousedown_point = None
        self.spotting = False
        self.spotted_statue_tiles = 0
        self.spotted_tiles = list()
        self.remaining_blocks = 0
        self.cleared_blocks = 0
        self.remaining_statue = 0
        self.faults = 0
        self.anchor = None
        self.graph = None
        self.level = None
        self.state = StatueState.INACTIVE
        self.summary = None
        self.ui = None
        self.finished_setup = False
        self.finished_ending = False
        self.transistioning_to_state = StatueState.NONE
        self.current_text_fading_time = 0

        self.footer_y = 0
        self.footer_height = 0
        self.header_height = 0
        self.sides_y = 0
        self.sides_width = 0
        self.sides_height = 0

        self.name_char_probabilites = []

        self.entities.clear()

        self.stage = None

        self.complete_sound = None

        self.load_header_effect = None
        self.load_footer_effect = None
        self.load_material_effect = None
        self.load_side_left_effect = None
        self.load_side_right_effect = None
        self.ending_effect = None


    def update(self):
        self.update_spotting_line()
    
    def render(self, console):
        if self.state == StatueState.LOAD_FOOTER:
            self.render_load_footer(console)
        elif self.state == StatueState.LOAD_HEADER:
            self.render_load_header(console)
        elif self.state == StatueState.LOAD_SIDES:
            self.render_load_sides(console)
        elif self.state == StatueState.LOAD_MATERIAL:
            self.render_load_material(console)
        elif self.state == StatueState.LOAD_TEXT:
            self.render_load_text(console)
        elif self.state == StatueState.IN_PROGRESS:
            self.render_in_progress(console)
        elif self.state == StatueState.ENDING:
            self.render_ending(console)
        elif self.state == StatueState.ENDED:
            self.render_ended(console)

    def render_load_footer(self, console):
        if self.load_footer_effect == None:
            self.load_footer_effect = VerticalWipeEffect(self.engine, 0, self.footer_y, self.width, self.footer_height)


        if not self.load_footer_effect.in_effect:
            if self.load_footer_effect.time_alive > 0:
                self.state = StatueState.LOAD_HEADER
                self.render_load_header(console)
                return

            temp_console = Console(width=self.width, height=self.footer_height, order="F")
            temp_console.tiles_rgb[0 :self.width, 0: self.footer_height] = self.tiles[0 :self.width, self.footer_y: self.footer_y + self.footer_height]["graphic"]

            self.load_footer_effect.tiles = temp_console.tiles
            self.load_footer_effect.start(VerticalWipeDirection.UP)

        elif self.load_footer_effect.in_effect == True:
            self.load_footer_effect.render(console)

    def render_load_header(self, console):
        if self.load_header_effect == None:
            self.load_header_effect = VerticalMoveEffect(self.engine, 0, 0, self.width, self.header_height)

        if not self.load_header_effect.in_effect:
            if self.load_header_effect.time_alive > 0:
                self.state = StatueState.LOAD_SIDES
                self.render_load_sides(console)
                return

            temp_console = Console(width=self.width, height=self.header_height, order="F")
            temp_console.tiles_rgb[0 :self.width, 0: self.header_height] = self.tiles[0 :self.width, 0: self.header_height]["graphic"]

            self.load_header_effect.tiles = temp_console.tiles
            self.load_header_effect.start(VerticalMoveDirection.DOWN)

        elif self.load_header_effect.in_effect == True:
            self.load_header_effect.render(console)

        temp_console = Console(width=self.width, height=self.footer_height, order="F")
        temp_console.tiles_rgb[0 :self.width, 0: self.footer_height] = self.tiles[0 :self.width, self.footer_y: self.footer_y + self.footer_height]["graphic"]
        temp_console.blit(console, src_x=0, src_y=0, dest_x=0, dest_y=self.footer_y, width=self.width, height=self.footer_height)

    def render_load_sides(self, console):
        if self.load_side_left_effect == None:
            self.load_side_left_effect = HorizontalMoveEffect(self.engine, 0, self.sides_y, self.sides_width, self.sides_height)
            self.load_side_right_effect = HorizontalMoveEffect(self.engine, self.width - self.sides_width, self.sides_y, self.sides_width, self.sides_height)

        if not self.load_side_left_effect.in_effect:
            if self.load_side_left_effect.time_alive > 0:
                self.state = StatueState.LOAD_MATERIAL
                self.render_load_material(console)
                return

            left_temp_console = Console(width=self.sides_width, height=self.sides_height, order="F")
            left_temp_console.tiles_rgb[0 :self.sides_width, 0: self.sides_height] = self.tiles[0 :self.sides_width, self.sides_y: self.sides_y+ self.sides_height]["graphic"]

            self.load_side_left_effect.tiles = left_temp_console.tiles
            self.load_side_left_effect.start(HorizontalMoveDirection.LEFT)

            right_temp_console = Console(width=self.sides_width, height=self.sides_height, order="F")
            right_temp_console.tiles_rgb[0 :self.sides_width, 0: self.sides_height] = self.tiles[self.width - self.sides_width  -1 : (self.width - self.sides_width) + self.sides_width - 1, self.sides_y: self.sides_y+ self.sides_height]["graphic"]

            self.load_side_right_effect.tiles = right_temp_console.tiles
            self.load_side_right_effect.start(HorizontalMoveDirection.RIGHT)

        elif self.load_side_left_effect.in_effect == True:
            self.load_side_left_effect.render(console)
            self.load_side_right_effect.render(console)

        temp_console = Console(width=self.width, height=self.footer_height, order="F")
        temp_console.tiles_rgb[0 :self.width, 0: self.footer_height] = self.tiles[0 :self.width, self.footer_y: self.footer_y + self.footer_height]["graphic"]
        temp_console.blit(console, src_x=0, src_y=0, dest_x=0, dest_y=self.footer_y, width=self.width, height=self.footer_height)

        temp_console = Console(width=self.width, height=self.header_height, order="F")
        temp_console.tiles_rgb[0 :self.width, 0: self.header_height] = self.tiles[0 :self.width, 0: self.header_height]["graphic"]
        temp_console.blit(console, src_x=0, src_y=0, dest_x=0, dest_y=0, width=self.width, height=self.header_height)

    def render_load_material(self, console):
        if self.load_material_effect == None:
            self.load_material_effect = BrickWallEffect(self.engine, self.level["x"], self.level["y"], self.level["width"], self.level["height"])

        if not self.load_material_effect.in_effect:

            if self.load_material_effect.time_alive > 0:
                self.change_state(StatueState.LOAD_TEXT)
                self.render_static(console, True)
                return

            temp_console = Console(width=self.level["width"], height=self.level["height"], order="F")
            temp_console.tiles_rgb[self.x : self.x + self.width, self.y: self.y + self.height] = self.tiles[self.level["x"]:self.level["x"]+self.level["width"], self.level["y"]:self.level["y"]+self.level["height"] ]["graphic"]
            for entity in self.entities:
                temp_console.print(entity.x - self.level["x"], entity.y - self.level["y"],entity.char, fg=entity.fg_color, bg=entity.bg_color)

            self.load_material_effect.tiles = temp_console.tiles            
            self.load_material_effect.start(BrickWallDirection.UP)

        elif self.load_material_effect.in_effect == True:
            self.load_material_effect.render(console)

        self.render_static(console, False)

    def render_load_text(self,console):
        if self.current_text_fading_time > self.stage["start_length"]:
            if not self.finished_setup:
                super().render(console)
                if not self.level["disable_faults"]:
                    self.render_faults(console)

                self.render_spotted_tiles(console)
                self.render_material(console)

                if self.spotting:
                    self.render_spotting_line(console)

                self.finish_setup()
                return
        else:
            self.current_text_fading_time += self.engine.get_delta_time()

        self.render_static(console, False)

        t = translate_range(self.current_text_fading_time, 0, self.stage["start_length"], 0, 1)

        #Fade tutorial text
        if "tutorial_text_x" in self.level:
            x_extent = self.level["tutorial_text_x"] + self.level["tutorial_text_width"]
            y_extent = self.level["tutorial_text_y"] + self.level["tutorial_text_height"]
            for w in range(self.level["tutorial_text_x"], x_extent):
                for h in range(self.level["tutorial_text_y"], y_extent):
                    new_tile =  copy.copy(self.tiles[w,h]["graphic"])
                    new_tile[1] = blend_colour(new_tile[1], (0,0,0), t)
                    new_tile[2] = blend_colour(new_tile[2], (0,0,0), t)

                    console.tiles_rgb[w,h] = new_tile
        
        font = self.engine.font_manager.get_font("number_font")

        #Fade faults
        if not self.level["disable_faults"]:
            faults_string = "0"
            faults_console = Console(width = font.char_width * len(faults_string) + 1, height = font.char_height, order="F")
            faults_console.tiles_rgb[0:font.char_width, 0:font.char_height] = font.get_character(faults_string[0])
            final_width = font.char_width * len(faults_string)

            final_x = self.level["faults_x"] + 2
            if len(faults_string) > 1:
                final_width += 1
                final_x -= 2
            
            for w in range(0, final_width):
                for h in range(0, font.char_height):
                    new_tile =  copy.copy(faults_console.tiles[w,h])
                    new_tile[1] = blend_colour_with_alpha(new_tile[1], (0,0,0,255), t)
                    new_tile[2] = blend_colour_with_alpha(new_tile[2], (0,0,0,255), t)

                    faults_console.tiles_rgb[w,h] = new_tile
            faults_console.blit(console, src_x=0, src_y=0, dest_x = final_x, dest_y = self.level["faults_y"], width = final_width, height = font.char_height)

        #Fade Spotting numbers
        num_to_render = '0'
        if self.spotting:
            num_to_render = str(self.spotted_statue_tiles)
        for i in range(0, len(self.level["spotted_tiles_x"])):
            spotting_console = Console(width = font.char_width, height = font.char_height, order="F")
            spotting_console.tiles_rgb[0: font.char_width, 0:font.char_height] = font.get_character(num_to_render)

            x = self.level["spotted_tiles_x"][i] - int(font.char_width / 2)
            y = self.level["spotted_tiles_y"][i] - int(font.char_height / 2)

            for w in range(0, font.char_width):
                for h in range(0, font.char_height):
                    new_tile =  copy.copy(spotting_console.tiles[w,h])
                    new_tile[1] = blend_colour_with_alpha(new_tile[1], (0,0,0,255), t)
                    new_tile[2] = blend_colour_with_alpha(new_tile[2], (0,0,0,255), t)
                    spotting_console.tiles_rgb[w,h] = new_tile

            spotting_console.blit(console, src_x=0, src_y=0, dest_x = x, dest_y = y, width = font.char_width, height = font.char_height)
       
        self.render_material(console)
        if self.spotting:
            self.render_spotting_line(console)


    def render_static(self, console, render_material):
        
        #Render material
        if render_material:
            self.render_material(console)

        #Render footer
        temp_console = Console(width=self.width, height=self.footer_height, order="F")
        temp_console.tiles_rgb[0 :self.width, 0: self.footer_height] = self.tiles[0 :self.width, self.footer_y: self.footer_y + self.footer_height]["graphic"]
        temp_console.blit(console, src_x=0, src_y=0, dest_x=0, dest_y=self.footer_y, width=self.width, height=self.footer_height)

        #Render header
        temp_console = Console(width=self.width, height=self.header_height, order="F")
        temp_console.tiles_rgb[0 :self.width, 0: self.header_height] = self.tiles[0 :self.width, 0: self.header_height]["graphic"]
        temp_console.blit(console, src_x=0, src_y=0, dest_x=0, dest_y=0, width=self.width, height=self.header_height)

        #Render side left
        temp_console = Console(width=self.sides_width, height=self.sides_height, order="F")
        temp_console.tiles_rgb[0 :self.sides_width, 0: self.sides_height] = self.tiles[0 :self.sides_width, self.sides_y: self.sides_y+ self.sides_height]["graphic"]
        temp_console.blit(console, src_x=0, src_y=0, dest_x=0, dest_y=self.sides_y, width=self.sides_width, height=self.sides_height)

        #Render side right
        temp_console = Console(width=self.sides_width + 1, height=self.sides_height, order="F")
        temp_console.tiles_rgb[0 :self.sides_width + 1, 0: self.sides_height] = self.tiles[self.width - self.sides_width -1: (self.width - self.sides_width - 1) + self.sides_width + 1, self.sides_y: self.sides_y+ self.sides_height]["graphic"]
        temp_console.blit(console, src_x=0, src_y=0, dest_x=self.width - self.sides_width - 1, dest_y=self.sides_y, width=self.sides_width + 1, height=self.sides_height)

    def render_material(self, console):
        temp_console = Console(width=self.level["width"], height=self.level["height"], order="F")
        temp_console.tiles_rgb[self.x : self.x + self.width, self.y: self.y + self.height] = self.tiles[self.level["x"]:self.level["x"]+self.level["width"], self.level["y"]:self.level["y"]+self.level["height"] ]["graphic"]
        for entity in self.entities:
            temp_console.print(entity.x - self.level["x"], entity.y - self.level["y"],entity.char, fg=entity.fg_color, bg=entity.bg_color)
        temp_console.blit(console, dest_x=self.level["x"], dest_y=self.level["y"], width=self.level["width"], height=self.level["height"])

    def render_in_progress(self, console):
        super().render(console)

        temp_console = Console(width=console.width, height=console.height, order="F")

        temp_console.print(1,1, "Spotted Blocks: " + str(self.spotted_statue_tiles), (255,255,255))
        #temp_console.blit(console, src_x=1, src_y=1, dest_x=1, dest_y=1, width=17, height=1)           

        temp_console.print(1,2, "Remaining Blocks: " + str(self.remaining_blocks), (255,255,255))
        #temp_console.blit(console, src_x=1, src_y=2, dest_x=1, dest_y=2, width=22, height=1)

        temp_console.print(1,3, "Mistakes: " + str(self.faults), (255,255,255))
        #temp_console.blit(console, src_x=1, src_y=3, dest_x=1, dest_y=2, width=12, height=1)

        if self.level is not None:
            for i in range(0,len(self.level["name"])):
                if self.cleared_blocks >= self.name_char_probabilites[i]:
                    temp_console.print(i,0, self.level["name"][i], (255,255,255))
                    temp_console.blit(console, src_x=0, src_y=0, dest_x=self.level["name_x"], dest_y=self.level["name_y"], width=len(self.level["name"]), height=1)

            if not self.level["disable_faults"]:
                self.render_faults(console)

        if self.spotting:
            self.render_spotting_line(console)
        
        self.render_spotted_tiles(console)

    def render_ending(self, console):
        temp_console = Console(width=self.level["width"], height=self.level["height"], order="F")
        temp_console.tiles_rgb[self.x : self.x + self.width, self.y: self.y + self.height] = self.tiles[self.level["x"]:self.level["x"]+self.level["width"], self.level["y"]:self.level["y"]+self.level["height"] ]["graphic"]
        temp_console.blit(console, src_x= 0, src_y=0, dest_x = self.level["x"], dest_y=self.level["y"], width=self.level["width"], height=self.level["height"])
 
    def render_ended(self, console):
        self.render_statue(console)
 
        button_width = self.ui.summary_button.width
        button_height = self.ui.summary_button.height
        button_console = Console(width=button_width, height=button_height, order="F")
        button_console.draw_frame(0,0, button_width, button_height, decoration="╔═╗║ ║╚═╝")
        button_console.print_rect(1,1,button_width, button_height,"Continue")
        self.ui.summary_button.tiles = button_console.tiles_rgb

        console.print_box(0,26, self.width, 1, self.level["name"], fg=(255,255,255), bg=(0,0,0), alignment=tcod.CENTER)

        info_text = ""
        if self.level["artist"] != "N/A":
            info_text += self.level["artist"]
        if self.level["date"] != "N/A":
            if len(info_text) > 0:
                info_text += " - "
            info_text += self.level["date"]

        console.print_box(0,28, self.width, 1, info_text, fg=(255,255,255), bg=(0,0,0), alignment=tcod.CENTER)

        self.ui.render(console)
   
    def render_spotting_line(self, console):
        temp_console = Console(width=console.width, height=console.height, order="F")
        
        max_tile = min(10, len(self.spotted_tiles))
        for i in range(0,max_tile):
            tile = self.spotted_tiles[i]
            temp_console.tiles_rgb[tile[0], tile[1]] = (9632, black,spot_line)
            temp_console.blit(console, src_x=tile[0], src_y=tile[1], dest_x=tile[0], dest_y=tile[1], width=1, height=1)

    def render_faults(self,console):
        faults_to_render = min(99,self.faults)
        faults_string = str(faults_to_render)
        font = self.engine.font_manager.get_font("number_font")
        faults_console = Console(width = font.char_width * len(faults_string) + 1, height = font.char_height, order="F")
        for i in range(0, len(faults_string)):
            start_x = i * font.char_width
            if i > 0:
                start_x += 1
            faults_console.tiles_rgb[start_x:start_x+ font.char_width, 0:font.char_height] = font.get_character(faults_string[i])
        final_width = font.char_width * len(faults_string)

        final_x = self.level["faults_x"] + 2
        if len(faults_string) > 1:
            final_width += 1
            final_x -= 2
        faults_console.blit(console, src_x=0, src_y=0, dest_x = final_x, dest_y = self.level["faults_y"], width = final_width, height = font.char_height)

    def render_spotted_tiles(self, console):
        font = self.engine.font_manager.get_font("number_font")

        num_to_render = '0'
        if self.spotting:
            num_to_render = str(self.spotted_statue_tiles)

        for i in range(0, len(self.level["spotted_tiles_x"])):
            temp_console = Console(width = font.char_width, height = font.char_height, order="F")
            temp_console.tiles_rgb[0: font.char_width, 0:font.char_height] = font.get_character(num_to_render)

            x =self.level["spotted_tiles_x"][i] - int(font.char_width / 2)
            y =self.level["spotted_tiles_y"][i] - int(font.char_height / 2)
            temp_console.blit(console, src_x=0, src_y=0, dest_x = x, dest_y = y, width = font.char_width, height = font.char_height)

    def render_statue(self, console):
        temp_console = Console(width=self.level["width"], height=self.level["height"], order="F")
        temp_console.tiles_rgb[self.x : self.x + self.width, self.y: self.y + self.height] = self.tiles[self.level["x"]:self.level["x"]+self.level["width"], self.level["y"]:self.level["y"]+self.level["height"] ]["graphic"]
        temp_console.blit(console, src_x= 0, src_y=0, dest_x = self.level["x"], dest_y=self.level["y"], width=self.level["width"], height=self.level["height"])

    def update_spotting_line(self):
    
        mouse_pos = (self.engine.mouse_location[0], self.engine.mouse_location[1])

        spotted_material_tiles = 0
        self.spotted_statue_tiles = 0
        self.spotted_tiles.clear()
        
        if self.mousedown_point is not None and mouse_pos != self.mousedown_point:

            final_line_point = (0,0)
            if self.spotting_line_type == SpottingLineType.FREE:
               final_line_point = mouse_pos
            elif self.spotting_line_type == SpottingLineType.EIGHT_POINTS:
                final_line_point = mouse_pos
                nearest_distance = self.get_distance_between_tiles(mouse_pos, self.mousedown_point)
                for tile in self.get_moore_surrounding_tiles(self.mousedown_point[0], self.mousedown_point[1]):
                    distance = self.get_distance_between_tiles(mouse_pos, tile)
                    if distance < nearest_distance:
                        nearest_distance = distance
                        final_line_point = tile
                        
            #Figure out the normalised vector between the mouse and the button press point            
            spot_line_magnitude = sqrt((abs(final_line_point[0]-self.mousedown_point[0])**2) + (abs(final_line_point[1]-self.mousedown_point[1])**2))
            spot_line_normalised = ((final_line_point[0]-self.mousedown_point[0])/spot_line_magnitude,  (final_line_point[1]-self.mousedown_point[1])/spot_line_magnitude)

            #Extend the line along the vector between the mouse and the button press point           
            final_spot = (self.mousedown_point[0] + int(spot_line_normalised[0] * 10),self.mousedown_point[1] + int(spot_line_normalised[1] * 10))


            #Loop through all of the points in this line
            for tile in self.line_between(self.mousedown_point, final_spot):
                if self.is_point_in_section(tile[0], tile[1]):
                    entities = self.get_entities_at_location(tile[0], tile[1])
                    if len(entities) >= 1: #If there are entites at this tile...
                        for entity in entities:
                            if isinstance(entity, Material):
                                spotted_material_tiles += 1 #Track how much material we have seen, blocker or statue
                            
                                if spotted_material_tiles > self.max_spotted_material_tiles: #If we've seen as deep as the rules allow, return
                                    return

                                if isinstance(entity, StatueMaterial): #If its staute material, track it so we can display it on the UI
                                    self.spotted_statue_tiles += 1

                    elif spotted_material_tiles > 0: #If there are no entities, but we have seen material in the past, return
                        return
                        
                    self.spotted_tiles.append(tile)
        else:
            self.spotted_tiles.append([mouse_pos[0], mouse_pos[1]])

    def mousedown(self,button,x,y):
        if not self.engine.is_confirmation_dialog_open() and (self.state == StatueState.LOAD_TEXT or self.state == StatueState.IN_PROGRESS):
            processed_entity = False
            if not self.spotting:
                for entity in self.get_entities_at_location(self.engine.mouse_location[0], self.engine.mouse_location[1]):
                    entity.mousedown(button)
                    processed_entity = True

            if button == 1 and not processed_entity:
                self.mousedown_point = (x,y)
                self.spotting = not self.spotting

    def keydown(self, key):
        #TEMP
        if key == tcod.event.K_p:
            self.entities = [x for x in self.entities if not isinstance(x, BlockMaterial) and not isinstance(x, StatueMaterial)]
            self.remaining_blocks = 0
            self.remaining_statue = 0
            self.remove_entity(None)


        if key == tcod.event.K_ESCAPE and self.state == StatueState.IN_PROGRESS and self.total_remaining_blocks() > 0:
            OpenConfirmationDialog(self.engine, "       Return to menu?\n(progress will not be saved)", LevelLeaveAction(self.engine)).perform()

        if key == tcod.event.K_RETURN and self.state == StatueState.ENDED:
            LevelCompleteAction(self.engine, StatueSummary(self.level, self.faults)).perform()

    def line_between(self, start, end):
        """Return an line between these two points."""
        x1, y1 = start
        x2, y2 = end

        # Generate the coordinates for this tunnel.
        for x, y in tcod.los.bresenham((x1, y1), (x2, y2)).tolist():
            yield x, y

    def update_graph(self):
        self.cost = np.array(self.tiles["walkable"], dtype=np.int8)
        for entity in self.entities:
            if entity.blocks_movement:
                self.cost[entity.x, entity.y] = 0

        self.graph = tcod.path.SimpleGraph(cost=self.cost, cardinal=1, diagonal=1)

    def chisel_fault(self):
        self.fault_sound.play()
        if not self.level["disable_faults"]:
            self.faults += 1

    def change_state(self, new_state):
        
        if new_state == StatueState.ENDED:
            self.transistioning_to_state = StatueState.ENDED
            print("Changing to ENDED")
            Timer(1.0, self.end_level).start()   
        elif new_state == StatueState.IN_PROGRESS:
            self.state = StatueState.IN_PROGRESS
            QueueMusicAction(self.engine, self.stage["name"] ).perform()
        else:
            self.state = new_state

    def finish_setup(self):
        self.finished_setup = True
        self.change_state(StatueState.IN_PROGRESS)
                        
    def complete_level(self):
        if self.complete_sound is not None:
            self.complete_sound.play()
        self.state = StatueState.ENDING 
        Timer(self.stage["end_length"],self.change_state,[StatueState.ENDED]).start()

    def end_level(self):
        self.ui = self.statue_ended_ui
        self.ui.summary_button.set_action(LevelCompleteAction(self.engine, StatueSummary(self.level, self.faults)))
        self.state = StatueState.ENDED
        self.transistioning_to_state = StatueState.NONE
             

    def add_entity(self, entity):
        if isinstance(entity, BlockMaterial):
            self.remaining_blocks += 1
        elif isinstance(entity, Anchor):
            self.anchor = entity
        elif isinstance(entity, StatueMaterial):
            self.remaining_statue += 1
        self.entities.append(entity)
        self.update_graph()
    
    def remove_entity(self, entity):
        if isinstance(entity, BlockMaterial):
            self.remaining_blocks -= 1
            self.cleared_blocks += 1
            self.left_click_sound.play()
        if isinstance(entity, StatueMaterial):
            self.remaining_statue -= 1
            self.cleared_blocks += 1
            self.right_click_sound.play()

        if self.total_remaining_blocks() == 0:
            EndMusicQueueAction(self.engine, 500).perform()
            Timer(2.0,self.complete_level).start()

        super().remove_entity(entity)
        self.update_graph()

    def total_remaining_blocks(self):
        return self.remaining_statue + self.remaining_blocks

    def load_level(self, stage, level):
        self.reset()

        self.stage = stage
        
        if stage["ending_music"] != "" and stage["start_music"] != "":
            self.complete_sound = mixer.Sound('Sounds/' + stage["ending_music"])
            self.start_sound = mixer.Sound('Sounds/' + stage["start_music"])
            self.start_sound.play()
            self.curtain_sound.play()

        xp_data = self.load_xp_data(level["file"])
        self.load_tiles(level["file"], xp_data)
        self.load_entities(level["file"], xp_data)

        if "fg_color" in level and "bg_color" in level:
            self.colour_material(level["fg_color"], level["bg_color"])
        else:
            self.colour_material((255,0,0), (0,255,0))

        self.level = level
        self.state = StatueState.LOAD_FOOTER

        self.footer_y = level["footer_y"]
        self.footer_height = level["footer_height"]
        self.header_height = level["header_height"]
        
        self.sides_y = level["sides_y"]
        self.sides_width = level["sides_width"]
        self.sides_height = level["sides_height"]

        probability_step = (self.total_remaining_blocks() * 0.9)/len(self.level["name"])
        self.name_char_probabilites = list(map(lambda num: max(1,int(num * probability_step)), range(1, len(self.level["name"]) + 1)))
        random.shuffle(self.name_char_probabilites)
        
    def colour_material(self, fg_color, bg_color):
        for entity in self.entities:
            if isinstance(entity, Material):
                entity.set_initial_colors(bg_color, fg_color)


