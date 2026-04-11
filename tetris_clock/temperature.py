"""
Temperature display using Tetris-style falling blocks.

Renders temperature with integer part at full scale and fractional part
(decimal point + tenths digit + degree symbol) at scale=1.
"""

from tetris_clock.tetris_font import CHAR_WIDTHS
from tetris_clock.animation import DigitAnimation

# Character indices for extended characters
CHAR_MINUS = 10
CHAR_DEGREE = 11
CHAR_POINT = 12

# Content bounds in local (1x) coordinates (same as clock)
_CONTENT_TOP_1X = 4
_CONTENT_BOTTOM_1X = 15


class TemperatureDisplay:
    """Displays temperature using Tetris-style falling blocks."""

    def __init__(self, scale=2, display_width=64, display_height=32):
        self.scale = scale
        self.display_width = display_width
        self.display_height = display_height

        # Compute y_base for scale=2 (same formula as Clock)
        content_h = (_CONTENT_BOTTOM_1X - _CONTENT_TOP_1X + 1) * scale
        y_margin = (display_height - content_h) // 2 - 2
        self.y_base_full = y_margin - _CONTENT_TOP_1X * scale

        # y_base for scale=1 chars, baseline-aligned with scale=2
        # Bottom pixel (y_pos=15) must land at same screen row
        self.y_base_small = self.y_base_full + _CONTENT_BOTTOM_1X * (scale - 1)

        self._chars = []       # list of (char_index, char_scale)
        self._anims = []       # DigitAnimation per character
        self._x_shifts = []    # screen x offset per character
        self._active = False

    def set_temperature(self, value):
        """
        Start animation for a temperature value.

        Args:
            value: Temperature as float (e.g., 23.5, -5.2)
        """
        # Build character list with per-char scale
        chars = []
        rounded = round(value, 1)
        negative = rounded < 0
        abs_val = abs(rounded)
        integer_part = int(abs_val)
        frac_part = int(round((abs_val - integer_part) * 10))

        if negative:
            chars.append((CHAR_MINUS, self.scale))

        # Integer digits
        if integer_part == 0:
            chars.append((0, self.scale))
        else:
            digits = []
            n = integer_part
            while n > 0:
                digits.append(n % 10)
                n //= 10
            for d in reversed(digits):
                chars.append((d, self.scale))

        # Fractional part at scale=1
        chars.append((CHAR_POINT, 1))
        chars.append((frac_part, 1))

        # Degree symbol at scale=1
        chars.append((CHAR_DEGREE, 1))

        self._chars = chars

        # Compute total pixel width and x_shifts
        total_width = 0
        x_shifts = []
        for i, (char_idx, char_scale) in enumerate(chars):
            x_shifts.append(total_width)
            total_width += CHAR_WIDTHS[char_idx] * char_scale

        # Center on display
        x_origin = (self.display_width - total_width) // 2

        self._x_shifts = [x_origin + xs for xs in x_shifts]

        # Create animations
        self._anims = []
        for char_idx, _ in chars:
            anim = DigitAnimation()
            anim.reset(char_idx)
            self._anims.append(anim)

        self._active = True

    def tick(self):
        """Advance all character animations by one step."""
        for anim in self._anims:
            anim.tick()

    def is_complete(self):
        """Check if all animations have finished."""
        return all(a.is_complete() for a in self._anims)

    def get_render_blocks(self):
        """
        Get all blocks in absolute screen coordinates.

        Returns list of (blocktype, color_index, screen_x, screen_y, rotation, scale)
        tuples. The 6th element (scale) is the per-block pixel scale.
        """
        if not self._active:
            return []

        blocks = []
        for i, (char_idx, char_scale) in enumerate(self._chars):
            anim = self._anims[i]
            x_origin = self._x_shifts[i]
            y_base = self.y_base_full if char_scale == self.scale else self.y_base_small

            for blocktype, color, x_pos, y_pos, rotation in anim.get_settled_blocks():
                screen_x = x_origin + x_pos * char_scale
                screen_y = y_base + y_pos * char_scale
                blocks.append((blocktype, color, screen_x, screen_y, rotation, char_scale))

            falling = anim.get_falling_block()
            if falling:
                blocktype, color, x_pos, y_pos, rotation = falling
                screen_x = x_origin + x_pos * char_scale
                screen_y = y_base + y_pos * char_scale
                blocks.append((blocktype, color, screen_x, screen_y, rotation, char_scale))

        return blocks

