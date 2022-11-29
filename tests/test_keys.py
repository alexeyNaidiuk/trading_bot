from unittest import TestCase

from module.keys import SECRET_KEY, API_KEY


class TestKeys(TestCase):

    def test_keys(self):
        self.assertIsNotNone(SECRET_KEY)
        self.assertIsNotNone(API_KEY)
