"""
Clock logic: time tracking, digit change detection, and display layout.

Manages 4 DigitAnimation instances for HH:MM display.
Converts animation state to absolute screen coordinates for rendering.
"""

from datetime import datetime
from tetris_clock.tetris_font import X_SHIFT_CLOCK, TETRIS_Y_DROP_DEFAULT
from tetris_clock.animation import DigitAnimation


class Clock:
    """Manages the tetris clock display state."""

    def __init__(self, x_origin=16, y_finish=32):
        """
        Args:
            x_origin: Left x offset on screen (default centers 31px layout on 64px display)
            y_finish: Bottom y coordinate of the digit area
        """
        self.x_origin = x_origin
        self.y_finish = y_finish
        self.y_base = y_finish - TETRIS_Y_DROP_DEFAULT

        self.digits = [DigitAnimation() for _ in range(4)]
        self.current_digits = [-1, -1, -1, -1]

    def update_time(self, now=None):
        """
        Check current time and reset animations for any changed digits.

        Args:
            now: Optional datetime for testing. Uses current time if None.
        """
        if now is None:
            now = datetime.now()

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
        blocks = []
        for i, digit_anim in enumerate(self.digits):
            x_shift = X_SHIFT_CLOCK[i]

            # Settled blocks
            for blocktype, color, x_pos, y_pos, rotation in digit_anim.get_settled_blocks():
                screen_x = self.x_origin + x_shift + x_pos
                screen_y = self.y_base + y_pos
                blocks.append((blocktype, color, screen_x, screen_y, rotation))

            # Falling block
            falling = digit_anim.get_falling_block()
            if falling:
                blocktype, color, x_pos, y_pos, rotation = falling
                screen_x = self.x_origin + x_shift + x_pos
                screen_y = self.y_base + y_pos
                blocks.append((blocktype, color, screen_x, screen_y, rotation))

        return blocks

    def get_colon_pixels(self):
        """
        Get colon pixel positions in absolute screen coordinates.

        The colon is drawn at x = origin + DISTANCE_BETWEEN_DIGITS * 2,
        as two 2x2 squares at y offsets 8 and 12.
        """
        x = self.x_origin + 14  # 7 * 2
        pixels = []
        for y_offset in [8, 12]:
            y = self.y_base + y_offset
            pixels.extend([
                (x, y), (x + 1, y),
                (x, y + 1), (x + 1, y + 1),
            ])
        return pixels
