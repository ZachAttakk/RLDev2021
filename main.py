#!/usr/bin/env python3
import copy
from input_handlers import EventHandler
from procgen import generate_dungeon
import tcod
from numpy import floor

from engine import Engine
import entity_factories


def main():
    screen_width: int = 80
    screen_height: int = 50

    map_width: int = 80
    map_height: int = 45

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    max_monsters_per_room = 2

    tileset = tcod.tileset.load_tilesheet(
        "generic_rl_fnt.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )

    event_handler = EventHandler()

    # init player
    player = copy.deepcopy(entity_factories.player)

    # init map
    game_map = generate_dungeon(
        max_rooms, room_min_size, room_max_size, max_monsters_per_room, map_width, map_height, player)

    # init engine
    engine = Engine(event_handler=event_handler,
                    game_map=game_map, player=player)

    # The context is the window that you actually see
    # The console is the internal buffer that holds the next frame of the game
    with tcod.context.new_terminal(
            screen_width, screen_height, tileset=tileset, title="RLDev2021", vsync=True,) as context:
        root_console = tcod.Console(screen_width, screen_height, order="F")

        # MAIN LOOP
        while True:
            engine.render(console=root_console, context=context)
            events = tcod.event.wait()
            engine.handle_events(events)


if __name__ == '__main__':
    main()
