import enum
import sys
import math
try: 
  import pygame
except ImportError:
  print('Warning: pygame module not found. Cannot visualize befungle execution')
  print('Loaded befungle programs can still be executed, though')

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

class InstructionTerminate(Instruction):
  def __init__(self):
    super().__init__('@')

  def __call__(self, program):
    program.facing = Facing.DONE

def GetInstruction(c):
  inst_map = {}
  inst_map[' '] = InstructionSpace
  inst_map['^'] = InstructionUp
  inst_map['v'] = InstructionDown
  inst_map['<'] = InstructionLeft
  inst_map['>'] = InstructionRight
  inst_map['@'] = InstructionTerminate
  return inst_map[c]()


class Playfield:
  def __init__(self, filename=None):
    self.field = {}
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
            print(f'({row}, {col}) -> {c}')
            self.field[(row, col)] = GetInstruction(c)
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

  def step(self):
    if self.facing == Facing.DONE:
      print('Program terminated')
    elif self.facing == Facing.NORTH:
      self.PC[0] -= 1
    elif self.facing == Facing.EAST:
      self.PC[1] += 1
    elif self.facing == Facing.SOUTH:
      self.PC[0] += 1
    elif self.facing == Facing.WEST:
      self.PC[1] -= 1
    inst = self.field.get_inst(tuple(self.PC))
    inst(self)

