#!/usr/bin/env python3
"""
Tetris Clock - Main entry point.

Displays time using falling Tetris blocks on a 64x32 RGB LED matrix.
"""

import argparse
import gc
import time
import signal
import sys

from tetris_clock.clock import Clock


def create_matrix(args):
    """Create and configure the RGB matrix."""
    from rgbmatrix import RGBMatrix, RGBMatrixOptions

    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.hardware_mapping = "adafruit-hat"
    options.gpio_slowdown = args.slowdown
    options.brightness = args.brightness
    options.pwm_bits = args.pwm_bits
    options.drop_privileges = False

    return RGBMatrix(options=options)


def run_matrix(args):
    """Run the clock on the LED matrix."""
    from tetris_clock.renderer import MatrixRenderer

    matrix = create_matrix(args)
    renderer = MatrixRenderer(matrix, pixel_scale=args.pixel_scale)
    run_loop(renderer, args)


def run_test(args):
    """Run the clock in test mode, saving PNGs."""
    from tetris_clock.renderer import PNGRenderer

    renderer = PNGRenderer(args.test_output, png_scale=args.scale,
                           pixel_scale=args.pixel_scale)
    run_loop(renderer, args, max_frames=args.frames)


def run_loop(renderer, args, max_frames=None):
    """Main animation loop."""
    target_fps = args.fps
    frame_duration = 1.0 / target_fps
    ticks_per_frame = args.ticks

    clock = Clock(scale=args.pixel_scale)
    last_time_check = 0
    frame_count = 0

    # Graceful shutdown
    running = True

    def signal_handler(sig, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(f"Tetris Clock running (fps={target_fps}, ticks={ticks_per_frame})")

    # Disable automatic GC to avoid random frame-drop pauses
    gc.disable()

    try:
        while running:
            frame_start = time.monotonic()

            # Check time every second; run GC here where a small hitch is invisible
            now = time.monotonic()
            if now - last_time_check >= 1.0:
                gc.collect()
                clock.update_time()
                last_time_check = now

            # Advance animations
            for _ in range(ticks_per_frame):
                clock.tick()

            # Render
            blocks = clock.get_render_blocks()
            colon = clock.get_colon_pixels()
            renderer.render_frame(blocks, colon)

            frame_count += 1
            if max_frames and frame_count >= max_frames:
                break

            # Frame rate cap
            elapsed = time.monotonic() - frame_start
            sleep_time = frame_duration - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
    finally:
        renderer.cleanup()
        print(f"\nStopped after {frame_count} frames.")


def main():
    parser = argparse.ArgumentParser(description="Tetris Clock for RGB LED Matrix")
    parser.add_argument("--fps", type=int, default=20,
                        help="Target frames per second (default: 20)")
    parser.add_argument("--ticks", type=int, default=2,
                        help="Animation ticks per frame (default: 2)")
    parser.add_argument("--brightness", type=int, default=50,
                        help="LED brightness 1-100 (default: 50)")
    parser.add_argument("--slowdown", type=int, default=2,
                        help="GPIO slowdown factor (default: 2 for Pi Zero)")
    parser.add_argument("--pwm-bits", type=int, default=7,
                        help="PWM bits for color depth 1-11 (default: 7, lower=less flicker)")

    # Test mode
    parser.add_argument("--test", action="store_true",
                        help="Run in test mode (PNG output, no matrix)")
    parser.add_argument("--test-output", default="test_output",
                        help="Output directory for test mode (default: test_output)")
    parser.add_argument("--frames", type=int, default=200,
                        help="Max frames in test mode (default: 200)")
    parser.add_argument("--scale", type=int, default=8,
                        help="PNG scale factor in test mode (default: 8)")
    parser.add_argument("--pixel-scale", type=int, default=2,
                        help="Clock pixel scale factor (default: 2)")

    args = parser.parse_args()

    if args.test:
        run_test(args)
    else:
        run_matrix(args)


if __name__ == "__main__":
    main()
