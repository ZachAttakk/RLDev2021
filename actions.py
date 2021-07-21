from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Tuple

import color

# This class needs to know that these objects exist without trying to initialise them
# Otherwise we get a circle reference
if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity, Actor


class Action:
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to."""
        return self.entity.gamemap.engine

    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

            self.engine (Engine): The scope this action is being performed in
            self.entity (Entity): The object performing the action

            This method must be overridden by Action subclasses 
        """
        raise NotImplementedError()


class EscapeAction(Action):
    def perform(self) -> None:
        raise SystemExit()


class ActionWithDir(Action):
    def __init__(self, entity: Actor, dx: int, dy: int) -> None:
        super().__init__(entity)

        self.dx, self.dy = dx, dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        """Returns this action's destination"""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Return the blocking entity at this action's destination."""
        return self.engine.game_map.get_blocking_entity_at(*self.dest_xy)

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this action's destination."""
        return self.engine.game_map.get_actor_at(*self.dest_xy)

    def perform(self) -> None:
        # Can't just perform if we don't know what the action is for
        raise NotImplementedError()


class MeleeAction(ActionWithDir):
    def perform(self) -> None:
        target = self.target_actor

        if not target:
            return  # nothing to attack

        damage = self.entity.fighter.power - target.fighter.defense

        attack_description = f"{self.entity.name.capitalize()} attacks {target.name}"
        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk
        if damage > 0:
            self.engine.message_log.add_message(f"{attack_description} for {damage}.", attack_color)
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(
                f"{attack_description} but does no damage.", attack_color)


class MovementAction(ActionWithDir):

    def perform(self) -> None:

        # get destination space
        dest_x, dest_y = self.dest_xy

        # Validate movement
        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            return  # Destination out of bounds

        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            return  # Destination not walkable

        if self.engine.game_map.get_blocking_entity_at(dest_x, dest_y):
            return  # Entity is blocking the movement

        # if we make it to here, it's safe to move
        self.entity.move(self.dx, self.dy)


class BumpAction(ActionWithDir):
    """If there's something in the space, attack it, otherwise move there.
    Returns MeleeAction or MovementAction as appropriate."""

    def perform(self) -> None:

        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()


class WaitAction(Action):
    def perform(self) -> None:
        """THE GOGGLES! THEY DO NOTHING!"""
        pass
