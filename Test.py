import unittest
from Abhi import greet

class TestExamplePlugin(unittest.TestCase):
    def test_greet(self):
        self.assertEqual(greet("Abhi"), "Hello, Abhi! This is a plugin.")

if __name__ == '__main__':
    unittest.main()
