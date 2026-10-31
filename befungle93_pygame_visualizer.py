import sys
import math
import befungle93_interpreter as bf93
try: 
  import pygame
except ImportError:
  print('Error: pygame module not found. Cannot visualize befungle execution')
  print('Loaded befungle programs can still be executed using befungle93_interpreter.py instead')
  print('If you want to use this visualizer, install pygame with:')
  print('python3 -m pip install pygame-ce')
  sys.exit(1)

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
    self.pixel_offset = [0,0]#[self.screen_res[0] // 2, self.screen_res[1] // 2]
    self.tile_size = 32
    self.max_timer_ticks = 6
    self.timer_ticks = self.max_timer_ticks
    self.info_pane_width = self.screen_res[0] // 4
    if self.program.field.filename is not None:
      max_col = self.program.field.max_col
      max_row = self.program.field.max_row
      print(f'Found {max_row} rows and {max_col} columns!')
      width_pixels = self.screen_res[0] - self.info_pane_width
      tile_size_col = width_pixels // (max_col+2)
      tile_size_row = self.screen_res[1] // (max_row+2)
      self.tile_size = min(tile_size_col, tile_size_row)
      self.pixel_offset = [self.tile_size, self.tile_size]

  def run(self):
    self.clock = pygame.time.Clock()
    self.is_running = True
    self.is_paused = True
    self.is_following = False
    while self.is_running:
      self.handle_input()
      if not self.is_paused:
        self.timer_ticks -= 1
        if self.timer_ticks <= 0:
          self.timer_ticks = self.max_timer_ticks
          self.step()
          if self.program.facing == bf93.Facing.DONE:
            self.is_paused = True
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
        elif evt.key == pygame.K_f:
          self.is_following = not self.is_following
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
    if self.is_following:
      grid_width = self.screen_res[0] - self.info_pane_width
      x = -self.program.PC[1] * self.tile_size + grid_width // 2
      y = -self.program.PC[0] * self.tile_size + self.screen_res[1] // 2
      self.pixel_offset = [x, y]
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
    num_cols = math.ceil((self.screen_res[0] - self.info_pane_width) / self.tile_size) + 1
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
    if self.program.facing == bf93.Facing.EAST:
      nose = (pc_x + self.tile_size // 8 * 3, pc_y)
      tl = (pc_x - self.tile_size // 4, pc_y - self.tile_size // 6)
      bl = (pc_x - self.tile_size // 4, pc_y + self.tile_size // 6)
      pygame.draw.polygon(self.screen, (200, 30, 80), [nose, tl, bl])
    elif self.program.facing == bf93.Facing.WEST:
      nose = (pc_x - self.tile_size // 8 * 3, pc_y)
      tr = (pc_x + self.tile_size // 4, pc_y - self.tile_size // 6)
      br = (pc_x + self.tile_size // 4, pc_y + self.tile_size // 6)
      pygame.draw.polygon(self.screen, (200, 30, 80), [nose, tr, br])
    elif self.program.facing == bf93.Facing.SOUTH:
      nose = (pc_x, pc_y + self.tile_size // 8 * 3)
      tl = (pc_x - self.tile_size // 6, pc_y - self.tile_size // 4)
      tr = (pc_x + self.tile_size // 6, pc_y - self.tile_size // 4)
      pygame.draw.polygon(self.screen, (200, 30, 80), [nose, tl, tr])
    elif self.program.facing == bf93.Facing.NORTH:
      nose = (pc_x, pc_y - self.tile_size // 8 * 3)
      bl = (pc_x - self.tile_size // 6, pc_y + self.tile_size // 4)
      br = (pc_x + self.tile_size // 6, pc_y + self.tile_size // 4)
      pygame.draw.polygon(self.screen, (200, 30, 80), [nose, bl, br])
    elif self.program.facing == bf93.Facing.DONE:
      pygame.draw.circle(self.screen, (200, 30, 80), (pc_x, pc_y), self.tile_size // 3)
   
    self.draw_info_pane()
    pygame.display.flip()

  def draw_info_pane(self):
    info_font = pygame.font.SysFont(None, 20)
    start_x = self.screen_res[0] - self.info_pane_width
    pygame.draw.rect(self.screen, (0,0,0), (start_x, 0, self.info_pane_width, self.screen_res[1]))
    pygame.draw.line(self.screen, (255,255,255), (start_x, 0), (start_x, self.screen_res[1]))

    indent = 10
    line_height = 24
    cur_y = 5
    # Draw header
    text_surf = info_font.render('INFO', True, (255,255,255))
    text_rect = text_surf.get_rect()
    text_rect.centerx = (start_x + self.info_pane_width // 2)
    text_rect.top = cur_y
    self.screen.blit(text_surf, text_rect)
    cur_y += line_height
    # Count execution steps
    text_surf = info_font.render(f'Steps: {self.program.execution_step}', True, (255,255,255))
    text_rect = text_surf.get_rect()
    text_rect.topleft = (start_x + indent, cur_y)
    self.screen.blit(text_surf, text_rect)
    cur_y += line_height
    # Display stdout
    text_surf = info_font.render(f'stdout: {self.program.stdout}', True, (255,255,255))
    text_rect = text_surf.get_rect()
    text_rect.topleft = (start_x + indent, cur_y)
    self.screen.blit(text_surf, text_rect)
    cur_y += line_height
    # Draw stack
    text_surf = info_font.render('Stack:', True, (255,255,255))
    text_rect = text_surf.get_rect()
    text_rect.topleft = (start_x + indent, cur_y)
    self.screen.blit(text_surf, text_rect)
    cur_y += line_height
    stack_vals = self.program.stack
    if len(stack_vals) > 0:
      for stack_idx in range(len(stack_vals) -1, -1, -1):
        stack_val = stack_vals[stack_idx]
        text_surf = info_font.render(str(stack_val.value), True, (255,255,255))
        text_rect = text_surf.get_rect()
        text_rect.topleft = (start_x + indent + indent, cur_y)
        self.screen.blit(text_surf, text_rect)
        cur_y += line_height


if __name__ == '__main__':
  if len(sys.argv) > 1:
    p = bf93.Program(sys.argv[1])
    viz = PygameVisualizer(p)
    viz.run()

