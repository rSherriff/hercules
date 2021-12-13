
import numpy as np
import xp_loader
import gzip
import tile_types
import os


class Image():
    def __init__(self, width, height, xp_filepath):
        self.tiles = np.full((width, height),fill_value=tile_types.background_tile, order="F")
        if os.path.isfile(xp_filepath):
            xp_file = gzip.open(xp_filepath)
            raw_data = xp_file.read()
            xp_file.close()

            xp_data = xp_loader.load_xp_string(raw_data)

            for h in range(0, height):
                if h < xp_data['height']:
                    for w in range(0, width):
                        if w < xp_data['width']:
                            self.tiles[w, h]['graphic'] = xp_data['layer_data'][0]['cells'][w][h]
                        else:
                            break
                else:
                    break
        else:
            print("Tried to load \"" + xp_filepath + "\" but it doesn't exist!")