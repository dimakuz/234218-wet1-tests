#!/usr/bin/python
import datetime
import functools
import os
import random
import unittest
import simulator as sim

glob_ctr = 0
DO_VALGRIND = int(os.environ.get('WET1_VALGRIND', 0)) == 1


def emit_test_name(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        self.sp.Comment('Test: %s' % func.func_name)
        return func(*args, **kwargs)
    return wrapper


class Wet1RandomizedTestCases(unittest.TestCase):
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
        try:
            self.sp.Quit()
        except:
            pass
        self.sp._p._proc.stdin.write('\n\n')
        self.sp._p._proc.wait()
        del self.sp

    def testFuzz(self):
        order = 5
        actions = ['Init', 'AddJobSearcher', 'RemoveJobSearcher', 'Hire',
                   'HireBySalary', 'Fire', 'Bonus', 'GetNumEmployed',
                   'HighestPaid', 'CutBacks', 'Quit']
        get_rand = lambda: random.randint(-1, order)
        self.sp.Init(order)
        for _ in xrange(order ** 7):
            action = random.choice(actions)
            if action == 'Init':
                # self.sp.Init(get_rand())
                pass
            elif action == 'AddJobSearcher':
                self.sp.AddJobSearcher(get_rand(), get_rand())
            elif action == 'RemoveJobSearcher':
                self.sp.RemoveJobSearcher(get_rand())
            elif action == 'Hire':
                self.sp.Hire(get_rand(), get_rand())
            elif action == 'HireBySalary':
                self.sp.HireBySalary(get_rand(), get_rand())
            elif action == 'Fire':
                self.sp.Fire(get_rand(), get_rand())
            elif action == 'Bonus':
                self.sp.Bonus(get_rand(), get_rand(), get_rand())
            elif action == 'GetNumEmployed':
                self.sp.GetNumEmployed(get_rand())
            elif action == 'HighestPaid':
                self.sp.HighestPaid(get_rand())
            elif action == 'CutBacks':
                self.sp.CutBacks(get_rand(), get_rand(), get_rand())


if __name__ == '__main__':
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    TEST_OUTPUT_PATH = os.path.join(os.getcwd(), 'test-output',
                                    'random', timestamp)
    os.makedirs(TEST_OUTPUT_PATH)
    unittest.main()
