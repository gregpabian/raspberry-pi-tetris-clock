# Tetris Clock

A Raspberry Pi-powered clock that displays time using falling Tetris blocks on a 64x32 LED matrix.

## Hardware

- Raspberry Pi Zero W
- 64x32 HUB-75D LED Matrix
- Adafruit RGB Matrix Bonnet
- 5V/3A power supply

## Project Structure

- `tetris_clock/` - Main package
  - `tetris_font.py` - Pure data: digit block definitions, piece shapes, colors
  - `pieces.py` - Converts blocktype+rotation to pixel coordinates
  - `animation.py` - Per-digit falling block animation state machine
  - `clock.py` - Time tracking, digit change detection, display layout
  - `renderer.py` - Display abstraction (MatrixRenderer for Pi, PNGRenderer for testing)
  - `temperature.py` - Temperature display with mixed-scale Tetris blocks
  - `ha_client.py` - Home Assistant REST API polling (background thread)
- `main.py` - Entry point with argument parsing and main loop
- `test_render.py` - Offline visual testing (renders to PNG files)

## Running

### On Raspberry Pi
```bash
sudo python3 main.py
```
Matrix options (rows, cols, GPIO mapping) are set in code. Tunable via CLI: `--brightness`, `--slowdown`, `--pwm-bits`, `--pwm-lsb-nanoseconds`, `--pixel-scale`.

### Home Assistant Integration
Set `HA_URL`, `HA_TOKEN`, `HA_TEMP_ENTITY` (and optionally `HA_DISPLAY_ENTITY`) as env vars or CLI flags to enable temperature display and remote on/off control.

### Offline Testing (no hardware)
```bash
python3 test_render.py --all-digits --output test_output/
python3 test_render.py --clock --output test_output/
# Convert to GIF: ffmpeg -r 20 -i test_output/frame_%04d.png test.gif
```

### As a Service
```bash
sudo systemctl start tetris-clock
sudo systemctl status tetris-clock
journalctl -u tetris-clock -f
```

## Development

- Develop via SSH directly on the Pi
- Only `renderer.py`'s `MatrixRenderer` imports `rgbmatrix` - all other modules run on any machine
- Use `test_render.py` or `main.py --test` for development without hardware
- Digit data in `tetris_font.py` is transcribed from the Arduino TetrisAnimation library

## Key Dependencies

- [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) - LED matrix driver (Pi only)
- [Pillow](https://pillow.readthedocs.io/) - Image rendering (all platforms)

## Pi Configuration Notes

- Audio must be disabled (`dtparam=audio=off` in `/boot/config.txt`) - conflicts with PWM
- Bluetooth should be disabled (`dtoverlay=disable-bt`) to free up UART
- Requires root/sudo for GPIO access
