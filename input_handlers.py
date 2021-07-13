from __future__ import annotations
from typing import Dict, Optional, TYPE_CHECKING

import json

import tcod.event

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

    def handle_events(self) -> None:
        raise NotImplementedError()

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()


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

    def handle_events(self) -> None:
        for event in tcod.event.wait():
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

        # No valid key was pressed
        return action


class GameOverEventHandler(EventHandler):
    def handle_events(self) -> None:
        for event in tcod.event.wait():
            action = self.dispatch(event)

            if action is not None:
                action.perform()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        key = event.sym

        if key == tcod.event.K_ESCAPE:
            action = EscapeAction(self.engine.player)

        # Return action, which is either escape or nothing
        return action
