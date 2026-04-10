# Raspberry Pi Tetris Clock

The goal for this project is to implement a clock, where all the numbers are built from falling tetris blocks.
It's going to be running on Raspberry Pi with an LED matrix connected to it.

## Hardware

### SBC

Raspberry Pi Zero W single board computer

### LED Matrix

64x32 HUB-75D LED Matrix

### Matrix HAT

Adafruit RGB Matrix Bonnet for Raspberry Pi

### Power

5V/3A power supply

## Software

### Operating System

Fresh Raspberry Pi OS 32-bit installation, with WiFi and SSH enabled.

### Libraries

[RPi RGB LED Matrix](https://github.com/hzeller/rpi-rgb-led-matrix)

## Implementation

We want to recreate the popular Arduino Tetris Clock library [TetrisAnimation](https://github.com/toblum/TetrisAnimation) to run on Raspberry Pi with the help of the rpi-rgb-led-matrix library.

The clock should start automatically when the board powers on.

## Development

We'd like to develop the code directly on the device, e.g. via some SSH connection (details TBD).
