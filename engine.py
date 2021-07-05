from game_map import GameMap
from typing import Iterable, Any

from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

from entity import Entity
from game_map import GameMap
from input_handlers import EventHandler


class Engine:
    """go brrrrrr"""

    def __init__(self, event_handler: EventHandler, game_map: GameMap, player: Entity) -> None:
        self.event_handler = event_handler
        self.game_map = game_map
        self.player = player
        self.update_fov()

    def handle_events(self, events: Iterable[Any]) -> None:
        for event in events:
            action = self.event_handler.dispatch(event)

            if action is not None:
                # It's me doing the action because we're responding to events
                action.perform(self, self.player)
                # Let the enemies act
                self.handle_enemy_turns()
                # Update FOV in case something changed
                self.update_fov()

    def handle_enemy_turns(self) -> None:
        for entity in self.game_map.entities - {self.player}:  # All entities in list except player
            print(f"The {entity.name} waits.")

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

        # dump the console (buffer) to the screen (context)
        context.present(console)
        # clear the console so the next frame starts on a blank screen
        console.clear()
