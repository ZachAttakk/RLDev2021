from __future__ import annotations
from typing import TYPE_CHECKING

from game_map import GameMap

from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov


from input_handlers import EventHandler, MainGameEventHandler

if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap


class Engine:
    """go brrrrrr"""
    game_map: GameMap

    def __init__(self, player: Actor) -> None:
        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.player = player

    def handle_enemy_turns(self) -> None:
        # All entities in list except player
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                entity.ai.perform()

    def update_fov(self) -> None:
        """Recompute the visible area based on the player's point of view.
        """

        # TODO: Magic number: Visible radius
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"], (self.player.x, self.player.y), radius=8)

        # If it's in that result, it needs to be added to "explored"
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console, context: Context) -> None:
        # Draw map
        self.game_map.render(console)

        # Draw User Interface
        console.print(
            x=1, y=47,
            string=f"{self.player.fighter.hp}/{self.player.fighter.max_hp}",)

        # dump the console (buffer) to the screen (context)
        context.present(console)
        # clear the console so the next frame starts on a blank screen
        console.clear()
