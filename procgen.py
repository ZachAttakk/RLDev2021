from __future__ import annotations

from typing import Iterator, TYPE_CHECKING, Tuple, List
import random

import tcod

from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from entity import Entity


class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.x1, self.y1 = x, y
        self.x2, self.y2 = x+width, y+width

    @property
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1+self.x2)/2)
        center_y = int((self.y1+self.y2)/2)
        return (center_x, center_y)

    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index. Doesn't include the actual values, just where to slice them"""
        return slice(self.x1+1, self.x2), slice(self.y1+1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        return(self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1)


def generate_dungeon(max_rooms: int, room_min_size: int, room_max_size: int, map_width: int, map_height: int, player: Entity) -> GameMap:
    dungeon = GameMap(map_width, map_height)

    rooms: List[RectangularRoom] = []

    for r in range(max_rooms):

        # new room parameters
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)
        x = random.randint(0, dungeon.width-room_width-1)
        y = random.randint(0, dungeon.height-room_height-1)
        new_room = RectangularRoom(x, y, room_width, room_height)

        # Check whether they intersect existing rooms
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue

        # If the above didn't continue then we can add the room
        dungeon.tiles[new_room.inner] = tile_types.floor

        if len(rooms) == 0:
            # First room is where the player starts
            player.x, player.y = new_room.center
        else:
            # room needs a tunnel
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor

        # add the new room to the list
        rooms.append(new_room)

    return dungeon


def tunnel_between(start: Tuple[int, int], end: Tuple[int, int]) -> Iterator[Tuple[int, int]]:
    """Return an L-shaped tunnel between these two points.

    Args:
        start (Tuple[int, int]): x,y for start of tunnel
        end (Tuple[int, int]): x,y for end of tunnel

    Yields:
        Iterator[Tuple[int, int]]: Iterator with coordinates that, if followed, goes from start to end
    """

    x1, y1 = start
    x2, y2 = end
    if random.random() < 0.5:  # 50% chance
        # Horizontal then vertical
        corner_x, corner_y = x2, y1
    else:
        # Vertical then horizontal
        corner_x, corner_y = x1, y2

    # Generate the coordinates between start and end via corner
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y
