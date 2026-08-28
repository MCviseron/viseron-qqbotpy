"""Color conversion helpers used by embed/role APIs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

__all__ = ["Color", "convert_color"]


@dataclass(frozen=True)
class Color:
    red: int
    green: int
    blue: int

    @property
    def value(self) -> int:
        return (self.red << 16) | (self.green << 8) | self.blue


def convert_color(color: Union[tuple, list, int, str]) -> int:
    """Convert an RGB tuple/list, integer, or #RRGGBB hex string to an integer.

    The integer value has red in the high byte and blue in the low byte, which
    is the representation expected by QQ channel role color fields.
    """
    if isinstance(color, int):
        return color

    if isinstance(color, (tuple, list)):
        if len(color) != 3:
            raise ValueError("RGB color must contain three components")
        red, green, blue = (int(part) for part in color)
        if not all(0 <= part <= 255 for part in (red, green, blue)):
            raise ValueError("RGB components must be between 0 and 255")
        return Color(red, green, blue).value

    if isinstance(color, str):
        text = color.strip()
        if text.startswith("#"):
            text = text[1:]
        if len(text) != 6:
            raise ValueError("hex color must be #RRGGBB or RRGGBB")
        return int(text, 16)

    raise TypeError(f"unsupported color type: {type(color)!r}")
