from plone.restapi.imaging import get_actual_scale
from unittest import TestCase


class TestGetActualScale(TestCase):
    def test_constrains_landscape_to_width(self):
        img = (800, 400)
        bbox = (200, 200)
        self.assertEqual((200, 100), get_actual_scale(img, bbox))

    def test_constrains_portrait_to_height(self):
        img = (400, 800)
        bbox = (200, 200)
        self.assertEqual((100, 200), get_actual_scale(img, bbox))

    def test_doesnt_upscale(self):
        img = (5, 5)
        bbox = (200, 200)
        self.assertEqual((5, 5), get_actual_scale(img, bbox))

    def test_truncates_pixel_dimensions_instead_of_rounding(self):
        img = (215, 56)
        bbox = (64, 64)
        # 64, 16.66
        self.assertEqual((64, 16), get_actual_scale(img, bbox))

    def test_doesnt_produce_zero_pixel_lengths(self):
        img = (1, 1000)
        bbox = (1, 1)
        self.assertEqual((1, 1), get_actual_scale(img, bbox))
