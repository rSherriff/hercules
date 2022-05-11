import gzip

import numpy as np
import xp_loader
from tile_types import background_tile

def load_tiles(filepath, width, height):
    tiles =  np.full((width, height), fill_value=background_tile, order="F")
    if filepath:
        xp_file = gzip.open("images/" + filepath)
        raw_data = xp_file.read()
        xp_file.close()
        xp_data = xp_loader.load_xp_string(raw_data)
    if xp_data is not None:
        for h in range(0, height):
            if h < xp_data['height']:
                for w in range(0, width):
                    if w < xp_data['width']:
                        tiles[w, h]['walkable'] = True
                        tiles[w, h]['graphic'] = xp_data['layer_data'][0]['cells'][w][h]
                    else:
                        break
            else:
                break
    return tiles

util_tiles = load_tiles("utils.xp", 60,60)
    