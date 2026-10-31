import enum
import sys
import random

class StackValue:
  def __init__(self, val):
    self.set_value(val)

  @property
  def value(self):
    return self.__value
  
  def set_value(self, val):
    if isinstance(val, bool): # Bools ARE integers in Python, but we need to manually cast to store as int
      self.__value = int(val)
    elif isinstance(val, int):
      self.__value = val
    elif isinstance(val, str):
      if len(val) == 1:
        self.__value = ord(val)
      else:
        raise ValueError(f'Stack values can only be integers or ASCII chars (strings of length 1). You passed string {val} of length {len(val)}')
    else:
        raise TypeError(f'Stack values can only be integers or ASCII chars (strings of length 1). You passed {val}')

  @value.setter
  def value(self, val):
    self.set_value(val)

class Instruction:
  def __init__(self, symbol):
    self.symbol = symbol

  def __call__(self, program):
    raise NotImplementedError(f'Instruction not implemented: "{self.symbol}"')

class InstructionSpace(Instruction):
  def __init__(self):
    super().__init__(' ')

  def __call__(self, program):
    pass

class InstructionUp(Instruction):
  def __init__(self):
    super().__init__('^')

  def __call__(self, program):
    program.facing = Facing.NORTH

class InstructionDown(Instruction):
  def __init__(self):
    super().__init__('v')

  def __call__(self, program):
    program.facing = Facing.SOUTH

class InstructionLeft(Instruction):
  def __init__(self):
    super().__init__('<')

  def __call__(self, program):
    program.facing = Facing.WEST

class InstructionRight(Instruction):
  def __init__(self):
    super().__init__('>')

  def __call__(self, program):
    program.facing = Facing.EAST

class InstructionRandom(Instruction):
  def __init__(self):
    super().__init__('?')

  def __call__(self, program):
    p = random.uniform(0,1)
    if p < 0.25:
      program.facing = Facing.NORTH 
    elif p < 0.5:
      program.facing = Facing.SOUTH
    elif p < 0.75:
      program.facing = Facing.EAST
    else:
      program.facing = Facing.WEST 

class InstructionTerminate(Instruction):
  def __init__(self):
    super().__init__('@')

  def __call__(self, program):
    program.facing = Facing.DONE
    print('PROGRAM TERMINATED, @ REACHED')

class InstructionInt(Instruction):
  def __init__(self, val):
    s = str(val)
    super().__init__(s)

  def __call__(self, program):
    program.push(int(self.symbol))

class InstructionASCII(Instruction):
  def __init__(self, val):
    super().__init__(val)

  def __call__(self, program):
    pass

class InstructionAdd(Instruction):
  def __init__(self):
    super().__init__('+')

  def __call__(self, program):
    if len(program.stack) >= 2:
      a = program.pop()
      b = program.pop()
      program.push(StackValue(a.value + b.value))

class InstructionSub(Instruction):
  def __init__(self):
    super().__init__('-')

  def __call__(self, program):
    if len(program.stack) >= 2:
      a = program.pop()
      b = program.pop()
      program.push(StackValue(b.value - a.value))

class InstructionMult(Instruction):
  def __init__(self):
    super().__init__('*')

  def __call__(self, program):
    if len(program.stack) >= 2:
      a = program.pop()
      b = program.pop()
      program.push(StackValue(a.value * b.value))

