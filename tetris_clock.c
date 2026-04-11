/*
 * Clock logic: time tracking, digit change detection, and display layout.
 */

#include <stddef.h>
#include "tetris_clock.h"

void clock_init(ClockState *c, int scale, int display_width, int display_height)
{
    c->scale = scale;

    /* Center content on display — matches Python clock.py exactly */
    int content_w = CONTENT_WIDTH_1X * scale;
    int content_h = (CONTENT_BOTTOM_1X - CONTENT_TOP_1X + 1) * scale;
    c->x_origin = (display_width - content_w) / 2 + 1;
    int y_margin = (display_height - content_h) / 2 - 2;
    c->y_base = y_margin - CONTENT_TOP_1X * scale;

    for (int i = 0; i < NUM_DIGITS; i++) {
        digit_anim_init(&c->digits[i]);
        c->current_digits[i] = -1;
    }

    c->colon_visible = 1;

    /* Pre-compute colon pixel coordinates (two 2x2 square dots, scaled) */
    int cx = c->x_origin + 14 * scale;
    int n = 0;
    int dot_offsets[2] = {8, 12};
    for (int d = 0; d < 2; d++) {
        int cy = c->y_base + dot_offsets[d] * scale;
        for (int dx = 0; dx < 2 * scale; dx++) {
            for (int dy = 0; dy < 2 * scale; dy++) {
                c->colon_pixels[n].x = cx + dx;
                c->colon_pixels[n].y = cy + dy;
                n++;
            }
        }
    }
    c->colon_pixel_count = n;
}

void clock_update_time(ClockState *c, int hour, int minute, int second)
{
    c->colon_visible = (second % 2 == 0);

    int new_digits[4] = {
        hour / 10, hour % 10,
        minute / 10, minute % 10
    };

    for (int i = 0; i < NUM_DIGITS; i++) {
        if (new_digits[i] != c->current_digits[i]) {
            digit_anim_reset(&c->digits[i], new_digits[i]);
            c->current_digits[i] = new_digits[i];
        }
    }
}

void clock_tick(ClockState *c)
{
    for (int i = 0; i < NUM_DIGITS; i++) {
        digit_anim_tick(&c->digits[i]);
    }
}

int clock_is_complete(const ClockState *c)
{
    for (int i = 0; i < NUM_DIGITS; i++) {
        if (!digit_anim_is_complete(&c->digits[i]))
            return 0;
    }
    return 1;
}

int clock_get_render_blocks(const ClockState *c, RenderBlock *out)
{
    int s = c->scale;
    int n = 0;

    for (int i = 0; i < NUM_DIGITS; i++) {
        const DigitAnim *da = &c->digits[i];
        int x_shift = X_SHIFT_CLOCK[i];

        /* Settled blocks */
        BlockState settled[MAX_BLOCKS_PER_DIGIT];
        int settled_count = digit_anim_get_settled(da, settled);
        for (int j = 0; j < settled_count; j++) {
            out[n].blocktype = settled[j].blocktype;
            out[n].color = settled[j].color;
            out[n].screen_x = c->x_origin + (x_shift + settled[j].x_pos) * s;
            out[n].screen_y = c->y_base + settled[j].y_pos * s;
            out[n].rotation = settled[j].rotation;
            n++;
        }

        /* Falling block */
        BlockState falling;
        if (digit_anim_get_falling(da, &falling)) {
            out[n].blocktype = falling.blocktype;
            out[n].color = falling.color;
            out[n].screen_x = c->x_origin + (x_shift + falling.x_pos) * s;
            out[n].screen_y = c->y_base + falling.y_pos * s;
            out[n].rotation = falling.rotation;
            n++;
        }
    }

    return n;
}

const Pixel *clock_get_colon_pixels(const ClockState *c, int *count)
{
    if (!c->colon_visible) {
        *count = 0;
        return NULL;
    }
    *count = c->colon_pixel_count;
    return c->colon_pixels;
}
