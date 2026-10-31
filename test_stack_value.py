import pytest
import bungle93_pygame as b93pg

def test_stack_value_init_good__int_pos():
  sv = b93pg.StackValue(1)
  assert sv.value == 1

def test_stack_value_init_good__int_neg():
  sv = b93pg.StackValue(-2)
  assert sv.value == -2

def test_stack_value_init_good__int_zero():
  sv = b93pg.StackValue(0)
  assert sv.value == 0

def test_stack_value_init_good__char():
  sv = b93pg.StackValue('F')
  assert sv.value == 70

def test_stack_value_init__good__true():
  sv = b93pg.StackValue(True)
  assert sv.value == 1
  assert isinstance(sv.value, int)
  assert not isinstance(sv.value, bool)

def test_stack_value_init__good__false():
  sv = b93pg.StackValue(False)
  assert sv.value == 0
  assert isinstance(sv.value, int)
  assert not isinstance(sv.value, bool)

def test_stack_value_init__bad__long_str():
  with pytest.raises(ValueError):
    sv = b93pg.StackValue('hi')

def test_stack_value_init__bad__empty_str():
  with pytest.raises(ValueError):
    sv = b93pg.StackValue('')

def test_stack_value_init__bad__list():
  with pytest.raises(TypeError):
    sv = b93pg.StackValue([23])
