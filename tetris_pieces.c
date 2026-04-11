/*
 * Piece rendering: converts blocktype + rotation to absolute pixel coordinates.
 */

#include "tetris_pieces.h"

int get_pixels(int blocktype, int rotation, int x, int y, int scale,
               Pixel *out)
{
    const Offset *offsets = PIECE_SHAPES[blocktype][rotation];
    int count = PIECE_PIXEL_COUNT[blocktype];
    int n = 0;

    if (scale == 1) {
        for (int i = 0; i < count; i++) {
            out[n].x = x + offsets[i].dx;
            out[n].y = y + offsets[i].dy;
            n++;
        }
    } else {
        for (int i = 0; i < count; i++) {
            int bx = x + offsets[i].dx * scale;
            int by = y + offsets[i].dy * scale;
            for (int sx = 0; sx < scale; sx++) {
                for (int sy = 0; sy < scale; sy++) {
                    out[n].x = bx + sx;
                    out[n].y = by + sy;
                    n++;
                }
            }
        }
    }

    return n;
}
