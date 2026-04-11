/*
 * Tetris digit data and piece shape definitions.
 *
 * Transcribed from the Arduino TetrisAnimation library via tetris_font.py.
 * Pure const data — no functions, no mutable state.
 */

#ifndef TETRIS_DATA_H
#define TETRIS_DATA_H

#include <stdint.h>

/* RGB color palette */
typedef struct { uint8_t r, g, b; } Color;

static const Color COLORS[9] = {
    {255,   0,   0},   /* 0: red */
    {  0, 255,   0},   /* 1: green */
    { 50,  95, 255},   /* 2: blue */
    {255, 255, 255},   /* 3: white */
    {255, 255,   0},   /* 4: yellow */
    {  0, 255, 255},   /* 5: cyan */
    {255,   0, 255},   /* 6: magenta */
    {251, 128,   0},   /* 7: orange */
    {  0,   0,   0},   /* 8: black */
};

/* Piece pixel offset from anchor point */
typedef struct { int dx, dy; } Offset;

/* Absolute pixel coordinate */
typedef struct { int x, y; } Pixel;

/*
 * PIECE_SHAPES[blocktype][rotation][pixel_index]
 * dy is negative (upward from anchor).
 * Corner (type 7) has 3 pixels; all others have 4.
 * The 4th entry for Corner is {0,0} padding, never read.
 */
static const Offset PIECE_SHAPES[8][4][4] = {
    /* 0: Square (O) — same for all rotations */
    {
        {{0,0},{1,0},{0,-1},{1,-1}},
        {{0,0},{1,0},{0,-1},{1,-1}},
        {{0,0},{1,0},{0,-1},{1,-1}},
        {{0,0},{1,0},{0,-1},{1,-1}},
    },
    /* 1: L-Shape */
    {
        {{0,0},{1,0},{0,-1},{0,-2}},
        {{0,0},{0,-1},{1,-1},{2,-1}},
        {{1,0},{1,-1},{1,-2},{0,-2}},
        {{0,0},{1,0},{2,0},{2,-1}},
    },
    /* 2: J-Shape (reverse L) */
    {
        {{0,0},{1,0},{1,-1},{1,-2}},
        {{0,0},{1,0},{2,0},{0,-1}},
        {{0,0},{0,-1},{0,-2},{1,-2}},
        {{0,-1},{1,-1},{2,-1},{2,0}},
    },
    /* 3: I-Shape */
    {
        {{0,0},{1,0},{2,0},{3,0}},
        {{0,0},{0,-1},{0,-2},{0,-3}},
        {{0,0},{1,0},{2,0},{3,0}},
        {{0,0},{0,-1},{0,-2},{0,-3}},
    },
    /* 4: S-Shape */
    {
        {{1,0},{0,-1},{1,-1},{0,-2}},
        {{0,0},{1,0},{1,-1},{2,-1}},
        {{1,0},{0,-1},{1,-1},{0,-2}},
        {{0,0},{1,0},{1,-1},{2,-1}},
    },
    /* 5: Z-Shape (reverse S) */
    {
        {{0,0},{0,-1},{1,-1},{1,-2}},
        {{1,0},{2,0},{0,-1},{1,-1}},
        {{0,0},{0,-1},{1,-1},{1,-2}},
        {{1,0},{2,0},{0,-1},{1,-1}},
    },
    /* 6: T-Shape (half cross) */
    {
        {{0,0},{1,0},{2,0},{1,-1}},
        {{0,0},{0,-1},{0,-2},{1,-1}},
        {{1,0},{0,-1},{1,-1},{2,-1}},
        {{1,0},{0,-1},{1,-1},{1,-2}},
    },
    /* 7: Corner (3 pixels only, 4th is padding) */
    {
        {{0,0},{1,0},{0,-1},{0,0}},
        {{0,0},{0,-1},{1,-1},{0,0}},
        {{1,0},{1,-1},{0,-1},{0,0}},
        {{0,0},{1,0},{1,-1},{0,0}},
    },
};

/* Number of actual pixels per piece type */
static const int PIECE_PIXEL_COUNT[8] = { 4, 4, 4, 4, 4, 4, 4, 3 };

/*
 * Digit block definitions.
 * Each block: (blocktype, color_index, x_pos, y_stop, num_rot)
 */
#define MAX_BLOCKS_PER_DIGIT 13

typedef struct {
    int blocktype;
    int color;
    int x_pos;
    int y_stop;
    int num_rot;
} BlockDef;

