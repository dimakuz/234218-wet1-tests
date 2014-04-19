#!/usr/bin/python
import os
import subprocess
import threading
import Queue


class Employee:
    def __init__(self, id, salary):
        self.id = id
        self.salary = salary


class Firm(object):
    def __init__(self):
        self.employees = set()

    def add_employee(self, e):
        if e in self.employees:
            raise RuntimeError('Duplicate employee')
        self.employees.add(e)

    def remove_employee(self, e):
        if not (e in self.employees):
            raise RuntimeError('No such employee')
        self.employees.remove(e)

    def get_employee(self, id):
        candidates = filter(lambda x: x.id == id, self.employees)
        if len(candidates) == 0:
            raise RuntimeError('No employee found')
        return candidates[0]


class RecruitmentFirm(Firm):
    def __init__(self):
        Firm.__init__(self)

    def find_by_salary(self, salary):
        candidates = list(filter(lambda x: x.salary <= salary, self.employees))
        if len(candidates) > 0:
            return max(candidates, key=lambda x: (x.salary, x.id))


class HighTechFirm(Firm):
    def __init__(self):
        Firm.__init__(self)

    def num_employees(self):
        return len(self.employees)

    def highest_paid(self):
        if len(self.employees) > 0:
            return sorted(self.employees, key=lambda x: (x.salary, x.id))[-1]
        raise RuntimeError()

    def cutbacks(self, thd, cut):
        def cut_salary(e):
            if e.salary >= thd:
                e.salary -= cut
        map(lambda x: cut_salary(x), self.employees)


class Wet1Sim(object):
    def __init__(self, *args, **kwargs):
        self._init = False
        self.ged = {}

    def Init(self, k):
        if (self._init):
            return 'Init was already called.\n'
        self.recr = RecruitmentFirm()
        self.firms = list(map(lambda x: HighTechFirm(), xrange(k)))
        self._init = True
        return 'Init done.\n'

    def AddJobSearcher(self, id, salary):
        if (id < 0 or salary < 0):
            return 'AddJobSearcher: Invalid_input\n'
        try:
            if id in self.ged:
                raise RuntimeError('Duplicate employee')
            self.ged[id] = Employee(id, salary)
            self.recr.add_employee(self.ged[id])
        except (RuntimeError):
            return 'AddJobSearcher: Failure\n'
        return 'AddJobSearcher: Success\n'

    def RemoveJobSearcher(self, id):
        if (id < 0):
            return 'RemoveJobSearcher: Invalid_input\n'
        try:
            if not id in self.ged:
                raise RuntimeError('No such employee')
            self.recr.remove_employee(self.recr.get_employee(id))
            del self.ged[id]
        except (RuntimeError):
            return 'RemoveJobSearcher: Failure\n'
        return 'RemoveJobSearcher: Success\n'

    def Hire(self, cid, id):
        if (id < 0 or cid < 0 or cid >= len(self.firms)):
            return 'Hire: Invalid_input\n'
        try:
            e = self.recr.get_employee(id)
            self.recr.remove_employee(e)
            self.firms[cid].add_employee(e)
        except:
            return 'Hire: Failure\n'
        return 'Hire: Success\n'

    def HireBySalary(self, cid, thd):
        if (cid < 0 or cid >= len(self.firms) or thd < 0):
            return 'HireBySalary: Invalid_input\n'
        try:
            e = self.recr.find_by_salary(thd)
            if not e:
                raise RuntimeError()
            self.recr.remove_employee(e)
            self.firms[cid].add_employee(e)
        except (RuntimeError):
            return 'HireBySalary: Failure\n'
        return 'HireBySalary: Success\n'

    def Bonus(self, cid, id, bonus):
        if (cid < 0 or cid >= len(self.firms) or id < 0 or bonus < 0):
            return 'Bonus: Invalid_input\n'
        try:
            e = self.firms[cid].get_employee(id)
            e.salary += bonus
        except (RuntimeError):
            return 'Bonus: Failure\n'
        return 'Bonus: Success\n'

    def Fire(self, cid, id):
        if (cid < 0 or cid >= len(self.firms) or id < 0):
            return 'Fire: Invalid_input\n'
        try:
            e = self.firms[cid].get_employee(id)
            self.firms[cid].remove_employee(e)
            self.recr.add_employee(e)
        except (RuntimeError):
            return 'Fire: Failure\n'
        return 'Fire: Success\n'

    def GetNumEmployed(self, cid):
        if (cid < 0 or cid >= len(self.firms)):
            return 'GetNumEmployed: Invalid_input\n'
        try:
            ret = self.firms[cid].num_employees()
        except (RuntimeError):
            return 'GetNumEmployed: Failure\n'
        return 'GetNumEmployed: Success %d\n' % ret

    def HighestPaid(self, cid):
        if (cid < 0 or cid >= len(self.firms)):
            return 'HighestPaid: Invalid_input\n'
        try:
            id = self.firms[cid].highest_paid().id
        except (RuntimeError):
            return 'HighestPaid: Failure\n'
        return 'HighestPaid: Success %d\n' % id

    def CutBacks(self, cid, thd, cut):
        if (cid < 0 or cid >= len(self.firms) or thd < 0 or cut < 0
                or cut > thd):
            return 'CutBacks: Invalid_input\n'
        try:
            if len(self.firms[cid].employees) < 1:
                raise RuntimeError()
            self.firms[cid].cutbacks(thd, cut)
        except (RuntimeError):
            return 'CutBacks: Failure\n'
        return 'CutBacks: Success\n'

    def Quit(self):
        self._init = False
        del self.recr
        del self.firms
        return 'Quit done.\n'

    def Comment(self, c):
        return '#%s\n' % c


