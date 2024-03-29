
from threading import Timer
from typing import List, Tuple
from enum import Enum, auto

import tcod
from actions.actions import (AddEntity, BlockMaterialChiseled, ChiselMistakeAction, DeleteEntity,
                             StatueMaterialChiseled)
from utils.color import marble, marble_highlight, black, mistake

from entities.blocker import Blocker
from entities.entity import Entity

class LeftClickAction(Enum):
    CARVE = auto()
    CHISEL = auto()


class Material(Entity):
    def __init__(self, engine, x: int, y: int,  section):
        super().__init__(engine, x, y, chr(9632), marble, marble_highlight)
        self.section = section
        self.stress = 0
        self.max_stress = 75
        self.pickable = False
        self.blocks_movement = True
        self.terminators = []
        self.initial_bg = marble
        self.initial_fg = marble_highlight
        self.dying = False
        for i in range(12,27):
            self.terminators.append([i,24,((abs(self.x - i) + abs(self.y - 24)))])

        self.terminators.sort(key=lambda x:x[2])

        self.leftClickAction = LeftClickAction.CHISEL
        
    def update(self):
        self.get_path_to_terminator()

        if self.stress > self.max_stress:
            self.chisel_material()
        
    def late_update(self):
        self.stress = 0

    def chisel_material(self):
        pass

    def is_path_to_anchor(self):
        if self.section.graph is None or self.section.anchor is None:
            print("Trying to find path but no anchor set!")
            return False

        pathfinder = tcod.path.Pathfinder(self.section.graph)

        pathfinder.add_root((self.x, self.y))
        path: List[List[int]] = pathfinder.path_to((self.section.anchor.x, self.section.anchor.y)).tolist()
        return len(path) > 1

    def get_path_to_terminator(self) -> List[Tuple[int, int]]:
        """Compute and return a path to the target position.
        If there is no valid path then returns an empty list.
        """
        if not self.section.graph:
            return 

        pathfinder = tcod.path.Pathfinder(self.section.graph)

        pathfinder.add_root((self.x, self.y))  # Start position.

        # Compute the path to the destination and remove the starting point.
        last_path = list()
        for t in self.terminators:
            dest_x = t[0]
            dest_y = t[1]

            if dest_x == self.x and dest_y == self.y:
                continue

            path: List[List[int]] = pathfinder.path_to((dest_x, dest_y)).tolist()
            if len(path) > 1 and (len(path) < len(last_path) or len(last_path) == 0 ):
                last_path = path

        if len(last_path) > 1:
            for index in last_path:
                for entity in self.engine.get_entities_at_location(index[0],index[1]):
                    if isinstance(entity, Material):
                        entity.stress += 1
        else:
            self.chisel_material()
    
    def chisel_mistake(self):
        if not self.dying:
            self.fg_color = mistake
            self.bg_color = black
            self.char = chr(ord('X'))
            ChiselMistakeAction(self.engine,self).perform()
            Timer(0.3, self.reset_tile).start()
    
    def reset_tile(self):
        self.fg_color = self.initial_fg
        self.bg_color = self.initial_bg
        self.char =chr(9632)

    def set_initial_colors(self, initial_bg, initial_fg):
        self.bg_color = initial_bg
        self.fg_color = initial_fg

        self.initial_bg = initial_bg
        self.initial_fg = initial_fg


class StatueMaterial(Material):
    def __init__(self, engine, x: int, y: int, section):
        super().__init__(engine, x, y, section)
        self.pickable = True

    def mousedown(self, button):
        if self.is_path_to_anchor():
            if button == 1:
                if self.leftClickAction == LeftClickAction.CARVE:
                    self.chisel_mistake()
                else:
                    self.chisel_material()
            elif button == 3:
                if self.leftClickAction == LeftClickAction.CARVE:
                    self.chisel_material()
                else:
                    self.chisel_mistake()
    
    def chisel_material(self):
        super().chisel_material()
        self.fg_color = marble
        self.bg_color = black
        self.char = chr(236)
        self.dying = True
        action = StatueMaterialChiseled(self.engine, self)
        Timer(0.1, action.perform).start()


class BlockMaterial(Material):
    def __init__(self, engine, x: int, y: int, section):
        super().__init__(engine, x, y, section)
        self.pickable = True

    def chisel_material(self):
        super().chisel_material()
        self.fg_color = marble
        self.bg_color = black
        self.char = chr(236)
        self.dying = True
        action = BlockMaterialChiseled(self.engine, self)
        Timer(0.1, action.perform).start()

    def mousedown(self, button):
        if self.is_path_to_anchor():
            if button == 1:
                if self.leftClickAction == LeftClickAction.CARVE:
                    self.chisel_material()
                else:
                    self.chisel_mistake()
            elif button == 3:
                if self.leftClickAction == LeftClickAction.CARVE:
                    self.chisel_mistake()
                else:
                    self.chisel_material()

    


