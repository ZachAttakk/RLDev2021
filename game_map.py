import numpy as np  # type: ignore
from tcod.console import Console

import tile_types


class GameMap:
    def __init__(self, width: int, height: int) -> None:
        self.width, self.height = width, height

        # Make map full of floor
        self.tiles = np.full(
            (width, height), fill_value=tile_types.wall, order="F")

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside the bounds of the map.
            Doesn't check for collision. Only extremes.

        Args:
            x (int): Horizontal position
            y (int): Vertical position

        Returns:
            bool: True if x,y is inside the map.
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        console.tiles_rgb[0:self.width, 0:self.height] = self.tiles["dark"]
