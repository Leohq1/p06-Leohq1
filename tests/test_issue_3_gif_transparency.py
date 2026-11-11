# -*- coding: utf-8 -*-

# Regression test for issue #3: resizing a palette GIF that has a
# transparent palette entry must keep those pixels transparent in GIF output
# when PILLOW_PRESERVE_INDEXED_MODE is on (the default).

from io import BytesIO

from PIL import Image, ImageDraw

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine


def make_transparent_palette_gif():
    # Palette GIF: index 0 is the transparent background, index 1 is a
    # blue disc in the middle. Same shape as sticker.gif in course/images.
    img = Image.new("P", (64, 64), 0)
    palette = [0, 0, 0, 0, 0, 255] + [0, 0, 0] * 254
    img.putpalette(palette)
    draw = ImageDraw.Draw(img)
    draw.ellipse([8, 8, 55, 55], fill=1)
    buffer = BytesIO()
    img.save(buffer, "GIF", transparency=0)
    return buffer.getvalue()


def test_resized_gif_keeps_transparent_background():
    config = Config()
    config.PILLOW_PRESERVE_INDEXED_MODE = True
    engine = Engine(Context(config=config))
    engine.load(make_transparent_palette_gif(), ".gif")

    engine.resize(32, 32)
    result = engine.read(".gif")

    out = Image.open(BytesIO(result)).convert("RGBA")
    corner_alpha = out.getpixel((0, 0))[3]
    centre_alpha = out.getpixel((16, 16))[3]

    # Background was transparent in the source, so it must stay transparent.
    assert corner_alpha == 0
    # The blue disc was opaque in the source, so it must stay opaque.
    assert centre_alpha == 255
