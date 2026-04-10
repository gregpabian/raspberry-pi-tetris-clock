#!/usr/bin/env python3
"""
Offline visual testing for the Tetris Clock.

Renders digit animations to PNG files without requiring LED matrix hardware.
"""

import argparse
import os
from datetime import datetime

from tetris_clock.animation import DigitAnimation
from tetris_clock.clock import Clock
from tetris_clock.renderer import PNGRenderer
from tetris_clock.tetris_font import DIGIT_BLOCKS, X_SHIFT_CLOCK


def render_single_digit(digit, output_dir, ticks_per_frame=1, pixel_scale=2):
    """Render a single digit's full animation to PNGs."""
    subdir = os.path.join(output_dir, f"digit_{digit}")
    renderer = PNGRenderer(subdir, pixel_scale=pixel_scale)
    anim = DigitAnimation()
    anim.reset(digit)

    s = pixel_scale
    # Center a single digit: ~7px wide at 1x
    x_origin = (64 - 7 * s) // 2
    # Center vertically: digit content spans y=4..15 at 1x
    content_h = 12 * s
    y_base = (32 - content_h) // 2 - 4 * s

    frame = 0
    while not anim.is_complete():
        blocks = []
        for blocktype, color, x_pos, y_pos, rotation in anim.get_settled_blocks():
            blocks.append((blocktype, color, x_origin + x_pos * s, y_base + y_pos * s, rotation))
        falling = anim.get_falling_block()
        if falling:
            blocktype, color, x_pos, y_pos, rotation = falling
            blocks.append((blocktype, color, x_origin + x_pos * s, y_base + y_pos * s, rotation))

        renderer.render_frame(blocks)

        for _ in range(ticks_per_frame):
            anim.tick()
        frame += 1

    # Render final settled frame
    blocks = []
    for blocktype, color, x_pos, y_pos, rotation in anim.get_settled_blocks():
        blocks.append((blocktype, color, x_origin + x_pos * s, y_base + y_pos * s, rotation))
    renderer.render_frame(blocks)

    print(f"  Digit {digit}: {frame + 1} frames -> {subdir}/")


def render_all_digits(output_dir, ticks_per_frame=1, pixel_scale=2):
    """Render all digits 0-9."""
    for digit in range(10):
        render_single_digit(digit, output_dir, ticks_per_frame, pixel_scale)


def render_clock(output_dir, start_time, num_frames=200, ticks_per_frame=2, pixel_scale=2):
    """Render a clock animation sequence."""
    subdir = os.path.join(output_dir, "clock")
    renderer = PNGRenderer(subdir, pixel_scale=pixel_scale)
    clock = Clock(scale=pixel_scale)

    clock.update_time(start_time)

    for frame in range(num_frames):
        blocks = clock.get_render_blocks()
        colon = clock.get_colon_pixels()
        renderer.render_frame(blocks, colon)

        for _ in range(ticks_per_frame):
            clock.tick()

    print(f"  Clock {start_time.strftime('%H:%M')}: {num_frames} frames -> {subdir}/")


def render_transition(output_dir, num_frames=300, ticks_per_frame=2, pixel_scale=2):
    """Render a time transition (12:59 -> 13:00)."""
    subdir = os.path.join(output_dir, "transition")
    renderer = PNGRenderer(subdir, pixel_scale=pixel_scale)
    clock = Clock(scale=pixel_scale)

    # Start with 12:59 fully rendered
    t1 = datetime(2024, 1, 1, 12, 59)
    clock.update_time(t1)
    # Run until complete
    for _ in range(500):
        clock.tick()
        if clock.is_complete():
            break

    # Render a few frames of settled state
    for _ in range(10):
        blocks = clock.get_render_blocks()
        colon = clock.get_colon_pixels()
        renderer.render_frame(blocks, colon)

    # Transition to 13:00
    t2 = datetime(2024, 1, 1, 13, 0)
    clock.update_time(t2)

    for frame in range(num_frames):
        blocks = clock.get_render_blocks()
        colon = clock.get_colon_pixels()
        renderer.render_frame(blocks, colon)

        for _ in range(ticks_per_frame):
            clock.tick()

    print(f"  Transition 12:59->13:00: {num_frames + 10} frames -> {subdir}/")


def main():
    parser = argparse.ArgumentParser(description="Tetris Clock offline renderer")
    parser.add_argument("--output", "-o", default="test_output",
                        help="Output directory (default: test_output)")
    parser.add_argument("--all-digits", action="store_true",
                        help="Render all digits 0-9")
    parser.add_argument("--digit", type=int, choices=range(10), metavar="N",
                        help="Render a single digit (0-9)")
    parser.add_argument("--clock", action="store_true",
                        help="Render a clock display")
    parser.add_argument("--transition", action="store_true",
                        help="Render a time transition (12:59->13:00)")
    parser.add_argument("--time", default="12:34",
                        help="Start time for --clock mode (HH:MM, default: 12:34)")
    parser.add_argument("--frames", type=int, default=200,
                        help="Number of frames for clock/transition modes (default: 200)")
    parser.add_argument("--ticks", type=int, default=2,
                        help="Animation ticks per frame (default: 2)")
    parser.add_argument("--pixel-scale", type=int, default=2,
                        help="Clock pixel scale factor (default: 2)")

    args = parser.parse_args()

    if not any([args.all_digits, args.digit is not None, args.clock, args.transition]):
        parser.print_help()
        return

    os.makedirs(args.output, exist_ok=True)
    print(f"Rendering to {args.output}/")

    ps = args.pixel_scale

    if args.all_digits:
        render_all_digits(args.output, args.ticks, ps)

    if args.digit is not None:
        render_single_digit(args.digit, args.output, args.ticks, ps)

    if args.clock:
        h, m = map(int, args.time.split(":"))
        start = datetime(2024, 1, 1, h, m)
        render_clock(args.output, start, args.frames, args.ticks, ps)

    if args.transition:
        render_transition(args.output, args.frames, args.ticks, ps)

    print("Done! Convert to GIF with:")
    print(f"  ffmpeg -r 20 -i {args.output}/<subdir>/frame_%04d.png output.gif")


if __name__ == "__main__":
    main()
