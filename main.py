#!/usr/bin/env python3
"""
Tetris Clock - Main entry point.

Displays time using falling Tetris blocks on a 64x32 RGB LED matrix.
"""

import argparse
import gc
import os
import time
import signal

from tetris_clock.clock import Clock
from tetris_clock.temperature import TemperatureDisplay


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
    options.pwm_lsb_nanoseconds = args.pwm_lsb_nanoseconds
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
    temp_display = TemperatureDisplay(scale=args.pixel_scale)
    showing_temp = False

    # Set up Home Assistant integration if configured
    ha_state = None
    ha_url = getattr(args, 'ha_url', None) or os.environ.get('HA_URL')
    ha_token = getattr(args, 'ha_token', None) or os.environ.get('HA_TOKEN')
    ha_temp_entity = getattr(args, 'ha_temp_entity', None) or os.environ.get('HA_TEMP_ENTITY')
    ha_display_entity = getattr(args, 'ha_display_entity', None) or os.environ.get('HA_DISPLAY_ENTITY')

    if ha_url and ha_token and ha_temp_entity:
        from tetris_clock.ha_client import HAState
        ha_state = HAState(
            ha_url, ha_token, ha_temp_entity, ha_display_entity,
            temp_display_secs=args.temp_display_secs,
        )
        ha_state.start()
        print(f"Home Assistant integration enabled (temp: {ha_temp_entity})")

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

                # Temperature display mode switching
                if ha_state and ha_state.show_temp_until > now:
                    if not showing_temp and ha_state.temperature is not None:
                        temp_display.set_temperature(ha_state.temperature)
                        showing_temp = True
                elif showing_temp:
                    showing_temp = False

                last_time_check = now

            # Display off: render blank every frame
            if ha_state and not ha_state.display_on:
                renderer.render_frame([], None)
                frame_count += 1
                if max_frames and frame_count >= max_frames:
                    break
                elapsed = time.monotonic() - frame_start
                sleep_time = frame_duration - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
                continue

            # Advance animations and render
            if showing_temp:
                for _ in range(ticks_per_frame):
                    temp_display.tick()
                blocks = temp_display.get_render_blocks()
                colon = None
            else:
                for _ in range(ticks_per_frame):
                    clock.tick()
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
    parser.add_argument("--pwm-bits", type=int, default=9,
                        help="PWM bits for color depth 1-11 (default: 9, lower=less flicker)")
    parser.add_argument("--pwm-lsb-nanoseconds", type=int, default=300,
                        help="PWM LSB timing in ns (default: 300, higher=less flicker)")

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

    # Home Assistant integration
    parser.add_argument("--ha-url",
                        help="Home Assistant base URL (or HA_URL env var)")
    parser.add_argument("--ha-token",
                        help="Home Assistant long-lived access token (or HA_TOKEN env var)")
    parser.add_argument("--ha-temp-entity",
                        help="Temperature sensor entity ID (or HA_TEMP_ENTITY env var)")
    parser.add_argument("--ha-display-entity",
                        help="input_boolean entity ID for display on/off (or HA_DISPLAY_ENTITY env var)")
    parser.add_argument("--temp-display-secs", type=int, default=12,
                        help="Seconds to show temperature (default: 12)")

    args = parser.parse_args()

    if args.test:
        run_test(args)
    else:
        run_matrix(args)


if __name__ == "__main__":
    main()
