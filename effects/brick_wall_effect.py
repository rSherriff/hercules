from effects.effect import Effect

from tcod import Console
from enum import auto, Enum

class BrickWallDirection(Enum):
    DOWN = auto()
    UP = auto()

class BrickWallEffect(Effect):
    def __init__(self, engine, x, y, width, height):
        super().__init__(engine,x,y,width,height)
        self.speed = 100
        self.index_into_render = 0
        
    def start(self, direction: BrickWallDirection):
        super().start()
        self.direction = direction
        
    def render(self, console):
        if self.index_into_render >= self.width * self.height:
            self.stop()
            pass

        temp_console = Console(width=self.width, height=self.height, order="F")

        count = 0

        if self.direction == BrickWallDirection.UP:
            step = -1
            height_start = self.height - 1
            width_start = self.width - 1
            height_end = width_end = -1
        elif self.direction == BrickWallDirection.DOWN:
            step = 1
            height_start = width_start = 0
            height_end = self.height
            width_end = self.width


        for h in range(height_start, height_end, step):
            for w in range(width_start, width_end, step):

                if count >= self.index_into_render:
                    break
                    
                temp_console.tiles_rgb[w,h] = self.tiles[w,h]
                count += 1

        self.index_into_render  += self.speed * self.engine.get_delta_time()

        temp_console.blit(console, src_x=0, src_y=0, dest_x=self.x, dest_y=self.y, width=self.width, height=self.height)

        self.time_alive += self.engine.get_delta_time()