class PygameVisualizer:
  def __init__(self, program, **kwargs):
    if 'pygame' not in sys.modules: # Source: https://stackoverflow.com/a/30483269 
      print('Error! Cannot launch pygame visualizer, pygame module was not found!', file = sys.stderr)
      print('If you wish to visualize, install it with "python3 -m pip install pygame-ce"')
      raise ImportError('pygame module not found')
    self.program = program
    pygame.init()
    self.screen_res = [800, 600]
    for key in kwargs:
      if key == 'screen_width':
        self.screen_res[0] = kwargs[key]
      if key == 'screen_height':
        self.screen_res[1] = kwargs[key]
    self.screen = pygame.display.set_mode(self.screen_res)
    self.pixel_offset = [self.screen_res[0] // 2, self.screen_res[1] // 2]
    self.tile_size = 32
    self.max_timer_ticks = 6
    self.timer_ticks = self.max_timer_ticks

  def run(self):
    self.clock = pygame.time.Clock()
    self.is_running = True
    self.is_paused = True
    while self.is_running:
      self.handle_input()
      if not self.is_paused:
        self.timer_ticks -= 1
        if self.timer_ticks <= 0:
          self.timer_ticks = self.max_timer_ticks
          self.step()
      self.render()
      self.clock.tick(60)

  def handle_input(self):
    for evt in pygame.event.get():
      if evt.type == pygame.QUIT:
        self.is_running = False
      elif evt.type == pygame.KEYDOWN:
        if evt.key == pygame.K_ESCAPE or evt.key == pygame.K_q:
          self.is_running = False
        elif evt.key == pygame.K_SPACE and self.is_paused:
          self.step()
        elif evt.key == pygame.K_p:
          self.is_paused = not self.is_paused
        elif evt.key == pygame.K_MINUS:
          self.tile_size -= 1
        elif evt.key == pygame.K_PLUS or evt.key == pygame.K_EQUALS:
          self.tile_size += 1
        elif evt.key == pygame.K_LEFTBRACKET:
          self.max_timer_ticks = max(self.max_timer_ticks - 1, 1)
        elif evt.key == pygame.K_RIGHTBRACKET:
          self.max_timer_ticks += 1
    pressed_keys = pygame.key.get_pressed()
    offset = 1
    if pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]:
      offset = 5
    if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]:
      self.pixel_offset[1] += offset
    elif pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]:
      self.pixel_offset[1] -= offset
    if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
      self.pixel_offset[0] += offset
    elif pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
      self.pixel_offset[0] -= offset

  def step(self):
    self.program.step()

  def render(self):
    self.screen.fill((0,0,0))
    # Draw the origin for reference
    origin_x = self.pixel_offset[0]
    origin_y = self.pixel_offset[1]
    origin_radius = self.tile_size // 2 - 2
    pygame.draw.circle(self.screen, (80, 80, 80), (origin_x, origin_y), origin_radius) 
    # Draw the grid lines
    tl_cell_x = math.floor((-1 * self.pixel_offset[0] + self.tile_size // 2) / self.tile_size)
    tl_cell_y = math.floor((-1 * self.pixel_offset[1] + self.tile_size // 2) / self.tile_size)
    tl_x = origin_x + (tl_cell_x * self.tile_size) - self.tile_size // 2
    tl_y = origin_y + (tl_cell_y * self.tile_size) - self.tile_size // 2
    #pygame.draw.rect(self.screen, (200, 200, 200), (tl_x, tl_y, self.tile_size, self.tile_size))
    num_cols = math.ceil(self.screen_res[0] / self.tile_size) + 1
    num_rows = math.ceil(self.screen_res[1] / self.tile_size) + 1
    for col_idx in range(num_cols):
      col_cell_x = tl_cell_x + col_idx
      col_x = origin_x + (col_cell_x * self.tile_size - self.tile_size // 2)
      pygame.draw.line(self.screen, (30, 30, 30), (col_x, 0), (col_x, self.screen_res[1]), 1)
    for row_idx in range(num_rows):
      row_cell_y = tl_cell_y + row_idx
      row_y = origin_y + (row_cell_y * self.tile_size - self.tile_size // 2)
      pygame.draw.line(self.screen, (30, 30, 30), (0, row_y), (self.screen_res[0], row_y), 1)

    # Draw the tiles
    font = pygame.font.SysFont(None, self.tile_size)
    min_col = tl_cell_x
    max_col = tl_cell_x + num_cols
    min_row = tl_cell_y
    max_row = tl_cell_y + num_rows
    for row in range(min_row, max_row + 1):
      for col in range(min_col, max_col + 1):
        address = (row, col)
        inst = self.program.field.get_inst(address)
        if inst.symbol == ' ':
          continue
        text_surf = font.render(inst.symbol, False, (255,255,255))
        text_rect = text_surf.get_rect()
        text_rect.centerx = origin_x + (col * self.tile_size)
        text_rect.centery = origin_y + (row * self.tile_size)
        self.screen.blit(text_surf, text_rect)
    # Draw the program counter
    pc_x = origin_x + self.program.PC[1] * self.tile_size
    pc_y = origin_y + self.program.PC[0] * self.tile_size
    if self.program.facing == Facing.EAST:
      nose = (pc_x + self.tile_size // 8 * 3, pc_y)
      tl = (pc_x - self.tile_size // 4, pc_y - self.tile_size // 6)
      bl = (pc_x - self.tile_size // 4, pc_y + self.tile_size // 6)
      pygame.draw.polygon(self.screen, (200, 30, 80), [nose, tl, bl])
    elif self.program.facing == Facing.WEST:
      nose = (pc_x - self.tile_size // 8 * 3, pc_y)
      tr = (pc_x + self.tile_size // 4, pc_y - self.tile_size // 6)
      br = (pc_x + self.tile_size // 4, pc_y + self.tile_size // 6)
      pygame.draw.polygon(self.screen, (200, 30, 80), [nose, tr, br])
    elif self.program.facing == Facing.SOUTH:
      nose = (pc_x, pc_y + self.tile_size // 8 * 3)
      tl = (pc_x - self.tile_size // 6, pc_y - self.tile_size // 4)
      tr = (pc_x + self.tile_size // 6, pc_y - self.tile_size // 4)
      pygame.draw.polygon(self.screen, (200, 30, 80), [nose, tl, tr])
    elif self.program.facing == Facing.NORTH:
      nose = (pc_x, pc_y - self.tile_size // 8 * 3)
      bl = (pc_x - self.tile_size // 6, pc_y + self.tile_size // 4)
      br = (pc_x + self.tile_size // 6, pc_y + self.tile_size // 4)
      pygame.draw.polygon(self.screen, (200, 30, 80), [nose, bl, br])
    elif self.program.facing == Facing.DONE:
      pygame.draw.circle(self.screen, (200, 30, 80), (pc_x, pc_y), self.tile_size // 3)
   
    


    pygame.display.flip()

if __name__ == '__main__':
  if len(sys.argv) > 1:
    p = Program(sys.argv[1])
  else:
    p = Program()
    p.field.field[(0,0)] = InstructionRight()
    p.field.field[(0,3)] = InstructionDown()
    p.field.field[(3,3)] = InstructionLeft()
    p.field.field[(3,0)] = InstructionUp()
  viz = PygameVisualizer(p)#, screen_width=100)
  viz.run()

