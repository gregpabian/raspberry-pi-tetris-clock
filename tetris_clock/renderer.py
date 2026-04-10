"""
Display abstraction: renders animation state to either an LED matrix or PNG files.
"""

import os
from PIL import Image, ImageDraw
from tetris_clock.tetris_font import COLORS
from tetris_clock.pieces import get_pixels


def draw_frame_to_image(image, blocks, colon_pixels=None):
    """
    Draw blocks and colon onto a PIL Image.

    Args:
        image: PIL Image (64x32 RGB)
        blocks: List of (blocktype, color_index, abs_x, abs_y) tuples
                where abs_x/abs_y are absolute screen coordinates
        colon_pixels: List of (x, y) pixel positions for the colon, or None
    """
    width, height = image.size
    for blocktype, color_index, x, y, rotation in blocks:
        rgb = COLORS[color_index]
        pixels = get_pixels(blocktype, rotation, x, y)
        for px, py in pixels:
            if 0 <= px < width and 0 <= py < height:
                image.putpixel((px, py), rgb)

    if colon_pixels:
        for px, py in colon_pixels:
            if 0 <= px < width and 0 <= py < height:
                image.putpixel((px, py), (255, 255, 255))


class PNGRenderer:
    """Saves each frame as a numbered PNG for offline testing."""

    def __init__(self, output_dir, scale=8):
        self.output_dir = output_dir
        self.scale = scale
        self.frame_num = 0
        os.makedirs(output_dir, exist_ok=True)

    def render_frame(self, blocks, colon_pixels=None):
        """Render one frame and save as PNG."""
        image = Image.new("RGB", (64, 32), (0, 0, 0))
        draw_frame_to_image(image, blocks, colon_pixels)

        # Scale up for visibility
        scaled = image.resize(
            (64 * self.scale, 32 * self.scale),
            Image.NEAREST,
        )
        path = os.path.join(self.output_dir, f"frame_{self.frame_num:04d}.png")
        scaled.save(path)
        self.frame_num += 1
        return path

    def cleanup(self):
        pass


class MatrixRenderer:
    """Renders frames to an RGB LED matrix via rpi-rgb-led-matrix."""

    def __init__(self, matrix):
        self.matrix = matrix
        self.canvas = matrix.CreateFrameCanvas()
        self.image = Image.new("RGB", (64, 32), (0, 0, 0))

    def render_frame(self, blocks, colon_pixels=None):
        """Render one frame to the LED matrix."""
        # Clear and draw
        self.image.paste((0, 0, 0), [0, 0, 64, 32])
        draw_frame_to_image(self.image, blocks, colon_pixels)

        # Push to matrix
        self.canvas.SetImage(self.image)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def cleanup(self):
        self.matrix.Clear()
