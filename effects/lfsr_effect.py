from effects.effect import Effect
from ctypes import c_uint32
from tcod import Console

class LFSREffect(Effect):
    def __init__(self, engine, x, y, width, height):
        super().__init__(engine,x,y,width,height)
        self.current_tile = 0
        self.size = width * height
        self.tile = c_uint32(1).value
        self.feedback = 0x62B    

        self.temp_console = Console(width=self.width, height=self.height, order="F")
        self.processed_tiles = []
        
    def start(self):
        super().start()
        self.processed_tiles.clear()
        
    def render(self, console):

        for i in range(0, 50): 
            feedback_this_step = -(self.tile & c_uint32(1).value) & self.feedback
            self.tile = (self.tile >> 1) ^ feedback_this_step

            tile_width = self.tile % self.width
            tile_height = int((self.tile - tile_width) / self.width)

            tile_tuple = (tile_width, tile_height)

            if tile_tuple not in self.processed_tiles:
                self.processed_tiles.append(tile_tuple)
            else:
                self.stop()

        tile_console = Console(width=1, height=1, order="F")
        for x in range(0,self.width):
            for y in range(0,self.height):
                if (x,y) not in self.processed_tiles:
                    tile_console.tiles_rgb[0,0] = self.tiles[x,y]
                    tile_console.blit(console, src_x=0, src_y=0, dest_x=x, dest_y=y, width=1, height=1)





        