class InstructionDiv(Instruction):
  def __init__(self):
    super().__init__('/')

  def __call__(self, program):
    if len(program.stack) >= 2:
      a = program.pop()
      b = program.pop()
      if a.value == 0:
        program.push(StackValue(0))
      else:
        program.push(StackValue(b.value // a.value))

class InstructionMod(Instruction):
  def __init__(self):
    super().__init__('%')

  def __call__(self, program):
    if len(program.stack) >= 2:
      a = program.pop()
      b = program.pop()
      if a.value == 0:
        program.push(StackValue(0))
      else:
        program.push(StackValue(b.value % a.value))

class InstructionNot(Instruction):
  def __init__(self):
    super().__init__('!')

  def __call__(self, program):
    if len(program.stack) >= 1:
      a = program.pop()
      if a.value == 0:
        program.push(StackValue(1))
      else:
        program.push(StackValue(0))

class InstructionHorizontalIf(Instruction):
  def __init__(self):
    super().__init__('_')

  def __call__(self, program):
    if len(program.stack) >= 1:
      a = program.pop()
      if a.value == 0:
        program.facing = Facing.EAST
      else:
        program.facing = Facing.WEST
    else:
      program.facing = Facing.EAST

class InstructionVerticalIf(Instruction):
  def __init__(self):
    super().__init__('|')

  def __call__(self, program):
    if len(program.stack) >= 1:
      a = program.pop()
      if a.value == 0:
        program.facing = Facing.SOUTH
      else:
        program.facing = Facing.NORTH
    else:
      program.facing = Facing.SOUTH

class InstructionDuplicate(Instruction):
  def __init__(self):
    super().__init__(':')

  def __call__(self, program):
    if len(program.stack) >= 1:
      a = program.pop()
      program.push(a)
      program.push(a)

class InstructionSwap(Instruction):
  def __init__(self):
    super().__init__('\\')

  def __call__(self, program):
    if len(program.stack) >= 2:
      a = program.pop()
      b = program.pop()
      program.push(a)
      program.push(b)

class InstructionDiscard(Instruction):
  def __init__(self):
    super().__init__('$')

  def __call__(self, program):
    if len(program.stack) >= 1:
      a = program.pop()

class InstructionPrintInt(Instruction):
  def __init__(self):
    super().__init__('.')

  def __call__(self, program):
    if len(program.stack) >= 1:
      a = program.pop()
      program.output(a.value)

class InstructionPrintASCII(Instruction):
  def __init__(self):
    super().__init__(',')

  def __call__(self, program):
    if len(program.stack) >= 1:
      a = program.pop()
      program.output(chr(a.value))

class InstructionBridge(Instruction):
  def __init__(self):
    super().__init__('#')

  def __call__(self, program):
    program.bridge()

class InstructionGreaterThan(Instruction):
  def __init__(self):
    super().__init__('`')

  def __call__(self, program):
    if len(program.stack) >= 2:
      a = program.pop()
      b = program.pop()
      if b.value > a.value:
        program.push(StackValue(1))
      else:
        program.push(StackValue(0))

class InstructionGet(Instruction):
  def __init__(self):
    super().__init__('g')

  def __call__(self, program):
    if len(program.stack) >= 2:
      row = program.pop().value
      col = program.pop().value
      print(f'Getting from ({row},{col})')
      inst = program.field.get_inst((row,col))
      program.push(inst.symbol)

class InstructionPut(Instruction):
  def __init__(self):
    super().__init__('p')

  def __call__(self, program):
    if len(program.stack) >= 3:
      row = program.pop().value
      col = program.pop().value
      c = chr(program.pop().value)
      print(f'Putting "{c}" at ({row},{col})')
      program.field.field[(row,col)] = GetInstruction(c)

class InstructionGetUserInt(Instruction):
  def __init__(self):
    super().__init__('&')

  def __call__(self, program):
    while True:
      user_input = input('Please enter an integer: ')
      try: 
        user_int = int(user_input)
      except:
        print('Invalid integer. Try again!')
      finally:
        program.push(user_int)
        break

class InstructionGetUserASCII(Instruction):
  def __init__(self):
    super().__init__('~')

  def __call__(self, program):
    while True:
      user_input = input('Please enter an ASCII character: ')
      if len(user_input) != 1:
        print('Invalid character. Try again!')
      else:
        program.push(user_input)
        break

class InstructionStringMode(Instruction):
  def __init__(self):
    super().__init__('"')

  def __call__(self, program):
    program.toggle_stringmode()


def GetInstruction(c):
  inst_map = {}
  inst_map[' '] = InstructionSpace
  inst_map['^'] = InstructionUp
  inst_map['v'] = InstructionDown
  inst_map['<'] = InstructionLeft
  inst_map['>'] = InstructionRight
  inst_map['?'] = InstructionRandom
  inst_map['@'] = InstructionTerminate
  inst_map['+'] = InstructionAdd
  inst_map['-'] = InstructionSub
  inst_map['*'] = InstructionMult
  inst_map['/'] = InstructionDiv
  inst_map['%'] = InstructionMod
  inst_map['!'] = InstructionNot
  inst_map['_'] = InstructionHorizontalIf
  inst_map['|'] = InstructionVerticalIf
  inst_map[':'] = InstructionDuplicate
  inst_map['\\'] = InstructionSwap
  inst_map['$'] = InstructionDiscard
  inst_map['.'] = InstructionPrintInt
  inst_map[','] = InstructionPrintASCII
  inst_map['`'] = InstructionGreaterThan
  inst_map['&'] = InstructionGetUserInt
  inst_map['~'] = InstructionGetUserASCII
  inst_map['"'] = InstructionStringMode
  inst_map['#'] = InstructionBridge
  inst_map['g'] = InstructionGet
  inst_map['p'] = InstructionPut
  arg_map = {}
  for i in range(10):
    i_str = str(i)
    inst_map[i_str] = InstructionInt
    arg_map[i_str] = i
  for i in range(26):
    tmp_char = chr(ord('a') + i)
    if tmp_char not in inst_map:
      inst_map[tmp_char] = InstructionASCII
      arg_map[tmp_char] = tmp_char
  for i in range(26):
    tmp_char = chr(ord('A') + i)
    if tmp_char not in inst_map:
      inst_map[tmp_char] = InstructionASCII
      arg_map[tmp_char] = tmp_char
  if c in arg_map:
    args = arg_map[c]
    return inst_map[c](args)
  else:
    return inst_map[c]()

class Playfield:
  def __init__(self, filename=None):
    self.field = {}
    self.filename = filename
    self.max_col = 0
    self.max_row = 0
    if filename is not None:
      self.load(filename)
 
  def get_inst(self, pos):
    if pos in self.field:
      return self.field[pos]
    else:
      return InstructionSpace()

  def load(self, filename):
    print(f'Loading field from file: {filename}')
    with open(filename, 'r') as fp:
      row = 0
      for line in fp:
        col = 0
        for c in line.rstrip('\n'):
          if c != '':
            self.field[(row, col)] = GetInstruction(c)
            if c != ' ':
              if col > self.max_col:
                self.max_col = col
              if row > self.max_row:
                self.max_row = row
          col += 1
        row += 1

class Facing(enum.Enum):
  NORTH=0
  EAST=1
  SOUTH=2
  WEST=3
  DONE=4

class Program:
  def __init__(self, filename=None):
    self.PC = [0,0]
    self.facing = Facing.EAST
    self.stack = []
    self.field = Playfield(filename)
    self.execution_step = 0
    self.stdout = ''
    self.stringmode = False
    self.run_inst()

  def push(self, val):
    if isinstance(val, StackValue):
      self.stack.append(val)
    else:
      self.stack.append(StackValue(val))

  def pop(self):
    if len(self.stack) > 0:
      return self.stack.pop()


  def move(self):
    if self.facing == Facing.DONE:
      print('Program terminated -- no move to make')
      return None
    elif self.facing == Facing.NORTH:
      self.PC[0] -= 1
    elif self.facing == Facing.EAST:
      self.PC[1] += 1
    elif self.facing == Facing.SOUTH:
      self.PC[0] += 1
    elif self.facing == Facing.WEST:
      self.PC[1] -= 1

  def bridge(self):
    self.move()


  def run_inst(self):
    inst = self.field.get_inst(tuple(self.PC))
    if self.stringmode:
      if inst.symbol == '"':
        inst(self)
      else:
        self.push(inst.symbol)
    else:
      inst(self)
    self.execution_step += 1

  def step(self):
    self.move()
    self.run_inst()

  def toggle_stringmode(self):
    self.stringmode = not self.stringmode

  def output(self, val):
    self.stdout += str(val)
    print(str(val), end='', flush=True)



if __name__ == '__main__':
  if len(sys.argv) > 1:
    p = Program(sys.argv[1])
    while p.facing != Facing.DONE:
      p.step()
  print('')
  print(f'Execution terminated after {p.execution_step} instructions were executed!')

