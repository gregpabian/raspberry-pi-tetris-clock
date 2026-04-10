"""
Piece rendering: converts blocktype + rotation to absolute pixel coordinates.
"""

from tetris_clock.tetris_font import PIECE_SHAPES


def get_pixels(blocktype, rotation, x, y, scale=1):
    """
    Get absolute pixel coordinates for a Tetris piece.

    Args:
        blocktype: Piece type (0-7)
        rotation: Rotation (0-3)
        x: Anchor x position
        y: Anchor y position (bottom of piece in Arduino coords)
        scale: Pixel scale factor (each block pixel becomes scale×scale)

    Returns:
        List of (x, y) pixel coordinates.
    """
    offsets = PIECE_SHAPES[blocktype][rotation]
    if scale == 1:
        return [(x + dx, y + dy) for dx, dy in offsets]
    pixels = []
    for dx, dy in offsets:
        bx = x + dx * scale
        by = y + dy * scale
        for sx in range(scale):
            for sy in range(scale):
                pixels.append((bx + sx, by + sy))
    return pixels
