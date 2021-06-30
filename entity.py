from typing import Tuple


class Entity:
    """Generic object to represent players, enemies, items, etc. """

    def __init__(self, x: int, y: int, char: str, color: Tuple[int, int, int]) -> None:
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def move(self, dx: int, dy: int) -> None:
        """Move entity by given amount

        Args:
            dx (int): Horizontal delta
            dy (int): Vertical delta
        """
        self.x += dx
        self.y += dy

        # TODO: Consider returning new position just for lols
