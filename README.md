# Tetris Clock

A Raspberry Pi-powered clock that displays time using falling Tetris blocks on a 64x32 LED matrix.

Recreates the popular Arduino [TetrisAnimation](https://github.com/toblum/TetrisAnimation) library to run on Raspberry Pi using [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix). Written in C for flicker-free performance on the Pi Zero W.

## Hardware

- **SBC:** Raspberry Pi Zero W
- **Display:** 64x32 HUB-75D LED Matrix
- **HAT:** Adafruit RGB Matrix Bonnet for Raspberry Pi
- **Power:** 5V/3A power supply

## Setup

### 1. Prepare the Raspberry Pi

Flash **Raspberry Pi OS 32-bit** (Lite is sufficient) to an SD card. Enable SSH and configure WiFi during setup.

### 2. Connect the hardware

1. Attach the Adafruit RGB Matrix Bonnet to the Pi's GPIO header
2. Connect the HUB-75 ribbon cable from the bonnet to the LED matrix
3. Connect the 5V/3A power supply to the bonnet's power terminal

### 3. Clone the project

```bash
ssh pi@<your-pi-ip>
git clone <your-repo-url> ~/tetris-clock
cd ~/tetris-clock
```

### 4. Run the installer

```bash
sudo bash install.sh
```

This will:
- Install build dependencies (`build-essential`, `git`)
- Clone and build the [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) shared library
- Compile the tetris-clock binary
- Disable onboard audio and Bluetooth in `/boot/config.txt` (required -- audio's PWM conflicts with the LED matrix driver)
- Install and enable the systemd service for auto-start on boot

### 5. Reboot

```bash
sudo reboot
```

The clock will start automatically after reboot.

## Usage

### Manual control

```bash
# Start
sudo systemctl start tetris-clock

# Stop
sudo systemctl stop tetris-clock

# View logs
journalctl -u tetris-clock -f

# Check status
sudo systemctl status tetris-clock
```

### Command-line options

```bash
sudo ./tetris-clock --brightness 50 --fps 20 --ticks 2
```

| Flag | Default | Description |
|------|---------|-------------|
| `--brightness` | 50 | LED brightness (1-100) |
| `--fps` | 20 | Target frames per second |
| `--ticks` | 2 | Animation speed (ticks per frame, higher = faster) |
| `--slowdown` | 2 | GPIO slowdown factor (2 for Pi Zero, 1 for Pi 3/4) |
| `--pwm-bits` | 9 | PWM color depth (1-11, lower = less flicker) |
| `--pwm-lsb-nanoseconds` | 300 | PWM LSB timing (higher = less flicker) |
| `--pixel-scale` | 2 | Clock pixel scale factor |

## Development

### Offline testing (no Pi required)

Build the test binary on any machine with a C compiler:

```bash
make test
./tetris-clock-test --test-output test_output/ --frames 200
```

Convert frames to a GIF for review:

```bash
ffmpeg -r 20 -i test_output/frame_%04d.png clock.gif
```

### Project structure

```
tetris_data.h        # Digit block definitions + piece shapes + colors (const arrays)
tetris_pieces.h/c    # Block type + rotation -> pixel coordinates
tetris_anim.h/c      # Per-digit falling block state machine
tetris_clock.h/c     # Time tracking, digit change detection, layout
tetris_render.h/c    # LED matrix renderer / PNG test renderer (#ifdef TEST_MODE)
main.c               # Entry point
stb_image_write.h    # Vendored PNG writer (test mode only)
install.sh           # Pi setup script
tetris-clock.service # systemd unit file
```

Only `tetris_render.c` (matrix mode) includes `led-matrix-c.h` -- all other modules compile on any machine.

## License

Digit and piece data derived from [TetrisAnimation](https://github.com/toblum/TetrisAnimation) by Tobias Blum, licensed under LGPL-2.1.
