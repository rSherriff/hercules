

import numpy as np  # type: ignore

# Tile graphics structured type compatible with Console.tiles_rgb.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B")
    ]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("walkable", bool),
        ("graphic", graphic_dt)  # Graphics for when this tile is not in FOV.
    ]
)


def new_tile(walkable, graphic) -> np.ndarray:
    return np.array((walkable, graphic), dtype=tile_dt)


background_tile = new_tile(False, (0x00, (255, 255, 255), (0, 0, 0)))
