"""
Clock logic: time tracking, digit change detection, and display layout.

Manages 4 DigitAnimation instances for HH:MM display.
Converts animation state to absolute screen coordinates for rendering.
"""

from datetime import datetime
from tetris_clock.tetris_font import X_SHIFT_CLOCK
from tetris_clock.animation import DigitAnimation

# Content bounds in local (1x) coordinates
_CONTENT_WIDTH_1X = 31   # approximate total width of HH:MM layout
_CONTENT_TOP_1X = 4      # topmost pixel y (settled block with max upward piece offset)
_CONTENT_BOTTOM_1X = 15  # bottommost pixel y (y_stop=16, settled at 15)


class Clock:
    """Manages the tetris clock display state."""

    def __init__(self, scale=1, display_width=64, display_height=32):
        """
        Args:
            scale: Pixel scale factor (each block pixel becomes scale×scale)
            display_width: Display width in pixels
            display_height: Display height in pixels
        """
        self.scale = scale

        # Center content on display
        content_w = _CONTENT_WIDTH_1X * scale
        content_h = (_CONTENT_BOTTOM_1X - _CONTENT_TOP_1X + 1) * scale
        self.x_origin = (display_width - content_w) // 2
        # y_base positions local y=0; center the content vertically
        y_margin = (display_height - content_h) // 2
        self.y_base = y_margin - _CONTENT_TOP_1X * scale

        self.digits = [DigitAnimation() for _ in range(4)]
        self.current_digits = [-1, -1, -1, -1]
        self.colon_visible = True

        # Pre-compute colon pixel coordinates (two square dots, scaled)
        x = self.x_origin + 14 * scale
        self._colon_pixel_coords = []
        for y_offset in [8, 12]:
            y = self.y_base + y_offset * scale
            for dx in range(2 * scale):
                for dy in range(2 * scale):
                    self._colon_pixel_coords.append((x + dx, y + dy))

    def update_time(self, now=None):
        """
        Check current time and reset animations for any changed digits.

        Args:
            now: Optional datetime for testing. Uses current time if None.
        """
        if now is None:
            now = datetime.now()

        self.colon_visible = now.second % 2 == 0

        h = now.hour
        m = now.minute
        new_digits = [h // 10, h % 10, m // 10, m % 10]

        for i in range(4):
            if new_digits[i] != self.current_digits[i]:
                self.digits[i].reset(new_digits[i])
                self.current_digits[i] = new_digits[i]

    def tick(self):
        """Advance all digit animations by one step."""
        for digit in self.digits:
            digit.tick()

    def is_complete(self):
        """Check if all animations have finished."""
        return all(d.is_complete() for d in self.digits)

    def get_render_blocks(self):
        """
        Get all blocks (settled + falling) in absolute screen coordinates.

        Returns list of (blocktype, color_index, screen_x, screen_y, rotation).
        """
        s = self.scale
        blocks = []
        for i, digit_anim in enumerate(self.digits):
            x_shift = X_SHIFT_CLOCK[i]

            # Settled blocks
            for blocktype, color, x_pos, y_pos, rotation in digit_anim.get_settled_blocks():
                screen_x = self.x_origin + (x_shift + x_pos) * s
                screen_y = self.y_base + y_pos * s
                blocks.append((blocktype, color, screen_x, screen_y, rotation))

            # Falling block
            falling = digit_anim.get_falling_block()
            if falling:
                blocktype, color, x_pos, y_pos, rotation = falling
                screen_x = self.x_origin + (x_shift + x_pos) * s
                screen_y = self.y_base + y_pos * s
                blocks.append((blocktype, color, screen_x, screen_y, rotation))

        return blocks

    def get_colon_pixels(self):
        """
        Get colon pixel positions in absolute screen coordinates.

        Returns pre-computed coordinates or empty list based on visibility.
        """
        if not self.colon_visible:
            return None
        return self._colon_pixel_coords
