from __future__ import annotations

import copy
from typing import Tuple, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from game_map import GameMap

T = TypeVar("T", bound="Entity")


class Entity:
    """Generic object to represent players, enemies, items, etc. """

    def __init__(self, x: int = 0, y: int = 0, char: str = "?", color: Tuple[int, int, int] = (255, 255, 255), name: str = "<Unnamed>", blocks_movement: bool = False,) -> None:
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement

    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        """Spawn a copy of this instance at the given location.

        Args:
            gamemap (GameMap): Map on which it goes
            x (int): X
            y (int): Y

        Returns:
            T: Reference to new entity, already added to map
        """
        clone = copy.deepcopy(self)
        clone.x, clone.y = x, y
        gamemap.entities.add(clone)
        return clone

    def move(self, dx: int, dy: int) -> Tuple[int, int]:
        """Move entity by given amount

        Args:
            dx (int): Horizontal delta
            dy (int): Vertical delta

        Returns Tuple[int,int]: New position x,y
        """
        self.x += dx
        self.y += dy

        return dx, dy
