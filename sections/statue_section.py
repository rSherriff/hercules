
import random
from enum import Enum, auto
from math import sqrt
from threading import Timer

import numpy as np
import tcod
from actions.actions import LevelCompleteAction
from data.statue_summary import StatueSummary
from effects.brick_wall_effect import BrickWallDirection, BrickWallEffect
from effects.horizontal_move_effect import (HorizontalMoveDirection,
                                            HorizontalMoveEffect)
from effects.vertical_wipe_effect import (VerticalWipeDirection,
                                          VerticalWipeEffect)
from entities.anchor import Anchor
from entities.blocker import Blocker
from entities.material import BlockMaterial, Material, StatueMaterial
from tcod import Console
from utils.color import black, spot_line

from sections.section import Section


class StatueState(Enum):
    INACTIVE = auto()
    LOAD_HEADER = auto()
    LOAD_FOOTER = auto()
    LOAD_SIDES = auto()
    LOAD_MATERIAL = auto()
    IN_PROGRESS = auto()
    ENDING = auto()

class StatueSection(Section):
    def __init__(self, engine, x: int, y: int, width: int, height: int, xp_filepath: str = ""):
        self.max_spotted_material_tiles = 3
        self.index_into_render = 1 
        self.state_speed = 10
        self.footer_y = 26
        self.footer_height = 4
        self.header_height = 4
        
        self.sides_y = 4
        self.sides_width = 13
        self.sides_height = 22

        self.reset()       

        super().__init__(engine, x, y, width, height, xp_filepath=xp_filepath)      

        self.update_graph()

    def reset(self):
        self.mousedown_point = None
        self.spotting = False
        self.spotted_statue_tiles = 0
        self.spotted_tiles = list()
        self.remaining_blocks = 0
        self.cleared_blocks = 0
        self.mistakes = 0
        self.anchor = None
        self.graph = None
        self.level = None
        self.state = StatueState.INACTIVE
        self.level_ending = False

        self.name_char_probabilites = []

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
        elif self.state == StatueState.IN_PROGRESS:
            self.render_in_progress(console)
        elif self.state == StatueState.ENDING:
            self.render_ending(console)

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
            self.load_header_effect = VerticalWipeEffect(self.engine, 0, 0, self.width, self.header_height)

        if not self.load_header_effect.in_effect:
            if self.load_header_effect.time_alive > 0:
                self.state = StatueState.LOAD_SIDES
                self.render_load_sides(console)
                return

            temp_console = Console(width=self.width, height=self.header_height, order="F")
            temp_console.tiles_rgb[0 :self.width, 0: self.header_height] = self.tiles[0 :self.width, 0: self.header_height]["graphic"]

            self.load_header_effect.tiles = temp_console.tiles
            self.load_header_effect.start(VerticalWipeDirection.DOWN)

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
                self.state = StatueState.IN_PROGRESS
                self.render_in_progress(console)
                return

            temp_console = Console(width=self.level["width"], height=self.level["height"], order="F")
            temp_console.tiles_rgb[self.x : self.x + self.width, self.y: self.y + self.height] = self.tiles[self.level["x"]:self.level["x"]+self.level["width"], self.level["y"]:self.level["y"]+self.level["height"] ]["graphic"]
            for entity in self.entities:
                temp_console.print(entity.x - self.level["x"], entity.y - self.level["y"],entity.char, fg=entity.fg_color, bg=entity.bg_color)

            self.load_material_effect.tiles = temp_console.tiles            
            self.load_material_effect.start(BrickWallDirection.UP)

        elif self.load_material_effect.in_effect == True:
            self.load_material_effect.render(console)

        temp_console = Console(width=self.width, height=self.footer_height, order="F")
        temp_console.tiles_rgb[0 :self.width, 0: self.footer_height] = self.tiles[0 :self.width, self.footer_y: self.footer_y + self.footer_height]["graphic"]
        temp_console.blit(console, src_x=0, src_y=0, dest_x=0, dest_y=self.footer_y, width=self.width, height=self.footer_height)

        temp_console = Console(width=self.width, height=self.header_height, order="F")
        temp_console.tiles_rgb[0 :self.width, 0: self.header_height] = self.tiles[0 :self.width, 0: self.header_height]["graphic"]
        temp_console.blit(console, src_x=0, src_y=0, dest_x=0, dest_y=0, width=self.width, height=self.header_height)

        temp_console = Console(width=self.sides_width, height=self.sides_height, order="F")
        temp_console.tiles_rgb[0 :self.sides_width, 0: self.sides_height] = self.tiles[0 :self.sides_width, self.sides_y: self.sides_y+ self.sides_height]["graphic"]
        temp_console.blit(console, src_x=0, src_y=0, dest_x=0, dest_y=self.sides_y, width=self.sides_width, height=self.sides_height)

        temp_console = Console(width=self.sides_width + 1, height=self.sides_height, order="F")
        temp_console.tiles_rgb[0 :self.sides_width + 1, 0: self.sides_height] = self.tiles[self.width - self.sides_width -1: (self.width - self.sides_width - 1) + self.sides_width + 1, self.sides_y: self.sides_y+ self.sides_height]["graphic"]
        temp_console.blit(console, src_x=0, src_y=0, dest_x=self.width - self.sides_width - 1, dest_y=self.sides_y, width=self.sides_width + 1, height=self.sides_height)

    def render_in_progress(self, console):
        super().render(console)

        temp_console = Console(width=console.width, height=console.height, order="F")

        temp_console.print(1,1, "Spotted Blocks: " + str(self.spotted_statue_tiles), (255,255,255))
        #temp_console.blit(console, src_x=1, src_y=1, dest_x=1, dest_y=1, width=17, height=1)           

        temp_console.print(1,2, "Remaining Blocks: " + str(self.remaining_blocks), (255,255,255))
        #temp_console.blit(console, src_x=1, src_y=2, dest_x=1, dest_y=2, width=22, height=1)

        temp_console.print(1,3, "Mistakes: " + str(self.mistakes), (255,255,255))
        #temp_console.blit(console, src_x=1, src_y=3, dest_x=1, dest_y=2, width=12, height=1)

        if self.level is not None:
            for i in range(0,len(self.level["name"])):
                if self.cleared_blocks >= self.name_char_probabilites[i]:
                    temp_console.print(i,0, self.level["name"][i], (255,255,255))
                    temp_console.blit(console, src_x=0, src_y=0, dest_x=self.level["name_x"], dest_y=self.level["name_y"], width=len(self.level["name"]), height=1)

            mistakes_to_render = min(99,self.mistakes)
            mistakes_string = str(mistakes_to_render)
            font = self.engine.font_manager.get_font("number_font")
            mistakes_console = Console(width = font.char_width * len(mistakes_string) + 1, height = font.char_height, order="F")
            for i in range(0, len(mistakes_string)):
                start_x = i * font.char_width
                if i > 0:
                    start_x += 1
                mistakes_console.tiles_rgb[start_x:start_x+ font.char_width, 0:font.char_height] = font.get_character(mistakes_string[i])
            final_width = font.char_width * len(mistakes_string)

            final_x = self.level["mistakes_x"] + 2
            if len(mistakes_string) > 1:
                final_width += 1
                final_x -= 2
            mistakes_console.blit(console, src_x=0, src_y=0, dest_x = final_x, dest_y = self.level["mistakes_y"], width = final_width, height = font.char_height)

        if self.spotting:
            self.render_spotting_line(console)
            self.render_spotted_tiles(console)

    def render_ending(self, console):
        super().render(console)
        if self.ending_effect == None:
            self.ending_effect = VerticalWipeEffect(self.engine, self.level["x"], self.level["y"], self.level["width"], self.level["height"])

        if not self.ending_effect.in_effect:

            if self.ending_effect.time_alive > 0:
                if not self.level_ending:
                    self.level_ending = True
                    Timer(2.0, self.end_level).start()
                console.tiles_rgb[self.x : self.x + self.width, self.y: self.y + self.height] = self.tiles["graphic"]
                return

            temp_console = Console(width=self.level["width"], height=self.level["height"], order="F")
            temp_console.tiles_rgb[self.x : self.x + self.width, self.y: self.y + self.height] = self.tiles[self.level["x"]:self.level["x"]+self.level["width"], self.level["y"]:self.level["y"]+self.level["height"] ]["graphic"]

            self.ending_effect.tiles = temp_console.tiles
            self.ending_effect.start(VerticalWipeDirection.DOWN)

        elif self.ending_effect.in_effect == True:
            self.ending_effect.render(console)
   
    def render_spotting_line(self, console):
        temp_console = Console(width=console.width, height=console.height, order="F")
        
        max_tile = min(10, len(self.spotted_tiles))
        for i in range(0,max_tile):
            tile = self.spotted_tiles[i]
            temp_console.tiles_rgb[tile[0], tile[1]] = (9632, black,spot_line)
            temp_console.blit(console, src_x=tile[0], src_y=tile[1], dest_x=tile[0], dest_y=tile[1], width=1, height=1)

    def render_spotted_tiles(self, console):
        font = self.engine.font_manager.get_font("number_font")

        for i in range(0, len(self.level["spotted_tiles_x"])):
            temp_console = Console(width = font.char_width, height = font.char_height, order="F")
            temp_console.tiles_rgb[0: font.char_width, 0:font.char_height] = font.get_character(str(self.spotted_statue_tiles))

            x =self.level["spotted_tiles_x"][i] - int(font.char_width / 2)
            y =self.level["spotted_tiles_y"][i] - int(font.char_height / 2)
            temp_console.blit(console, src_x=0, src_y=0, dest_x = x, dest_y = y, width = font.char_width, height = font.char_height)
        
    def update_spotting_line(self):
    
        mouse_pos = (self.engine.mouse_location[0], self.engine.mouse_location[1])

        spotted_material_tiles = 0
        self.spotted_statue_tiles = 0
        self.spotted_tiles.clear()
        
        if self.mousedown_point is not None and mouse_pos != self.mousedown_point:

            #Figure out the normalised vector between the mouse and the button press point            
            spot_line_magnitude = sqrt((abs(mouse_pos[0]-self.mousedown_point[0])**2) + (abs(mouse_pos[1]-self.mousedown_point[1])**2))
            spot_line_normalised = ((mouse_pos[0]-self.mousedown_point[0])/spot_line_magnitude,  (mouse_pos[1]-self.mousedown_point[1])/spot_line_magnitude)

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
            self.entities = [x for x in self.entities if not isinstance(x, BlockMaterial)]
            self.remaining_blocks = 0
            self.remove_entity(None)

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

    def chisel_mistake(self):
        self.mistakes += 1
                        
    def complete_level(self):
        self.state = StatueState.ENDING 

    def end_level(self):
        self.state = StatueState.INACTIVE
        summary = StatueSummary(self.level, self.mistakes)
        LevelCompleteAction(self.engine, summary).perform()

    def add_entity(self, entity):
        if isinstance(entity, BlockMaterial):
            self.remaining_blocks += 1
        elif isinstance(entity, Anchor):
            self.anchor = entity
        self.entities.append(entity)
        self.update_graph()
    
    def remove_entity(self, entity):
        if isinstance(entity, BlockMaterial):
            self.remaining_blocks -= 1
            self.cleared_blocks += 1

        if self.remaining_blocks == 0:
            self.complete_level()

        super().remove_entity(entity)
        self.update_graph()

    def load_level(self, level):
        self.reset()

        xp_data = self.load_xp_data(level["file"])
        self.load_tiles(level["file"], xp_data)
        self.load_entities(level["file"], xp_data)
        self.level = level
        self.state = StatueState.LOAD_FOOTER

        probability_step = (self.remaining_blocks * 0.9)/len(self.level["name"])
        self.name_char_probabilites = list(map(lambda num: int(num * probability_step), range(1, len(self.level["name"]) + 1)))
        random.shuffle(self.name_char_probabilites)
        
