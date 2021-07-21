#!/usr/bin/env python3
import copy

from tcod import console
from procgen import generate_dungeon
import tcod

from engine import Engine
import entity_factories
import color


def main():
    screen_width: int = 80
    screen_height: int = 50

    map_width: int = 80
    map_height: int = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    max_monsters_per_room = 2

    tileset = tcod.tileset.load_tilesheet(
        "generic_rl_fnt.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )

    # init player
    player = copy.deepcopy(entity_factories.player)

    # init engine
    engine = Engine(player=player)

    # init map
    engine.game_map = generate_dungeon(
        max_rooms, room_min_size, room_max_size, max_monsters_per_room, map_width, map_height, engine=engine)

    engine.update_fov()

    # Welcome message!
    engine.message_log.add_message(
        "Hello and welcome to yet another dungeon!", color.welcome_text)

    # The context is the window that you actually see
    # The console is the internal buffer that holds the next frame of the game
    with tcod.context.new_terminal(
            screen_width, screen_height, tileset=tileset, title="RLDev2021", vsync=True,) as context:
        root_console = tcod.Console(screen_width, screen_height, order="F")

        # MAIN LOOP
        while True:
            root_console.clear()
            engine.event_handler.on_render(console=root_console)
            context.present(root_console)

            engine.event_handler.handle_events(context)


if __name__ == '__main__':
    main()
