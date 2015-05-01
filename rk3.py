import sys

def check_int(s):
    s = ''.join(s.split())
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()

class MemoryUnit(object):
    def __init__(self, label):
        self._label = label

    def get_label(self):
        return self._label

    def is_this_label(self, label):
        if self._label is None:
            return False
        return self._label == label

    def get_unit_type(self):
        raise NotImplementedError


class MemoryDataUnit(MemoryUnit):
    def __init__(self, label, value):
        super(MemoryDataUnit, self).__init__(label)
        self._value = value

    def get_unit_type(self):
        return 'data'

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value


class MemoryCmdUnit(MemoryUnit):
    def __init__(self, label, value):
        super(MemoryCmdUnit, self).__init__(label)
        self._cmd = value

    def _get_real_address(self, computer, address):
        if address.isdigit():
            return int(address)
        for i, unit in enumerate(computer._memory):
            if unit.is_this_label(address):
                return i
        print("Label %s in unknown" % address)

    def get_unit_type(self):
        return 'cmd'

    def act(self, computer):
        raise NotImplementedError


class MemoryCmdStoreUnit(MemoryCmdUnit):
    def act(self, computer):
        computer._instruction_pointer += 1
        computer._memory[self._get_real_address(computer, self._cmd)].set_value(computer._ac)


class MemoryCmdAddUnit(MemoryCmdUnit):
    def act(self, computer):
        computer._instruction_pointer += 1
        computer._ac += computer._memory[self._get_real_address(computer, self._cmd)].get_value()


class MemoryCmdTransferUnit(MemoryCmdUnit):
    def act(self, computer):
        if computer._ac < 0:
            computer._instruction_pointer = self._get_real_address(computer, self._cmd)
        else:
            computer._instruction_pointer += 1


class MemoryCmdOperateUnit(MemoryCmdUnit):
    def __init__(self, label, value):
        super(MemoryCmdOperateUnit, self).__init__(label, value)
        operands = value.split(',')
        self._source = operands[0]
        self._operation = operands[1]
        self._destination = operands[2]

    def _get_from_source(self, computer):
        if self._source == 'AC':
            return computer._ac
        elif self._source == 'READ':
            return computer.read_word()
        elif self._source == 'EOF':
            if computer.is_eof():
                return -1
            else:
                return 0

    def act(self, computer):
        computer._instruction_pointer += 1
        val = self._get_from_source(computer)
        print("%s VAL %s" % (self._source, val))

        if self._operation == 'COPY':
            pass
        elif self._operation == 'CLEAR':
            val = 0
        elif self._operation == 'NEGATE':
            val = -val

        if self._destination == 'AC':
            computer._ac = val
        elif self._destination == 'HALT':
            computer.halt(val)
        elif self._destination == 'ERROR':
            computer.error(val)


class Computer(object):
    def reset(self):
        self._instruction_pointer = 0
        self._memory = []
        self._ac = 0
        self._result = None
        self._error = False
        self._input_line = []
        self._eof = False

    def is_eof(self):
        return self._eof

    def halt(self, val):
        self._result = val

    def error(self, val):
        self._result = val
        self._error = True

    def read_word(self):
        if len(self._input_line) > 0:
            res = self._input_line[0]
            self._input_line = self._input_line[1:]
            return res
        else:
            self._eof = True
            return 0

    def is_working(self):
        if self._result is not None:
            return False
        if self._error:
            return False
        return True


    def _interprete_line(self, line):
        line_args = line.split()
        if len(line_args) == 0:
            return None
        label = None
        if line_args[0].endswith(':'):
            label = line_args[0][:-1]
            line_args = line_args[1:]

        if line_args[0] == 'WORD':
            return MemoryDataUnit(label, int(line_args[1]))

        if line_args[0] == 'STORE':
            return MemoryCmdStoreUnit(label, line_args[1])

        if line_args[0] == 'ADD':
            return MemoryCmdAddUnit(label, line_args[1])

        if line_args[0] == 'TRANSFER':
            return MemoryCmdTransferUnit(label, line_args[1])

        if line_args[0] == 'OPERATE':
            return MemoryCmdOperateUnit(label, line_args[1])


    def _read_program(self, program_code):
        with open(program_code, 'r') as f:
            for line in f:
                comment_start = line.find('//')
                if comment_start >= 0:
                    line = line[:comment_start]
                line = ' '.join(line.split())
                unit = self._interprete_line(line)
                if unit is not None:
                    self._memory.append(unit)


    def __init__(self, program_code):
        self.reset()
        self._read_program(program_code)

    def tick(self):
        self._memory[self._instruction_pointer].act(self)

    def set_input_line(self, input_line):
        self._input_line = input_line

    def report(self):
        if self._error:
            print('ERROR')
        else:
            print('HALT %s' % self._result)


progname = sys.argv[1]
computer = Computer(progname)
input_line = []
first = True
for line in sys.stdin:
    line = line.strip(' \n\t\r')
    if not check_int(line.strip()):
        computer = Computer(progname)
        if not first:
            computer.set_input_line(input_line)
            while computer.is_working():
                computer.tick()
            computer.report()
        first = False
        input_line = []
        print(line)
        continue
    else:
        input_line.append(int(line))
computer = Computer(progname)
computer.set_input_line(input_line)
while computer.is_working():
    computer.tick()
computer.report()
