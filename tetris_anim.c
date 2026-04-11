/*
 * Per-digit animation state machine.
 */

#include "tetris_anim.h"

/*
 * Calculate current rotation during fall based on progress.
 * Blocks rotate progressively as they fall.
 */
static int get_rotation(int num_rot, int fallindex, int y_stop)
{
    if (num_rot == 0)
        return 0;

    if (num_rot == 1) {
        if (fallindex < y_stop / 2)
            return 0;
        return 1;
    }

    if (num_rot == 2) {
        if (fallindex < y_stop / 3)
            return 0;
        if (fallindex < y_stop / 3 * 2)
            return 1;
        return 2;
    }

    /* num_rot == 3 */
    if (fallindex < y_stop / 4)
        return 0;
    if (fallindex < y_stop / 4 * 2)
        return 1;
    if (fallindex < y_stop / 4 * 3)
        return 2;
    return 3;
}

void digit_anim_init(DigitAnim *a)
{
    a->digit = -1;
    a->blockindex = 0;
    a->fallindex = 0;
}

void digit_anim_reset(DigitAnim *a, int new_digit)
{
    a->digit = new_digit;
    a->blockindex = 0;
    a->fallindex = 0;
}

int digit_anim_is_complete(const DigitAnim *a)
{
    if (a->digit < 0 || a->digit > 9)
        return 1;
    return a->blockindex >= DIGIT_BLOCK_COUNT[a->digit];
}

void digit_anim_tick(DigitAnim *a)
{
    if (digit_anim_is_complete(a))
        return;

    const BlockDef *block = &DIGIT_BLOCKS[a->digit][a->blockindex];
    int y_stop = block->y_stop;

    a->fallindex++;
    if (a->fallindex > y_stop) {
        a->fallindex = 0;
        a->blockindex++;
    }
}

int digit_anim_get_settled(const DigitAnim *a, BlockState *settled)
{
    if (a->digit < 0 || a->digit > 9)
        return 0;

    int limit = a->blockindex;
    int total = DIGIT_BLOCK_COUNT[a->digit];
    if (limit > total)
        limit = total;

    for (int i = 0; i < limit; i++) {
        const BlockDef *b = &DIGIT_BLOCKS[a->digit][i];
        settled[i].blocktype = b->blocktype;
        settled[i].color = b->color;
        settled[i].x_pos = b->x_pos;
        settled[i].y_pos = b->y_stop - 1;
        settled[i].rotation = b->num_rot;
    }
    return limit;
}

int digit_anim_get_falling(const DigitAnim *a, BlockState *out)
{
    if (digit_anim_is_complete(a))
        return 0;

    const BlockDef *b = &DIGIT_BLOCKS[a->digit][a->blockindex];
    out->blocktype = b->blocktype;
    out->color = b->color;
    out->x_pos = b->x_pos;
    out->y_pos = a->fallindex - 1;
    out->rotation = get_rotation(b->num_rot, a->fallindex, b->y_stop);
    return 1;
}
