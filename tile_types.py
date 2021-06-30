from typing import Tuple
import numpy as np  # type: ignore (not sure what this means)

# Tile graphics structured type compatible with Console.tiles_rgb.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode character codepoint
        ("fg", "3B"),  # 3 unsigned bytes, RGB
        ("bg", "3B"),  # 3 unsigned bytes, RGB
    ]
)

# Tile struct used for statically defines tile data
tile_dt = np.dtype(
    [
        ("walkable", np.bool8),  # True if this tile can be walked on
        ("transparent", np.bool8),  # True if this tile doesn't block FOV
        ("dark", graphic_dt),  # What the tile looks like outside FOV
    ]
)


def new_tile(*, walkable: int, transparent: int, dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],) -> np.ndarray:
    return np.array((walkable, transparent, dark), dtype=tile_dt)


# Tile factory

floor = new_tile(walkable=True, transparent=True, dark=(
    ord(" "), (255, 255, 255), (50, 50, 150)),)
wall = new_tile(walkable=False, transparent=False, dark=(
    ord(" "), (255, 255, 255), (0, 0, 100)),)
