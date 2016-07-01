#!/usr/bin/env python

import unittest

class doesBeepEqualBoopTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_doesBeepIndeedEqualBoop(self):
        beep = 'beep'
        boop = 'boop'
        assert not beep==boop
        # Q.E.D

if __name__ == '__main__':
    unittest.main()
