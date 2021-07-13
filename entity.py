from __future__ import annotations

import copy
from typing import Tuple, TypeVar, Type, Optional, TYPE_CHECKING

from render_order import RenderOrder

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.fighter import Fighter
    from game_map import GameMap

T = TypeVar("T", bound="Entity")


class Entity:
    """Generic object to represent players, enemies, items, etc. """

    gamemap: GameMap

    def __init__(self, gamemap: Optional[GameMap] = None, x: int = 0, y: int = 0, char: str = "?", color: Tuple[int, int, int] = (255, 255, 255), name: str = "<Unnamed>", blocks_movement: bool = False, render_order: RenderOrder = RenderOrder.CORPSE,) -> None:
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order

        # gamemap is options
        if gamemap:
            self.gamemap = gamemap
            gamemap.entities.add(self)

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
        clone.gamemap = gamemap
        gamemap.entities.add(clone)
        return clone

    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
        """Place this entity at a location

        Args:
            x (int): Horizontal position
            y (int): Vertical position
            gamemap (GameMap, optional): Reference to the game map. Defaults to None.
        """
        self.x, self.y = x, y
        if gamemap:
            # check whether the entity already has a gamemap that it belongs to
            if hasattr(self, "gamemap"):
                self.gamemap.entities.remove(self)
            self.gamemap = gamemap
            gamemap.entities.add(self)

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


class Actor(Entity):
    def __init__(self, *, x: int = 0, y: int = 0, char: str = "?", color: Tuple[int, int, int] = (255, 255, 255), name: str = "<Unnamed>", ai_cls: Type[BaseAI], fighter: Fighter) -> None:
        super().__init__(x=x, y=y, char=char, color=color, name=name,
                         blocks_movement=True, render_order=RenderOrder.ACTOR)

        self.ai: Optional[BaseAI] = ai_cls(self)

        self.fighter = fighter
        self.fighter.entity = self

    @property
    def is_alive(self) -> bool:
        """Returns Trie as long as this actor can perform actions."""
        return bool(self.ai)
