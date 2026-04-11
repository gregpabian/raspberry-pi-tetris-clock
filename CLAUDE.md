# Tetris Clock

A Raspberry Pi-powered clock that displays time using falling Tetris blocks on a 64x32 LED matrix. Pure C implementation for flicker-free performance on Pi Zero W.

## Hardware

- Raspberry Pi Zero W
- 64x32 HUB-75D LED Matrix
- Adafruit RGB Matrix Bonnet
- 5V/3A power supply

## Project Structure

- `tetris_data.h` - Pure data: digit block definitions, piece shapes, colors (const arrays)
- `tetris_pieces.h/c` - Converts blocktype+rotation to pixel coordinates
- `tetris_anim.h/c` - Per-digit falling block animation state machine
- `tetris_clock.h/c` - Time tracking, digit change detection, display layout
- `tetris_render.h/c` - Display abstraction (LED matrix for Pi, PNG for testing via `#ifdef TEST_MODE`)
- `main.c` - Entry point with argument parsing and main loop
- `stb_image_write.h` - Vendored single-header PNG writer (test mode only)

## Building

### On Raspberry Pi
```bash
make                                          # default: library at /usr/local
make MATRIX_ROOT=~/rpi-rgb-led-matrix         # if built from source
sudo ./tetris-clock
```

### Test Build (no hardware, PNG output)
```bash
make test
./tetris-clock-test --test-output test_output/ --frames 200
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
- Only `tetris_render.c` (matrix mode) includes `led-matrix-c.h` — all other modules compile anywhere
- Use `make test` to build without hardware dependencies; renders PNG frames
- Digit data in `tetris_data.h` is transcribed from the Arduino TetrisAnimation library

## Key Dependencies

- [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) - LED matrix driver (Pi only)
- [stb_image_write](https://github.com/nothings/stb) - PNG output (test mode only, vendored)

## Pi Configuration Notes

- Audio must be disabled (`dtparam=audio=off` in `/boot/config.txt`) - conflicts with PWM
- Bluetooth should be disabled (`dtoverlay=disable-bt`) to free up UART
- Requires root/sudo for GPIO access
