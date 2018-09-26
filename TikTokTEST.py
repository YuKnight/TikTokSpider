from unittest import TestCase


class TestIs_valid_id(TestCase):
    def test_is_valid_id(self):
        from dyspider import is_valid_id
        self.assertTrue(is_valid_id(100))
        self.assertTrue(is_valid_id(198372198))
        self.assertFalse(is_valid_id('a'))
        self.assertFalse(is_valid_id(''))
        self.assertFalse(is_valid_id('KASFJ'))
        self.assertFalse(is_valid_id(0))
