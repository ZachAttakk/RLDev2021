from __future__ import annotations
from typing import TYPE_CHECKING

# This class needs to know that these objects exist without trying to initialise them
# Otherwise we get a circle reference
if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class Action:
    def perform(self, engine: Engine, entity: Entity) -> None:
        """Perform this action with the objects needed to determine its scope.

        Args:
            engine (Engine): The scope this action is being performed in
            entity (Entity): The object performing the action

            This method must be overridden by Action subclasses 
        """
        raise NotImplementedError()


class EscapeAction(Action):
    def perform(self, engine: Engine, entity: Entity) -> None:
        raise SystemExit()


class MovementAction(Action):
    def __init__(self, dx: int, dy: int):
        super().__init__()

        self.dx = dx
        self.dy = dy

    def perform(self, engine: Engine, entity: Entity) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        # Validate movement
        if not engine.game_map.in_bounds(dest_x, dest_y):
            return  # Destination out of bounds

        if not engine.game_map.tiles["walkable"][dest_x, dest_y]:
            return  # Destination not walkable

        # if we make it to here, it's safe to move
        entity.move(self.dx, self.dy)
