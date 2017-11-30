import unittest
import yaml

from src.config.general import GeneralConfig


class StorageTest(unittest.TestCase):
    general = GeneralConfig('../settings.yml')

    def test_storage(self):
        self.assertIsNotNone(self.general.storage)
        self.assertIsNotNone(self.general.cams)


if __name__ == "__main__":
    unittest.main()
