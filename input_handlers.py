from __future__ import annotations
from typing import Dict, Optional, TYPE_CHECKING

import tcod

from actions import *

if TYPE_CHECKING:
    from engine import Engine


class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.read_keys(engine.config.configs)

    def read_keys(self, keys: Dict):
        """Read and process keys that should be recognised for inputs"""
        pass

    def handle_events(self, context: tcod.context.Context) -> None:
        for event in tcod.event.wait():
            context.convert_event(event)
            self.dispatch(event)

    def ev_mousemotion(self, event: "tcod.event.MouseMotion") -> None:
        if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
            self.engine.mouse_location = event.tile.x, event.tile.y

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

    def on_render(self, console: tcod.Console) -> None:
        self.engine.render(console)


class MainGameEventHandler(EventHandler):

    def read_keys(self, keys: Dict):
        # For main game we need to read move keys and wait keys
        self.MOVE_KEYS = {}
        for k in keys["MOVE_KEYS"]:
            if hasattr(tcod.event, k):
                keysym = getattr(tcod.event, k)
                keyvalue = tuple(keys["MOVE_KEYS"][k])
                self.MOVE_KEYS[keysym] = keyvalue
        self.WAIT_KEYS = []
        for k in keys["WAIT_KEYS"]:
            if hasattr(tcod.event, k):
                keysym = getattr(tcod.event, k)
                self.WAIT_KEYS.append(keysym)

    def handle_events(self, context: tcod.context.Context) -> None:
        for event in tcod.event.wait():
            context.convert_event(event)
            action = self.dispatch(event)

            if action is not None:
                # It's me doing the action because we're responding to events
                action.perform()
                # Let the enemies act
                self.engine.handle_enemy_turns()
                # Update FOV in case something changed
                self.engine.update_fov()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        key = event.sym
        player = self.engine.player

        if key in self.MOVE_KEYS:
            dx, dy = self.MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        elif key in self.WAIT_KEYS:
            action = WaitAction(player)

        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction(player)
        elif key == tcod.event.K_v:
            self.engine.event_handler = HistoryViewer(self.engine)
        # No valid key was pressed
        return action


class GameOverEventHandler(EventHandler):

    def handle_events(self, context: tcod.context.Context) -> None:
        for event in tcod.event.wait():
            context.convert_event(event)
            action = self.dispatch(event)

            if action is not None:
                action.perform()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        key = event.sym

        if key == tcod.event.K_ESCAPE:
            action = EscapeAction(self.engine.player)
        elif key == tcod.event.K_v:
            self.engine.event_handler = HistoryViewer(self.engine)
        # Return action, which is either escape or nothing
        return action


class HistoryViewer(EventHandler):
    """Navigate the message history"""

    def __init__(self, engine: Engine) -> None:
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def read_keys(self, keys: Dict):
        # For game over we need to scroll the message log
        self.CURSOR_Y_KEYS = {}
        for k in keys["CURSOR_Y_KEYS"]:
            if hasattr(tcod.event, k):
                keysym = getattr(tcod.event, k)
                keyvalue = int(keys["CURSOR_Y_KEYS"][k])
                self.CURSOR_Y_KEYS[keysym] = keyvalue

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)  # Draw main state first

        log_console = tcod.Console(console.width-6, console.height-6)

        # Draw a frame with a custom banner title
        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(0, 0, log_console.width, 1,
                              "┤Message history├", alignment=tcod.CENTER)

        # Render the message log using the cursor parameter
        self.engine.message_log.render_messages(log_console, 1, 1,
                                                log_console.width-2, log_console.height-2,
                                                self.engine.message_log.messages[:self.cursor+1]
                                                )
        log_console.blit(console, 3, 3)

    def ev_keydown(self, event: "tcod.event.KeyDown") -> None:
        if event.sym in self.CURSOR_Y_KEYS:
            adjust = self.CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge
                #self.cursor = self.log_length - 1
                return
                # Removed because I don't like wrapped scrolling
            elif adjust > 0 and self.cursor == self.log_length - 1:
                #self.cursor = 0
                return
                # Removed because I don't like wrapped scrolling
            else:
                # Move while stayin gclamped to the bounds of the history log
                self.cursor = max(0, min(self.cursor + adjust, self.log_length-1))
        else:  # Any other key moves back to the main game state.
            if self.engine.player.is_alive:
                self.engine.event_handler = MainGameEventHandler(self.engine)
            else:
                self.engine.event_handler = GameOverEventHandler(self.engine)
