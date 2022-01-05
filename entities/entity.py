from typing import Tuple


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(self, engine, x: int, y: int, char: str, fg_color: Tuple[int, int, int], bg_color: Tuple[int, int, int]):
        self.engine = engine
        self.x = x
        self.y = y
        self.char = char
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.blocks_movement = False
        self.invisible = False

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        self.x += dx
        self.y += dy

    def update(self):
        pass

    def late_update(self):
        pass
    
    def keydown(self, key):
        pass

    def mousedown(self, button):
        pass