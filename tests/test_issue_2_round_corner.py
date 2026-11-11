# Regression test for Leohq1/p06-Leohq1 issue #2.
#
# round_corner with transparent=True must not leave dark, opaque pixels on
# the curved edge. Such pixels are drawn in the source color scaled toward
# black, which shows up as a dark ring over any background.

from PIL import Image

from thumbor.ext.filters import _round_corner

WIDTH = 60
HEIGHT = 60
RADIUS = 30
SOURCE = (0, 0, 255, 255)


def _apply_transparent_round_corner():
    source = Image.new("RGBA", (WIDTH, HEIGHT), SOURCE)
    result = _round_corner.apply(
        1,
        "RGBA",
        RADIUS,
        RADIUS,
        255,
        255,
        255,
        WIDTH,
        HEIGHT,
        source.tobytes(),
        True,
    )
    return Image.frombytes("RGBA", (WIDTH, HEIGHT), bytes(result))


def test_transparent_round_corner_has_no_dark_opaque_edge_pixels():
    """Opaque edge pixels must keep the source color, not a darkened one."""
    out = _apply_transparent_round_corner()

    dark_opaque = []
    for y in range(RADIUS):
        for x in range(RADIUS):
            r, g, b, a = out.getpixel((x, y))
            if a == 255 and b < SOURCE[2]:
                dark_opaque.append((x, y, (r, g, b, a)))

    assert dark_opaque == [], (
        "dark opaque pixels on the rounded corner (issue #2): "
        f"{dark_opaque[:5]}"
    )
