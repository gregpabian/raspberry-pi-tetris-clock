"""
Per-digit animation state machine.

Manages the sequential falling of Tetris blocks that compose a digit.
"""

from tetris_clock.tetris_font import ALL_CHAR_BLOCKS


def _get_rotation(num_rot, fallindex, y_stop):
    """
    Calculate current rotation during fall based on progress.

    Blocks rotate progressively as they fall:
    - num_rot=1: switch at y_stop/2
    - num_rot=2: switch at y_stop/3 intervals
    - num_rot=3: switch at y_stop/4 intervals
    """
    if num_rot == 0:
        return 0

    if num_rot == 1:
        if fallindex < y_stop // 2:
            return 0
        return 1

    if num_rot == 2:
        if fallindex < y_stop // 3:
            return 0
        if fallindex < y_stop // 3 * 2:
            return 1
        return 2

    # num_rot == 3
    if fallindex < y_stop // 4:
        return 0
    if fallindex < y_stop // 4 * 2:
        return 1
    if fallindex < y_stop // 4 * 3:
        return 2
    return 3


class DigitAnimation:
    """Animation state for a single digit position."""

    def __init__(self):
        self.digit = -1  # -1 means nothing to draw
        self.blockindex = 0
        self.fallindex = 0

    def reset(self, new_digit):
        """Start animation for a new digit."""
        self.digit = new_digit
        self.blockindex = 0
        self.fallindex = 0

    def is_complete(self):
        """Check if all blocks have finished falling."""
        if self.digit not in ALL_CHAR_BLOCKS:
            return True
        return self.blockindex >= len(ALL_CHAR_BLOCKS[self.digit])

    def tick(self):
        """Advance animation by one step."""
        if self.is_complete():
            return

        blocks = ALL_CHAR_BLOCKS[self.digit]
        current = blocks[self.blockindex]
        y_stop = current[3]

        self.fallindex += 1
        if self.fallindex > y_stop:
            self.fallindex = 0
            self.blockindex += 1

    def get_settled_blocks(self):
        """
        Get all blocks that have finished falling.

        Returns list of (blocktype, color_index, x_pos, y_pos, rotation)
        where y_pos = y_stop - 1 (final resting position).
        """
        if self.digit not in ALL_CHAR_BLOCKS:
            return []

        result = []
        blocks = ALL_CHAR_BLOCKS[self.digit]
        for i in range(min(self.blockindex, len(blocks))):
            blocktype, color, x_pos, y_stop, num_rot = blocks[i]
            result.append((blocktype, color, x_pos, y_stop - 1, num_rot))
        return result

    def get_falling_block(self):
        """
        Get the currently falling block.

        Returns (blocktype, color_index, x_pos, y_pos, rotation) or None.
        y_pos is the current fall position (fallindex - 1).
        Rotation is interpolated based on fall progress.
        """
        if self.is_complete():
            return None

        blocks = ALL_CHAR_BLOCKS[self.digit]
        blocktype, color, x_pos, y_stop, num_rot = blocks[self.blockindex]
        rotation = _get_rotation(num_rot, self.fallindex, y_stop)
        y_pos = self.fallindex - 1
        return (blocktype, color, x_pos, y_pos, rotation)
