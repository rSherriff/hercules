from effects.effect import Effect

from tcod import Console
from enum import auto, Enum

class HorizontalWipeDirection(Enum):
    LEFT = auto()
    RIGHT = auto()

class HorizontalWipeEffect(Effect):
    def __init__(self, engine, x, y, width, height):
        super().__init__(engine,x,y,width,height)
        self.current_wipe_length = 0
        self.speed = 54
        self.lifespan = 2.5
        
    def start(self, direction: HorizontalWipeDirection):
        super().start()
        self.direction = direction
        self.current_wipe_length = 0
        
    def render(self, console):
        if self.time_alive > self.lifespan:
            self.stop()

        if(self.direction == HorizontalWipeDirection.LEFT):
            self.current_wipe_length -= self.speed  * self.engine.get_delta_time()
        elif(self.direction == HorizontalWipeDirection.RIGHT):
            self.current_wipe_length += self.speed  * self.engine.get_delta_time()

        temp_console = Console(width=self.width, height=self.height, order="F")

        for x in range(0,self.width):
            for y in range(0, self.height):
                temp_console.tiles_rgb[x,y] = self.tiles[x,y]

        temp_console.blit(console, src_x=int(self.current_wipe_length), src_y=0, dest_x=self.x + int(self.current_wipe_length), dest_y=self.y, width=self.width, height=self.height)

        self.time_alive += self.engine.get_delta_time()