/*
 * Display abstraction: renders animation state to either an LED matrix or PNG files.
 */

#include <string.h>
#include "tetris_render.h"

/* Maximum pixels per piece at any scale: 4 pixels * scale^2 each.
 * At scale=2 that's 16; at scale=4 that's 64. 256 covers scale up to 8. */
#define MAX_PIECE_PIXELS 256

#ifdef TEST_MODE

#include <stdio.h>
#include <stdlib.h>

#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

void renderer_init_test(Renderer *r, const char *output_dir, int png_scale)
{
    strncpy(r->output_dir, output_dir, sizeof(r->output_dir) - 1);
    r->output_dir[sizeof(r->output_dir) - 1] = '\0';
    r->png_scale = png_scale;
    r->frame_num = 0;
}

void renderer_render_frame(Renderer *r,
                           const RenderBlock *blocks, int block_count,
                           const Pixel *colon_pixels, int colon_count,
                           int scale)
{
    /* Clear framebuffer */
    memset(r->framebuf, 0, sizeof(r->framebuf));

    /* Draw blocks */
    Pixel pixels[MAX_PIECE_PIXELS];
    for (int i = 0; i < block_count; i++) {
        const RenderBlock *b = &blocks[i];
        Color c = COLORS[b->color];
        int n = get_pixels(b->blocktype, b->rotation,
                           b->screen_x, b->screen_y, scale, pixels);
        for (int j = 0; j < n; j++) {
            int px = pixels[j].x, py = pixels[j].y;
            if (px >= 0 && px < DISPLAY_WIDTH && py >= 0 && py < DISPLAY_HEIGHT) {
                r->framebuf[py][px][0] = c.r;
                r->framebuf[py][px][1] = c.g;
                r->framebuf[py][px][2] = c.b;
            }
        }
    }

    /* Draw colon */
    if (colon_pixels) {
        for (int i = 0; i < colon_count; i++) {
            int px = colon_pixels[i].x, py = colon_pixels[i].y;
            if (px >= 0 && px < DISPLAY_WIDTH && py >= 0 && py < DISPLAY_HEIGHT) {
                r->framebuf[py][px][0] = 255;
                r->framebuf[py][px][1] = 255;
                r->framebuf[py][px][2] = 0;
            }
        }
    }

    /* Scale up and write PNG */
    int sw = DISPLAY_WIDTH * r->png_scale;
    int sh = DISPLAY_HEIGHT * r->png_scale;
    uint8_t *scaled = (uint8_t *)malloc(sw * sh * 3);
    if (!scaled) return;

    for (int y = 0; y < DISPLAY_HEIGHT; y++) {
        for (int x = 0; x < DISPLAY_WIDTH; x++) {
            for (int sy = 0; sy < r->png_scale; sy++) {
                for (int sx = 0; sx < r->png_scale; sx++) {
                    int di = ((y * r->png_scale + sy) * sw + (x * r->png_scale + sx)) * 3;
                    scaled[di + 0] = r->framebuf[y][x][0];
                    scaled[di + 1] = r->framebuf[y][x][1];
                    scaled[di + 2] = r->framebuf[y][x][2];
                }
            }
        }
    }

    char path[512];
    snprintf(path, sizeof(path), "%s/frame_%04d.png", r->output_dir, r->frame_num);
    stbi_write_png(path, sw, sh, 3, scaled, sw * 3);
    free(scaled);
    r->frame_num++;
}

void renderer_cleanup(Renderer *r)
{
    (void)r;
}

#else /* Matrix mode */

void renderer_init_matrix(Renderer *r, struct RGBLedMatrix *matrix)
{
    r->matrix = matrix;
    r->canvas = led_matrix_create_offscreen_canvas(matrix);
}

void renderer_render_frame(Renderer *r,
                           const RenderBlock *blocks, int block_count,
                           const Pixel *colon_pixels, int colon_count,
                           int scale)
{
    led_canvas_clear(r->canvas);

    /* Draw blocks */
    Pixel pixels[MAX_PIECE_PIXELS];
    for (int i = 0; i < block_count; i++) {
        const RenderBlock *b = &blocks[i];
        Color c = COLORS[b->color];
        int n = get_pixels(b->blocktype, b->rotation,
                           b->screen_x, b->screen_y, scale, pixels);
        for (int j = 0; j < n; j++) {
            int px = pixels[j].x, py = pixels[j].y;
            if (px >= 0 && px < DISPLAY_WIDTH && py >= 0 && py < DISPLAY_HEIGHT) {
                led_canvas_set_pixel(r->canvas, px, py, c.r, c.g, c.b);
            }
        }
    }

    /* Draw colon */
    if (colon_pixels) {
        for (int i = 0; i < colon_count; i++) {
            int px = colon_pixels[i].x, py = colon_pixels[i].y;
            if (px >= 0 && px < DISPLAY_WIDTH && py >= 0 && py < DISPLAY_HEIGHT) {
                led_canvas_set_pixel(r->canvas, px, py, 255, 255, 0);
            }
        }
    }

    r->canvas = led_matrix_swap_on_vsync(r->matrix, r->canvas);
}

void renderer_cleanup(Renderer *r)
{
    led_canvas_clear(r->canvas);
    led_matrix_swap_on_vsync(r->matrix, r->canvas);
}

#endif /* TEST_MODE */
