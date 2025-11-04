# GameManager: 管理回合、落子、胜负判定（当一方无法下法时视为认输/结束）
from .board import Board, EMPTY, BLACK, WHITE

class GameResult:
    ONGOING = "ongoing"
    BLACK_WINS = "black_wins"
    WHITE_WINS = "white_wins"
    DRAW = "draw"

class GameManager:
    def __init__(self, size=19, ai=None, human_color=BLACK):
        """
        ai: SimpleAI 实例或 None（如果不需要 AI）
        human_color: BLACK 或 WHITE，表示玩家执子颜色
        """
        self.board = Board(size=size)
        self.size = size
        self.to_move = BLACK  # 黑先
        self.ai = ai
        self.human_color = human_color
        self.ai_color = WHITE if human_color == BLACK else BLACK
        self.result = GameResult.ONGOING

    def is_human_turn(self):
        return self.to_move == self.human_color

    def legal_moves_for(self, color):
        moves = []
        for r in range(self.size):
            for c in range(self.size):
                if self.board.grid[r][c] == EMPTY and self.board.is_legal(r, c, color):
                    moves.append((r, c))
        return moves

    def make_human_move(self, r, c):
        """
        尝试让人类下子，返回 (ok, message)
        ok: bool 是否成功落子
        message: 失败原因或空字符串；若落子成功且导致对局结束，message 可包含提示
        """
        if self.result != GameResult.ONGOING:
            return False, "对局已结束"
        if not self.is_human_turn():
            return False, "现在不是你下子"
        if not self.board.is_legal(r, c, self.human_color):
            return False, "不合法着法"
        ok = self.board.place(r, c, self.human_color)
        if not ok:
            return False, "落子失败"
        # 切换执子方并检查对手是否有合法着法
        self.to_move = BLACK if self.to_move == WHITE else WHITE
        self._check_game_over_after_move()
        return True, ""

    def make_ai_move(self):
        """
        调用 AI 选着并落子；若 AI 无合法着法（AI.select_move 返回 None 或无合法落子），
        则视为 AI 无法下子 -> 认输 / 对局结束（由 self.result 标记）。
        返回 (moved: bool, message: str)
        """
        if self.result != GameResult.ONGOING:
            return False, "对局已结束"
        if self.is_human_turn():
            return False, "现在不是 AI 下子"
        if self.ai is None:
            return False, "无 AI"
        move = self.ai.select_move(self.board, self.ai_color)
        if move is None:
            # AI 无合法着法，视为 AI 投子/认输 => 人类获胜
            self.result = GameResult.BLACK_WINS if self.human_color == BLACK else GameResult.WHITE_WINS
            return False, "AI 无合法着法，认输。你获胜。"
        r, c = move
        if not self.board.is_legal(r, c, self.ai_color):
            # 保险：若 AI 返回非法着法，视为认输
            self.result = GameResult.BLACK_WINS if self.human_color == BLACK else GameResult.WHITE_WINS
            return False, "AI 返回非法着法，认输。你获胜。"
        ok = self.board.place(r, c, self.ai_color)
        if not ok:
            # 不应发生，但若发生，AI 认输
            self.result = GameResult.BLACK_WINS if self.human_color == BLACK else GameResult.WHITE_WINS
            return False, "AI 无法落子，认输。你获胜。"
        # 切换回合，检查是否人类还有合法着法；如果人无合法着法则人类认输
        self.to_move = BLACK if self.to_move == WHITE else WHITE
        self._check_game_over_after_move()
        return True, ""

    def _check_game_over_after_move(self):
        """
        在每次成功落子并切换执子后检查对方是否有合法着法。
        若对方无合法着法，则视为该方无法继续 -> 此方获胜（按照用户要求不允许 pass）。
        """
        if self.result != GameResult.ONGOING:
            return
        next_color = self.to_move
        has_move = len(self.legal_moves_for(next_color)) > 0
        if not has_move:
            # 下一方无法下子 -> 轮到下一方但无子：下一方认输，当前执子方获胜
            winner = BLACK if next_color == WHITE else WHITE
            if winner == BLACK:
                self.result = GameResult.BLACK_WINS
            else:
                self.result = GameResult.WHITE_WINS

    def get_winner_text(self):
        if self.result == GameResult.BLACK_WINS:
            return "Black wins"
        if self.result == GameResult.WHITE_WINS:
            return "White wins"
        if self.result == GameResult.DRAW:
            return "Draw"
        return "Ongoing"