PATH_TO_EXEC = os.environ['WET1_EXEC']


class Wet1Proxy(object):
    def __init__(self, command_log=None, valgrind=False, valgrind_log=None):
        cmd = []
        if valgrind:
            cmd = ['valgrind', '--leak-check=full']
            if valgrind_log:
                cmd.append('--log-file=%s' % valgrind_log)
        cmd.append(PATH_TO_EXEC)
        self._proc = subprocess.Popen(cmd, bufsize=1,
                                      stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE)
        self._queue = Queue.Queue()

        def enqueue():
            for line in iter(self._proc.stdout.readline, b''):
                self._queue.put(line)

        self._thread = threading.Thread(target=enqueue)
        self._thread.daemon = True
        self._thread.start()
        if command_log:
            self._command_log = open(command_log, 'w')
        else:
            self._command_log = None

    def _query_proc(self, q):
        self._proc.stdin.write(q + '\n')
        self._proc.stdin.flush()
        if self._command_log:
            self._command_log.write(q + '\n')
        try:
            return self._queue.get(timeout=1)
        except Queue.Empty:
            return ''

    def Init(self, k):
        return self._query_proc('Init %d' % k)

    def AddJobSearcher(self, id, salary):
        return self._query_proc('AddJobSearcher %d %d' % (id, salary))

    def RemoveJobSearcher(self, id):
        return self._query_proc('RemoveJobSearcher %d' % id)

    def Hire(self, cid, id):
        return self._query_proc('Hire %d %d' % (cid, id))

    def HireBySalary(self, cid, thd):
        return self._query_proc('HireBySalary %d %d' % (cid, thd))

    def Bonus(self, cid, id, bonus):
        return self._query_proc('Bonus %d %d %d' % (cid, id, bonus))

    def Fire(self, cid, id):
        return self._query_proc('Fire %d %d' % (cid, id))

    def GetNumEmployed(self, cid):
        return self._query_proc('GetNumEmployed %d' % cid)

    def HighestPaid(self, cid):
        return self._query_proc('HighestPaid %d' % cid)

    def CutBacks(self, cid, thd, cut):
        return self._query_proc('CutBacks %d %d %d' % (cid, thd, cut))

    def Quit(self):
        return self._query_proc('Quit')

    def Comment(self, c):
        return self._query_proc('#%s' % c)


class SimulatedWet1ProxyException(RuntimeError):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __str__(self):
        return '"%s" != "%s"' % (self.a.strip(), self.b.strip())


class SimulatedWet1Proxy:
    def __init__(self, proxy_output=None, sim_output=None, *args, **kwargs):
        self.proxy_stdout, self.sim_stdout = None, None
        if proxy_output:
            self.proxy_stdout = open(proxy_output, 'w')
        if sim_output:
            self.sim_stdout = open(sim_output, 'w')
        self._p = Wet1Proxy(*args, **kwargs)
        self._s = Wet1Sim(*args, **kwargs)

    def _assertEqual(self, a, b):
        if (a != b):
            raise SimulatedWet1ProxyException(a, b)

    def _runOnBoth(self, func):
        sim_output = func(self._s).strip()
        proxy_output = func(self._p).strip()
        self.sim_stdout.write(sim_output + '\n')
        self.proxy_stdout.write(proxy_output + '\n')
        self._assertEqual(proxy_output, sim_output)

    def Init(self, k):
        self._runOnBoth(lambda x: x.Init(k))

    def AddJobSearcher(self, id, salary):
        self._runOnBoth(lambda x: x.AddJobSearcher(id, salary))

    def RemoveJobSearcher(self, id):
        self._runOnBoth(lambda x: x.RemoveJobSearcher(id))

    def Hire(self, cid, id):
        self._runOnBoth(lambda x: x.Hire(cid, id))

    def HireBySalary(self, cid, thd):
        self._runOnBoth(lambda x: x.HireBySalary(cid, thd))

    def Bonus(self, cid, id, bonus):
        self._runOnBoth(lambda x: x.Bonus(cid, id, bonus))

    def Fire(self, cid, id):
        self._runOnBoth(lambda x: x.Fire(cid, id))

    def GetNumEmployed(self, cid):
        self._runOnBoth(lambda x: x.GetNumEmployed(cid))

    def HighestPaid(self, cid):
        self._runOnBoth(lambda x: x.HighestPaid(cid))

    def CutBacks(self, cid, thd, cut):
        self._runOnBoth(lambda x: x.CutBacks(cid, thd, cut))

    def Quit(self):
        self._runOnBoth(lambda x: x.Quit())

    def Comment(self, c):
        self._runOnBoth(lambda x: x.Comment(c))

if __name__ == '__main__':
    pass
