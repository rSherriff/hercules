from effects.effect import Effect

from tcod import Console
from enum import auto, Enum

class VerticalWipeDirection(Enum):
    UP = auto()
    DOWN = auto()

class VerticalWipeEffect(Effect):
    def __init__(self, engine, x, y, width, height, speed = 6, border_tile = None):
        super().__init__(engine,x,y,width,height)
        self.current_wipe_height = 0
        self.speed = speed
        self.border_tile = border_tile
        
    def start(self, direction: VerticalWipeDirection):
        super().start()
        self.direction = direction
        self.current_wipe_height = 0
        
    def render(self, console):
        
        if self.current_wipe_height > self.height:
            self.stop()
            
        self.current_wipe_height += self.speed * self.engine.get_delta_time()

        temp_console = Console(width=self.width, height=self.height, order="F")

        for x in range(0, self.width):
            for y in range(0, self.height):
                temp_console.tiles_rgb[x,y] = self.tiles[x,y]

        if not self.border_tile == None:
            for i in range(0,self.width):
                temp_console.tiles_rgb[i, min(self.height,int(self.current_wipe_height -1))] = self.border_tile
                

        if(self.direction == VerticalWipeDirection.UP):
            temp_console.blit(console, src_x=0, src_y=0, dest_x=self.x, dest_y=self.y + self.height -  int(self.current_wipe_height), width=self.width, height=max(int(self.current_wipe_height),1))
        elif(self.direction == VerticalWipeDirection.DOWN):
            temp_console.blit(console, src_x=0, src_y=0, dest_x=self.x, dest_y=self.y, width=self.width, height=max(int(self.current_wipe_height),1))

        self.time_alive += self.engine.get_delta_time()