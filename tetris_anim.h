/*
 * Per-digit animation state machine.
 *
 * Manages the sequential falling of Tetris blocks that compose a digit.
 */

#ifndef TETRIS_ANIM_H
#define TETRIS_ANIM_H

#include "tetris_data.h"

/* Animation state for a single digit position */
typedef struct {
    int digit;       /* -1 = nothing to draw */
    int blockindex;  /* index into DIGIT_BLOCKS[digit] */
    int fallindex;   /* current fall progress (0 to y_stop) */
} DigitAnim;

/* Block state returned by animation queries */
typedef struct {
    int blocktype;
    int color;
    int x_pos;
    int y_pos;
    int rotation;
} BlockState;

/* Initialize to idle state */
void digit_anim_init(DigitAnim *a);

/* Start animation for a new digit */
void digit_anim_reset(DigitAnim *a, int new_digit);

/* Check if all blocks have finished falling */
int digit_anim_is_complete(const DigitAnim *a);

/* Advance animation by one step */
void digit_anim_tick(DigitAnim *a);

/*
 * Get all blocks that have finished falling.
 * Fills settled[] with up to MAX_BLOCKS_PER_DIGIT entries.
 * Returns the count written.
 */
int digit_anim_get_settled(const DigitAnim *a, BlockState *settled);

/*
 * Get the currently falling block.
 * Returns 1 and fills *out if a block is falling, else returns 0.
 */
int digit_anim_get_falling(const DigitAnim *a, BlockState *out);

#endif /* TETRIS_ANIM_H */
