from goai.ai import SimpleAI
from goai.game_manager import GameManager, GameResult
from goai.board import Board, EMPTY, BLACK, WHITE

def test_human_move_and_turn_switch():
    ai = SimpleAI()
    gm = GameManager(size=5, ai=ai, human_color=BLACK)
    assert gm.is_human_turn() is True
    ok, msg = gm.make_human_move(2,2)
    assert ok is True
    # after human move it should switch to AI
    assert gm.is_human_turn() is False

def test_game_ends_when_player_has_no_moves():
    # Use 1x1 board where suicide is illegal -> there are no legal moves for either side.
    ai = SimpleAI()
    gm = GameManager(size=1, ai=ai, human_color=BLACK)
    # On a 1x1 board with suicide forbidden, black has no legal moves at start
    moves_black = gm.legal_moves_for(BLACK)
    assert moves_black == []
    # If human tries to move it should fail
    ok, msg = gm.make_human_move(0,0)
    assert ok is False
    # If it's AI's turn and AI also cannot move, make_ai_move should mark result appropriately.
    gm.to_move = gm.ai_color
    moved, msg = gm.make_ai_move()
    # Since no moves exist for AI either, moved should be False and result should indicate winner
    assert moved is False
    assert gm.result in (GameResult.BLACK_WINS, GameResult.WHITE_WINS)

def test_ai_illegal_return_triggers_loss():
    # Create a mock AI that returns an illegal move to force loss.
    class BadAI:
        def select_move(self, board, color):
            # deliberately return an occupied position to trigger failure path
            return (0, 0)
    bad_ai = BadAI()
    gm = GameManager(size=1, ai=bad_ai, human_color=BLACK)
    # Simulate occupied point by directly setting grid (place would reject due to suicide rule)
    gm.board.grid[0][0] = BLACK
    # switch to AI
    gm.to_move = gm.ai_color
    moved, msg = gm.make_ai_move()
    assert moved is False
    # human should be declared winner because AI made illegal move
    assert gm.result in (GameResult.BLACK_WINS, GameResult.WHITE_WINS)