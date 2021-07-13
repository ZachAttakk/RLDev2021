from __future__ import annotations

from typing import Iterator, TYPE_CHECKING, Tuple, List
import random

import tcod

import entity_factories
from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from engine import Engine


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


def generate_dungeon(max_rooms: int, room_min_size: int, room_max_size: int, max_monsters_per_room: int, map_width: int, map_height: int, engine: Engine) -> GameMap:
    """We make it a dungeon of rectangular rooms connected by paths

    Args:
        max_rooms (int): Max number of rooms to generate
        room_min_size (int): Smallest room in either dimension
        room_max_size (int): Largest room in either dimension
        max_monsters_per_room (int): Max number of monsters per room
        map_width (int): Map how big X
        map_height (int): Map how big Y
        engine (Engine): Reference to engine for map to use

    Returns:
        GameMap: Game map containing rooms and the player
    """

    # Grab player reference from engine
    player = engine.player

    # Init map
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

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
            player.place(*new_room.center, dungeon)
        else:
            # room needs a tunnel
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor

        # Make the baddies
        place_entities(new_room, dungeon, max_monsters_per_room)

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


def place_entities(room: RectangularRoom, dungeon: GameMap, maximum_monsters: int,) -> None:
    number_of_monsters = random.randint(0, maximum_monsters)

    for i in range(number_of_monsters):
        x = random.randint(room.x1+1, room.x2-1)
        y = random.randint(room.y1+1, room.y2-1)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            # TODO:Magic number probability of Troll
            if random.random() < 0.8:
                entity_factories.orc.spawn(dungeon, x, y)
            else:
                entity_factories.troll.spawn(dungeon, x, y)
