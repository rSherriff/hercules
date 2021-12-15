
from math import sqrt
from typing import final
import numpy as np
from numpy.lib.arraysetops import isin
import tcod
from entities.anchor import Anchor
from entities.blocker import Blocker
from entities.material import BlockMaterial, Material, StatueMaterial
from tcod import Console
from utils.color import spot_line, black

from sections.section import Section


class StatueSection(Section):
    def __init__(self, engine, x: int, y: int, width: int, height: int, xp_filepath: str = ""):
        self.mousedown_point = None
        self.spotting = False
        self.spotted_statue_tiles = 0
        self.max_spotted_material_tiles = 3
        self.spotted_tiles = list()
        self.remaining_blocks = 0
        self.anchor = None
        self.graph = None
        super().__init__(engine, x, y, width, height, xp_filepath=xp_filepath)      

        self.update_graph()


    def update(self):
        self.update_spotting_line()
    
    def render(self, console):
        super().render(console)

        temp_console = Console(width=console.width, height=console.height, order="F")

        temp_console.print(1,1, "Remaining Blocks: " + str(self.remaining_blocks), (255,255,255))
        temp_console.blit(console, src_x=1, src_y=1, dest_x=1, dest_y=2, width=22, height=1)

        if self.mousedown_point:
            
            temp_console.print(1,1, str(self.spotted_statue_tiles), (255,255,255))
            temp_console.blit(console, src_x=1, src_y=1, dest_x=1, dest_y=1, width=1, height=1)           

            self.render_spotting_line(console)


    def render_spotting_line(self, console):
        temp_console = Console(width=console.width, height=console.height, order="F")
        
        max_tile = min(10, len(self.spotted_tiles))
        for i in range(0,max_tile):
            tile = self.spotted_tiles[i]
            temp_console.tiles_rgb[tile[0], tile[1]] = (9632, black,spot_line)
            temp_console.blit(console, src_x=tile[0], src_y=tile[1], dest_x=tile[0], dest_y=tile[1], width=1, height=1)
        

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

        if button == 1 and not processed_entity and len(self.get_entities_at_location(self.engine.mouse_location[0], self.engine.mouse_location[1])) < 1:
            self.mousedown_point = (x,y)
            self.spotting = True
        elif button == 3:
            self.mousedown_point = None
            self.spotting = False

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
                        
    def check_first_stage_completion(self):
        for e in self.entities:
            if isinstance(e, BlockMaterial):
                return False
        return True

    def is_point_in_section(self, x,y):
        return (x >= 0) and (x < self.width) and (y >= 0) and (y < self.height)

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
        super().remove_entity(entity)
        self.update_graph()