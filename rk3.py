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
        computer._instruction_pointer = self._get_real_address(computer, self._cmd)


class Computer(object):
    def reset(self):
        self._instruction_pointer = 0
        self._memory = []
        self._ac = 0

    def _interprete_line(self, line):
        line_args = line.split()
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
    

    def _read_program(self, program_code):
        with open(program_code, 'r') as f:
            for line in f:
                comment_start = line.find('//')
                if comment_start >= 0:
                    line = line[:comment_start]
                line = ' '.join(line.split())
                self._memory.append(self._interprete_line(line))


    def __init__(self, program_code):
        self.reset()
        self._read_program(program_code)

    def tick(self):
        self._memory[self._instruction_pointer].act(self)
        print(self._ac)


computer = Computer('tx0r.tx0r')
