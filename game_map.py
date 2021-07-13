from __future__ import annotations

from typing import Iterable, Iterator, Optional, TYPE_CHECKING

import numpy as np
from numpy.lib.arraysetops import isin  # type: ignore
from tcod.console import Console

from entity import Actor
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class GameMap:
    def __init__(self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()) -> None:
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities)

        # Make map full of floor
        self.tiles = np.full(
            (width, height), fill_value=tile_types.wall, order="F")

        # Tiles the player can see now
        self.visible = np.full((width, height), fill_value=False, order="F")
        # Tiles the player has seen before
        self.explored = np.full((width, height), fill_value=False, order="F")

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this map's libing actors."""
        yield from (entity
                    for entity in self.entities
                    if isinstance(entity, Actor) and entity.is_alive)

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

    def get_blocking_entity_at(self, loc_x: int, loc_y: int) -> Optional[Entity]:
        for entity in self.entities:
            if entity.blocks_movement and entity.x == loc_x and entity.y == loc_y:
                return entity

        # If we're here, it means we didn't find anything blocking
        return None

    def get_actor_at(self, loc_x: int, loc_y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == loc_x and actor.y == loc_y:
                return actor

        # If we're here, it means we didn't find any actor
        return None

    def render(self, console: Console) -> None:
        """Render the map
        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """
        # Draw walls
        console.tiles_rgb[0:self.width, 0:self.height] = np.select(condlist=[self.visible, self.explored], choicelist=[
                                                                   self.tiles["light"], self.tiles["dark"]], default=tile_types.SHROUD,)

        # Sort entities in render order

        entities_sorted = sorted(
            self.entities, key=lambda x: x.render_order.value)
        # Draw entities
        for entity in entities_sorted:
            #console.print(entity.x, entity.y, entity.char, fg=entity.color)
            # Only print entities that are in the FOV
            if self.visible[entity.x, entity.y]:
                console.print(entity.x, entity.y, entity.char, fg=entity.color)
