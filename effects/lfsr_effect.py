from effects.effect import Effect
from ctypes import c_uint32
from tcod import Console

class LFSREffect(Effect):
    def __init__(self, engine, x, y, width, height):
        super().__init__(engine,x,y,width,height)
        self.current_tile = 0
        self.size = width * height
        self.tile = c_uint32(1).value

        self.temp_console = Console(width=self.width, height=self.height, order="F")
        self.processed_tiles = []
        
    def start(self):
        super().start()
        
    def render(self, console):
        feedback = 0x62B        
        feedback_this_step = -(self.tile & c_uint32(1).value) & feedback
        self.tile = (self.tile >> 1) ^ feedback_this_step

        self.time_alive += self.engine.get_delta_time()

        tile_width = self.tile % self.height
        tile_height = (self.tile - tile_width) / self.height

        self.processed_tiles.append()

        tile_tuple = (tile_width, tile_height)
        if tile_tuple not in  self.processed_tiles:
            self.processed_tiles.append((tile_tuple))
        else:
            self.stop()

        print(self.tile)

        tile_console = Console(width=1, height=1, order="F")
        for x in self.width:
            for y in self.height:
                if [x,y] not in self.processed_tiles:
                    tile_console.tiles_rgb = self.tiles[x,y]
                    tile_console.blit(self.temp_console, src_x=0, src_y=0, dest_x=x, dest_y=y, width=1, height=1)

        self.temp_console.blit(console, src_x=0, src_y=0, dest_x=0, dest_y=0, width=self.width, height=self.height)