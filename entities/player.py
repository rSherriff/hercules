
from typing import Tuple

import tcod.event
from application_path import get_app_path
from playsound import playsound
from utils.color import get_random_color
from utils.direction import Direction

from entities.entity import Entity


class Player(Entity):
    def __init__(self, engine, x: int, y: int):
        self.direction = Direction.LEFT
        super().__init__(engine, x, y, chr(250), get_random_color())
        self.update_direction_char()
        

    def keydown(self, key):  
        dx,dy = 0,0 

        if key == tcod.event.K_UP or key == tcod.event.K_DOWN or key == tcod.event.K_LEFT or key == tcod.event.K_RIGHT:
            if key == tcod.event.K_UP:
                dx=0
                dy=-1
                self.direction = Direction.UP
            elif key == tcod.event.K_DOWN:
                dx=0
                dy=1
                self.direction = Direction.DOWN
            elif key == tcod.event.K_LEFT:
                dx=-1
                dy=0
                self.direction = Direction.LEFT
            elif key == tcod.event.K_RIGHT:
                dx=1
                dy=0
                self.direction = Direction.RIGHT

            dest_x = self.x + dx
            dest_y = self.y + dy

            for _, section in self.engine.get_active_sections():
                if section.tiles["walkable"][dest_x, dest_y]:
                    self.move(dx, dy)

        
        self.update_direction_char()


    def update_direction_char(self):
        if self.direction == Direction.UP:
            self.char = chr(250)
        elif self.direction == Direction.DOWN:
            self.char = chr(237)
        elif self.direction == Direction.LEFT:
            self.char = chr(243)
        elif self.direction == Direction.RIGHT:
            self.char = chr(225)
