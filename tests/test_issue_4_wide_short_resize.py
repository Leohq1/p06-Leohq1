# -*- coding: utf-8 -*-

# Regression test for issue #4: very wide or very short resizes of
# transparent images return an empty picture or a 500 error.

import os
from io import BytesIO

from PIL import Image

from tests.base import TestCase
from thumbor.config import Config

IMAGES_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "course", "images")
)


class WideShortResizeTestCase(TestCase):
    def get_config(self):
        config = Config()
        config.LOADER = "thumbor.loaders.file_loader"
        config.FILE_LOADER_ROOT_PATH = IMAGES_ROOT
        return config

    def test_800x20_rainbow_returns_visible_picture(self):
        response = self.fetch("/unsafe/800x20/rainbow.png")
        self.assertEqual(response.code, 200)
        image = Image.open(BytesIO(response.body)).convert("RGBA")
        self.assertEqual(image.size, (800, 20))
        alpha = image.getchannel("A")
        self.assertIsNotNone(
            alpha.getextrema(),
            "picture has no pixels",
        )
        self.assertGreater(
            alpha.getextrema()[1],
            0,
            "every pixel is fully transparent",
        )

    def test_fit_in_1x1_does_not_return_500(self):
        response = self.fetch("/unsafe/fit-in/1x1/940x2.png")
        self.assertNotEqual(response.code, 500)
        image = Image.open(BytesIO(response.body))
        self.assertEqual(image.size, (1, 1))

    def test_fit_in_100x0_does_not_return_500(self):
        response = self.fetch("/unsafe/fit-in/100x0/940x2.png")
        self.assertNotEqual(response.code, 500)
        image = Image.open(BytesIO(response.body))
        self.assertEqual(image.size, (100, 1))
