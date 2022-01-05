from effects.effect import Effect

from tcod import Console
from enum import auto, Enum

class HorizontalMoveDirection(Enum):
    LEFT = auto()
    RIGHT = auto()

class HorizontalMoveEffect(Effect):
    def __init__(self, engine, x, y, width, height):
        super().__init__(engine,x,y,width,height)
        self.current_move_length = 0
        self.speed = 5
        
    def start(self, direction: HorizontalMoveDirection):
        super().start()
        self.direction = direction
        self.current_move_length = 0
        
    def render(self, console):
        if self.current_move_length > self.width:
            self.stop()
  
        self.current_move_length += self.speed  * self.engine.get_delta_time()

        temp_console = Console(width=self.width, height=self.height, order="F")

        for x in range(0,self.width):
            for y in range(0, self.height):
                temp_console.tiles_rgb[x,y] = self.tiles[x,y]

        if self.direction == HorizontalMoveDirection.LEFT:
            temp_console.blit(console, src_x=self.width - int(self.current_move_length), src_y=0, dest_x=self.x, dest_y=self.y, width=int(self.current_move_length), height=self.height)
        elif self.direction == HorizontalMoveDirection.RIGHT:
            temp_console.blit(console, src_x=0, src_y=0, dest_x=self.x +  (self.width - int(self.current_move_length)), dest_y=self.y, width=int(self.current_move_length), height=self.height)

        self.time_alive += self.engine.get_delta_time()