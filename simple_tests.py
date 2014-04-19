#!/usr/bin/python
import datetime
import os
import unittest
import simulator as sim

glob_ctr = 0
DO_VALGRIND = int(os.environ.get('WET1_VALGRIND', 0)) == 1


class Wet1TestCases(unittest.TestCase):
    def setUp(self):
        global glob_ctr
        global TEST_OUTPUT_PATH
        global DO_VALGRIND
        cls_name = self.__class__.__name__
        make_name = lambda infix: os.path.join(TEST_OUTPUT_PATH,
                                               '%s-%s-%02d' % (cls_name,
                                                               infix,
                                                               glob_ctr))
        self.sp = sim.SimulatedWet1Proxy(command_log=make_name('commands'),
                                         valgrind=DO_VALGRIND,
                                         valgrind_log=make_name('valgrind'),
                                         proxy_output=make_name('out-actual'),
                                         sim_output=make_name('out-expected'))
        glob_ctr += 1

    def tearDown(self):
        # self.sp._p._proc.kill()
        self.sp.Quit()
        self.sp._p._proc.stdin.write('\n\n')
        self.sp._p._proc.wait()
        del self.sp

    def testInitOnce(self):
        self.sp.Init(10)

    def testInitTwice(self):
        self.sp.Init(10)
        self.sp.Init(123)

    def testAddJobSearcher(self):
        self.sp.Init(10)
        self.sp.AddJobSearcher(1, 2)

    def testAddDuplicateJobSearcher(self):
        self.sp.Init(10)
        self.sp.AddJobSearcher(1, 2)
        self.sp.Hire(1, 1)
        self.sp.AddJobSearcher(1, 2)

    def testAdd100JobSearchers(self):
        self.sp.Init(10)
        for i in xrange(100):
            self.sp.AddJobSearcher(i, 10*i)

    def testAddRemoveJobSearcher(self):
        self.sp.Init(10)
        self.sp.AddJobSearcher(1, 2)
        self.sp.RemoveJobSearcher(1)

    def testRemoveJobSearcher(self):
        self.sp.Init(10)
        self.sp.RemoveJobSearcher(1)

    def testHire(self):
        self.sp.Init(10)
        self.sp.AddJobSearcher(1, 2)
        self.sp.Hire(2, 1)
        self.sp.GetNumEmployed(3)

    def testHireNonExistant(self):
        self.sp.Init(10)
        self.sp.Hire(1, 2)
        self.sp.AddJobSearcher(123, 421)
        self.sp.Hire(1, 2)

    def testHireTwice(self):
        self.sp.Init(11)
        self.sp.AddJobSearcher(10, 40)
        self.sp.Hire(3, 10)
        self.sp.GetNumEmployed(3)
        self.sp.Hire(3, 10)
        self.sp.GetNumEmployed(3)

    def testHireEqBySalary(self):
        self.sp.Init(100)
        self.sp.AddJobSearcher(1, 10)
        self.sp.HireBySalary(1, 10)
        self.sp.GetNumEmployed(1)

    def testHireBySalary(self):
        self.sp.Init(9)
        self.sp.AddJobSearcher(39, 1)
        self.sp.HireBySalary(7, 40)
        self.sp.GetNumEmployed(7)

    def testNoHireBySalary(self):
        self.sp.Init(9)
        self.sp.AddJobSearcher(9, 41)
        self.sp.HireBySalary(7, 40)
        self.sp.GetNumEmployed(7)

    def testBonusNoEmpl(self):
        self.sp.Init(10)
        self.sp.Bonus(2, 40, 50)

    def testBonus(self):
        self.sp.Init(10)
        self.sp.AddJobSearcher(1, 2)
        self.sp.Hire(1, 1)
        self.sp.Bonus(1, 1, 1000)

    def testNegBonus(self):
        self.sp.Init(10)
        self.sp.AddJobSearcher(1, 2)
        self.sp.Hire(1, 1)
        self.sp.Bonus(1, 1, -10)

    def testNoEmplBonus(self):
        self.sp.Init(100)
        self.sp.Bonus(55, 11, 23)

    def testFire(self):
        self.sp.Init(10)
        self.sp.AddJobSearcher(10, 10)
        self.sp.Hire(1, 10)
        self.sp.Fire(1, 10)
        self.sp.GetNumEmployed(1)

    def testFireNoEmpl(self):
        self.sp.Init(10)
        self.sp.Fire(1, 80)

    def testFireTwice(self):
        self.sp.Init(10)
        self.sp.AddJobSearcher(10, 10)
        self.sp.Hire(1, 10)
        self.sp.Fire(1, 10)
        self.sp.GetNumEmployed(1)
        self.sp.Fire(1, 10)
        self.sp.GetNumEmployed(1)

    def testEveryEmployer(self):
        o = 20
        self.sp.Init(o)
        self.sp.AddJobSearcher(111, 2000)
        for i in xrange(o):
            self.sp.Hire(i, 111)
            for j in xrange(o):
                self.sp.GetNumEmployed(i)
                self.sp.HighestPaid(i)
            self.sp.Fire(i, 111)
            for j in xrange(o):
                self.sp.GetNumEmployed(i)
                self.sp.HighestPaid(i)

    def testEmptyCutbacks(self):
        self.sp.Init(10)
        self.sp.CutBacks(1, 20, 3)

    def testUnaffectedCutbacks(self):
        self.sp.Init(10)
        self.sp.AddJobSearcher(1, 20)
        self.sp.Hire(1, 1)
        self.sp.CutBacks(1, 21, 2)
        self.sp.GetNumEmployed(1)
        self.sp.HighestPaid(1)

    def testAllAffectedCutbacks(self):
        self.sp.Init(10)
        self.sp.AddJobSearcher(1, 20)
        self.sp.Hire(1, 1)
        self.sp.CutBacks(1, 11, 2)
        self.sp.GetNumEmployed(1)
        self.sp.HighestPaid(1)

    def testTypicalCutbacks(self):
        self.sp.Init(10)
        self.sp.AddJobSearcher(1, 20)
        self.sp.AddJobSearcher(2, 30)
        self.sp.AddJobSearcher(3, 40)
        self.sp.Hire(1, 1)
        self.sp.Hire(1, 2)
        self.sp.Hire(1, 3)
        self.sp.CutBacks(1, 30, 10)
        self.sp.HighestPaid(1)
        self.sp.GetNumEmployed(1)

    def testHireFire100(self):
        self.sp.Init(10)
        for i in xrange(100):
            self.sp.AddJobSearcher(i, 10 * i)
        for i in xrange(100):
            self.sp.Hire(1, i)
        self.sp.GetNumEmployed(1)
        self.sp.HighestPaid(1)
        for i in xrange(100):
            self.sp.Fire(1, i)
        self.sp.GetNumEmployed(1)
        self.sp.HighestPaid(1)


if __name__ == '__main__':
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    TEST_OUTPUT_PATH = os.path.join(os.getcwd(), 'test-output',
                                    'simple', timestamp)
    os.makedirs(TEST_OUTPUT_PATH)
    unittest.main()
