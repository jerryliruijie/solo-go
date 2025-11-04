import pytest
from goai.board import Board, EMPTY, BLACK, WHITE

def test_place_and_capture_simple():
    # 3x3 局面方便构造提子
    b = Board(size=3)
    # place black at (1,1)
    assert b.is_legal(1, 1, BLACK)
    assert b.place(1, 1, BLACK) is True
    # surround black with whites at (0,1),(1,0),(1,2),(2,1) -> black should be captured after last white
    assert b.place(0, 1, WHITE) is True
    assert b.place(1, 0, WHITE) is True
    assert b.place(1, 2, WHITE) is True
    # last surrounding move
    assert b.place(2, 1, WHITE) is True
    # black stone at (1,1) should be removed (captured)
    assert b.grid[1][1] == EMPTY

def test_suicide_not_allowed():
    b = Board(size=3)
    # create white stones around (1,1) leaving no liberties
    assert b.place(0,1,WHITE)
    assert b.place(1,0,WHITE)
    assert b.place(1,2,WHITE)
    assert b.place(2,1,WHITE)
    # Now black trying to play at (1,1) would be suicide unless it captures (it doesn't)
    assert b.is_legal(1,1,BLACK) is False
    assert b.place(1,1,BLACK) is False

def test_liberty_count_and_group_behavior():
    b = Board(size=5)
    # build a black chain at (1,1) and (1,2)
    assert b.place(1,1,BLACK)
    assert b.place(1,2,BLACK)
    # place whites to reduce liberties
    assert b.place(0,1,WHITE)
    assert b.place(0,2,WHITE)
    # still should have liberties; not captured yet
    assert b.grid[1][1] == BLACK
    assert b.grid[1][2] == BLACK

def test_illegal_on_occupied_point():
    b = Board(size=5)
    assert b.place(2,2,BLACK)
    assert b.is_legal(2,2,WHITE) is False
    assert b.place(2,2,WHITE) is False