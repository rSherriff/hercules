
from threading import Timer
from typing import List, Tuple

import tcod
from actions.actions import (AddEntity, BlockMaterialChisled, DeleteEntity,
                             StatueMaterialChiseled)
from utils.color import marble, marble_highlight, marble_marked, black

from entities.blocker import Blocker
from entities.entity import Entity


class Material(Entity):
    def __init__(self, engine, x: int, y: int,  section):
        super().__init__(engine, x, y, chr(9632), marble, marble_highlight)
        self.section = section
        self.stress = 0
        self.max_stress = 75
        self.pickable = False
        self.marked = False
        self.blocks_movement = True
        self.terminators = []
        for i in range(12,27):
            self.terminators.append([i,24,((abs(self.x - i) + abs(self.y - 24)))])

        self.terminators.sort(key=lambda x:x[2])
        
    def update(self):
        self.get_path_to_terminator()

        if self.stress > self.max_stress:
            self.chisel_material()
        
    def late_update(self):
        self.stress = 0

    def mousedown(self, button):
        if button == 1:
            if self.pickable and self.is_path_to_anchor():
                self.chisel_material()
        elif button == 3:
            self.mark()

    def chisel_material(self):
        pass

    def is_path_to_anchor(self):
        if self.section.graph is None or self.section.anchor is None:
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

    def mark(self):
        self.marked = not self.marked 
        if self.marked:
            self.fg_color = marble_marked
        else:
            self.fg_color = marble

class StatueMaterial(Material):
    def __init__(self, engine, x: int, y: int, section):
        super().__init__(engine, x, y, section)
        self.pickable = False

    def mousedown(self, button):
        if button == 3:
            self.chisel_material()
    
    def chisel_material(self):
        super().chisel_material()
        self.fg_color = marble
        self.bg_color = black
        self.char = chr(236)
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
        action = BlockMaterialChisled(self.engine, self)
        Timer(0.1, action.perform).start()


