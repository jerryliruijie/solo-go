import pytest
from goai.ai import SimpleAI
from goai.board import Board, EMPTY, BLACK, WHITE

def test_ai_returns_legal_move_on_empty_board():
    b = Board(size=5)
    ai = SimpleAI()
    move = ai.select_move(b, BLACK)
    # on empty board AI should return some coordinate tuple or None if no legal moves
    # We assert that if a move is returned, it is within bounds and legal.
    if move is None:
        # It's acceptable if board rules (e.g. suicide forbidden) produce no legal moves in rare configs,
        # but on a 5x5 empty board that should not happen.
        pytest.fail("AI returned None on empty 5x5 board")
    r,c = move
    assert 0 <= r < b.size and 0 <= c < b.size
    assert b.is_legal(r,c,BLACK)

def test_ai_returns_none_when_no_moves():
    # On a 1x1 board with suicide illegal there are no legal moves for either color.
    b = Board(size=1)
    ai = SimpleAI()
    move = ai.select_move(b, BLACK)
    assert move is None