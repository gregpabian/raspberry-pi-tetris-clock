/*
 * Piece rendering: converts blocktype + rotation to absolute pixel coordinates.
 */

#ifndef TETRIS_PIECES_H
#define TETRIS_PIECES_H

#include "tetris_data.h"

/*
 * Get absolute pixel coordinates for a Tetris piece.
 *
 * blocktype: Piece type (0-7)
 * rotation:  Rotation (0-3)
 * x, y:      Anchor position (y is bottom of piece)
 * scale:     Pixel scale factor (each block pixel becomes scale x scale)
 * out:       Output buffer (must hold at least 4 * scale * scale entries)
 *
 * Returns the number of pixels written.
 */
int get_pixels(int blocktype, int rotation, int x, int y, int scale,
               Pixel *out);

#endif /* TETRIS_PIECES_H */
