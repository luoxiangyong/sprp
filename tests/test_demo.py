#!/usr/bin/env python3
# -*- coding:utf8 -*-

import unittest

class DemoTests(unittest.TestCase):

    def test_ture(self):
        self.assertTrue(True)

    def test_false(self):
        self.assertFalse(False)
        

if __name__ == "__main__":
    unittest.main()
