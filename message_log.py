from types import resolve_bases
from typing import List, Reversible, Tuple
import textwrap

import tcod
from tcod.console import Console
from tcod.libtcodpy import ConsoleBuffer

import color


class Message:
    def __init__(self, text: str, fg: Tuple[int, int, int]) -> None:
        self.plain_text = text
        self.fg = fg
        self.count = 1

    @property
    def full_text(self) -> str:
        """The full text of this message, including the count if necessary."""
        if self.count > 1:
            return f"{self.plain_text} (x{self.count})"
        else:
            return self.plain_text


class MessageLog:
    def __init__(self) -> None:
        self.messages: List[Message] = []

    def add_message(self,
                    text: str, fg: Tuple[int, int, int] = color.white,
                    *, stack: bool = True,) -> None:
        """Add a message to this log.

        Args:
            text (str): The message text
            fg (Tuple[int, int, int], optional): RGB of text color. Can use color class. Defaults to white.
            stack (bool, optional): If true, this message can stack with previous messages of the same text. Defaults to True.
        """

        # If this message is set to stack, if there's at least one message, if that last message has the same text
        # ... then we just increment the count
        if stack and self.messages and text == self.messages[-1].plain_text:
            self.messages[-1].count += 1
        else:
            self.messages.append(Message(text, fg))

    def render(self, console: Console, x: int, y: int, width: int, height: int,) -> None:
        """Render this log over the given area."""
        self.render_messages(console, x, y, width, height, self.messages)

    @staticmethod
    def render_messages(
            console: tcod.Console, x: int, y: int, width: int, height: int, messages: Reversible[Message], ) -> None:
        """Render the messages provided."""
        y_offset = height-1

        for message in reversed(messages):
            for line in reversed(textwrap.wrap(message.full_text, width)):
                console.print(x=x, y=y+y_offset, string=line, fg=message.fg)
                y_offset -= 1
                if y_offset < 0:
                    return  # no more space
