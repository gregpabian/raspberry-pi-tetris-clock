/*
 * Display abstraction: renders animation state to either an LED matrix or PNG files.
 */

#ifndef TETRIS_RENDER_H
#define TETRIS_RENDER_H

#include "tetris_clock.h"
#include "tetris_pieces.h"

#define DISPLAY_WIDTH  64
#define DISPLAY_HEIGHT 32

#ifdef TEST_MODE

/* Test renderer: writes PNG frames */
typedef struct {
    char output_dir[256];
    int png_scale;
    int frame_num;
    uint8_t framebuf[DISPLAY_HEIGHT][DISPLAY_WIDTH][3];
} Renderer;

void renderer_init_test(Renderer *r, const char *output_dir, int png_scale);

#else

/* Matrix renderer: drives LED matrix via rpi-rgb-led-matrix C API */
#include <led-matrix-c.h>

typedef struct {
    struct RGBLedMatrix *matrix;
    struct LedCanvas *canvas;
} Renderer;

void renderer_init_matrix(Renderer *r, struct RGBLedMatrix *matrix);

#endif /* TEST_MODE */

/* Render one frame */
void renderer_render_frame(Renderer *r,
                           const RenderBlock *blocks, int block_count,
                           const Pixel *colon_pixels, int colon_count,
                           int scale);

/* Cleanup resources */
void renderer_cleanup(Renderer *r);

#endif /* TETRIS_RENDER_H */
