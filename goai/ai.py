# SimpleAI：只在存在合法着法时返回一个 (r, c)；若无合法着法返回 None
import random
from .board import Board, EMPTY, BLACK, WHITE

class SimpleAI:
    def __init__(self, level=0):
        self.level = level

    def select_move(self, board: Board, color):
        """
        返回一个合法落子 (r, c)，若没有合法着法返回 None（表示无法下子）。
        AI 不会返回“pass”作为着法。
        """
        legal_moves = []
        for r in range(board.size):
            for c in range(board.size):
                if board.grid[r][c] == EMPTY and board.is_legal(r, c, color):
                    legal_moves.append((r, c))
        if not legal_moves:
            return None
        # 简单随机策略；未来可按启发式排序
        return random.choice(legal_moves)