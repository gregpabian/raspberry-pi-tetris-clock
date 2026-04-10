"""
Piece rendering: converts blocktype + rotation to absolute pixel coordinates.
"""

from tetris_clock.tetris_font import PIECE_SHAPES


def get_pixels(blocktype, rotation, x, y):
    """
    Get absolute pixel coordinates for a Tetris piece.

    Args:
        blocktype: Piece type (0-7)
        rotation: Rotation (0-3)
        x: Anchor x position
        y: Anchor y position (bottom of piece in Arduino coords)

    Returns:
        List of (x, y) pixel coordinates.
    """
    offsets = PIECE_SHAPES[blocktype][rotation]
    return [(x + dx, y + dy) for dx, dy in offsets]