static const BlockDef DIGIT_BLOCKS[10][MAX_BLOCKS_PER_DIGIT] = {
    /* Digit 0 (12 blocks) */
    {
        {2,5,4,16,0}, {4,7,2,16,1}, {3,4,0,16,1}, {6,6,1,16,1},
        {5,1,4,14,0}, {6,6,0,13,3}, {5,1,4,12,0}, {5,1,0,11,0},
        {6,6,4,10,1}, {6,6,0,9,1},  {5,1,1,8,1},  {2,5,3,8,3},
    },
    /* Digit 1 (5 blocks) */
    {
        {2,5,4,16,0}, {3,4,4,15,1}, {3,4,5,13,3}, {2,5,4,11,2},
        {0,0,4,8,0},
    },
    /* Digit 2 (11 blocks) */
    {
        {0,0,4,16,0}, {3,4,0,16,1}, {1,2,1,16,3}, {1,2,1,15,0},
        {3,4,1,12,2}, {1,2,0,12,1}, {2,5,3,12,3}, {0,0,4,10,0},
        {3,4,1,8,0},  {2,5,3,8,3},  {1,2,0,8,1},
    },
    /* Digit 3 (11 blocks) */
    {
        {1,2,3,16,3}, {2,5,0,16,1}, {3,4,1,15,2}, {0,0,4,14,0},
        {3,4,1,12,2}, {1,2,0,12,1}, {3,4,5,12,3}, {2,5,3,11,0},
        {3,4,1,8,0},  {1,2,0,8,1},  {2,5,3,8,3},
    },
    /* Digit 4 (9 blocks) */
    {
        {0,0,4,16,0}, {0,0,4,14,0}, {3,4,1,12,0}, {1,2,0,12,1},
        {2,5,0,10,0}, {2,5,3,12,3}, {3,4,4,10,3}, {2,5,0,9,2},
        {3,4,5,10,1},
    },
    /* Digit 5 (11 blocks) */
    {
        {0,0,0,16,0}, {2,5,2,16,1}, {2,5,3,15,0}, {3,4,5,16,1},
        {3,4,1,12,0}, {1,2,0,12,1}, {2,5,3,12,3}, {0,0,0,10,0},
        {3,4,1,8,2},  {1,2,0,8,1},  {2,5,3,8,3},
    },
    /* Digit 6 (12 blocks) */
    {
        {2,5,0,16,1}, {5,1,2,16,1}, {6,6,0,15,3}, {6,6,4,16,3},
        {5,1,4,14,0}, {3,4,1,12,2}, {2,5,0,13,2}, {3,4,2,11,0},
        {0,0,0,10,0}, {3,4,1,8,0},  {1,2,0,8,1},  {2,5,3,8,3},
    },
    /* Digit 7 (7 blocks) */
    {
        {0,0,4,16,0}, {1,2,4,14,0}, {3,4,5,13,1}, {2,5,4,11,2},
        {3,4,1,8,2},  {2,5,3,8,3},  {1,2,0,8,1},
    },
    /* Digit 8 (13 blocks) */
    {
        {3,4,1,16,0}, {6,6,0,16,1}, {3,4,5,16,1}, {1,2,2,15,3},
        {4,7,0,14,0}, {1,2,1,12,3}, {6,6,4,13,1}, {2,5,0,11,1},
        {4,7,0,10,0}, {4,7,4,11,0}, {5,1,0,8,1},  {5,1,2,8,1},
        {1,2,4,9,2},
    },
    /* Digit 9 (12 blocks) */
    {
        {0,0,0,16,0}, {3,4,2,16,0}, {1,2,2,15,3}, {1,2,4,15,2},
        {3,4,1,12,2}, {3,4,5,12,3}, {5,1,0,12,0}, {1,2,2,11,3},
        {5,1,4,9,0},  {6,6,0,10,1}, {5,1,0,8,1},  {6,6,2,8,2},
    },
};

/* Number of blocks per digit */
static const int DIGIT_BLOCK_COUNT[10] = {
    12, 5, 11, 11, 9, 11, 12, 7, 13, 12
};

/* Layout constants */
static const int X_SHIFT_CLOCK[4] = {0, 7, 17, 24};
#define TETRIS_Y_DROP_DEFAULT 16

/* Content bounds in local (1x) coordinates */
#define CONTENT_WIDTH_1X   31
#define CONTENT_TOP_1X      4
#define CONTENT_BOTTOM_1X  15

#endif /* TETRIS_DATA_H */
