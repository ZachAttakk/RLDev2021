from game_map import GameMap
from typing import Set, Iterable, Any

from tcod.context import Context
from tcod.console import Console

from entity import Entity
from game_map import GameMap
from input_handlers import EventHandler


class Engine:
    """go brrrrrr"""

    def __init__(self, entities: Set[Entity], event_handler: EventHandler, game_map: GameMap, player: Entity) -> None:
        self.entities = entities
        self.event_handler = event_handler
        self.game_map = game_map
        self.player = player

    def handle_events(self, events: Iterable[Any]) -> None:
        for event in events:
            action = self.event_handler.dispatch(event)

            if action is not None:
                # It's me doing the action because we're responding to events
                action.perform(self, self.player)

    def render(self, console: Console, context: Context) -> None:
        # Draw map
        self.game_map.render(console)

        # Dray entities
        for entity in self.entities:
            console.print(entity.x, entity.y, entity.char, fg=entity.color)

        # dump the console (buffer) to the screen (context)
        context.present(console)
        # clear the console so the next frame starts on a blank screen
        console.clear()
