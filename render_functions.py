from __future__ import annotations

from typing import TYPE_CHECKING
from tcod import console

from tcod.libtcodpy import color_scale_HSV

import color

if TYPE_CHECKING:
    from tcod import Console
    from engine import Engine
    from game_map import GameMap


def get_names_at(x: int, y: int, game_map: GameMap) -> str:
    # Sanity check. If out of bounds or the tile is invisible just quit out with blank string
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return ""

    names = ", ".join(
        entity.name for entity in game_map.entities if entity.x == x and entity.y == y
    )

    return names.capitalize()


def render_bar(console: Console, current_val: int, max_val: int, total_width: int) -> None:
    bar_width = int(float(current_val) / max_val * total_width)

    console.draw_rect(x=0, y=45, width=20, height=1, ch=1, bg=color.bar_empty)

    if bar_width > 0:
        console.draw_rect(x=0, y=45, width=bar_width, height=1, ch=1, bg=color.bar_filled)

    console.print(x=1, y=45, string=f"HP: {current_val}/{max_val}", fg=color.bar_text)


def render_names_at_mouse(console: Console, x: int, y: int, engine: Engine) -> None:
    mouse_x, mouse_y = engine.mouse_location

    names_at_mouse = get_names_at(mouse_x, mouse_y, engine.game_map)

    console.print(x=x, y=y, string=names_at_mouse)
