/*
 * Clock logic: time tracking, digit change detection, and display layout.
 *
 * Manages 4 DigitAnimation instances for HH:MM display.
 * Converts animation state to absolute screen coordinates for rendering.
 */

#ifndef TETRIS_CLOCK_H
#define TETRIS_CLOCK_H

#include "tetris_anim.h"

#define NUM_DIGITS 4
/* Upper bound: 4 digits x (13 settled + 1 falling) = 56 blocks */
#define MAX_RENDER_BLOCKS 64
/* Max colon pixels: 2 dots x (2*scale)^2, at scale=2 = 32 pixels */
#define MAX_COLON_PIXELS 128

/* Block in absolute screen coordinates, ready for rendering */
typedef struct {
    int blocktype;
    int color;
    int screen_x;
    int screen_y;
    int rotation;
} RenderBlock;

/* Full clock state */
typedef struct {
    int scale;
    int x_origin;
    int y_base;
    DigitAnim digits[NUM_DIGITS];
    int current_digits[NUM_DIGITS];
    int colon_visible;
    /* Pre-computed colon pixel coordinates */
    Pixel colon_pixels[MAX_COLON_PIXELS];
    int colon_pixel_count;
} ClockState;

/* Initialize clock with given scale and display dimensions */
void clock_init(ClockState *c, int scale, int display_width, int display_height);

/* Update time — resets animations for changed digits */
void clock_update_time(ClockState *c, int hour, int minute, int second);

/* Advance all digit animations by one step */
void clock_tick(ClockState *c);

/* Check if all animations have finished */
int clock_is_complete(const ClockState *c);

/*
 * Get all blocks (settled + falling) in absolute screen coordinates.
 * Fills out[] with up to MAX_RENDER_BLOCKS entries.
 * Returns the count written.
 */
int clock_get_render_blocks(const ClockState *c, RenderBlock *out);

/*
 * Get colon pixel positions if visible.
 * Returns pointer to internal colon_pixels array if visible, NULL otherwise.
 * Sets *count to number of pixels.
 */
const Pixel *clock_get_colon_pixels(const ClockState *c, int *count);

#endif /* TETRIS_CLOCK_H */
