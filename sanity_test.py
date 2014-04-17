#!/usr/bin/python
import unittest
import simulator as sim


class Wet1TestCases(unittest.TestCase):
    def setUp(self):
        self.sp = sim.SimulatedWet1Proxy()

    def tearDown(self):
        self.sp._p._proc.kill()
        self.sp._p._proc.wait()

    def testSanity(self):
        pass

if __name__ == '__main__':
    unittest.main()
