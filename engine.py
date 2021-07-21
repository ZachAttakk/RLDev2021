from __future__ import annotations
from config import Config
from render_functions import render_bar, render_names_at_mouse
from message_log import MessageLog
from typing import Tuple, TYPE_CHECKING

from game_map import GameMap

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
        self.config = Config()
        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.message_log = MessageLog()
        self.mouse_location: Tuple[int, int] = 0, 0
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

    def render(self, console: Console) -> None:
        # Draw map
        self.game_map.render(console)

        # Draw User Interface
        render_bar(console=console, current_val=self.player.fighter.hp,
                   max_val=self.player.fighter.max_hp, total_width=20,)

        render_names_at_mouse(console=console, x=21, y=44, engine=self)

        # Draw message log
        self.message_log.render(console, x=21, y=45, width=40, height=5)
