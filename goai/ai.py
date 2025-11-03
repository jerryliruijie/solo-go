import random
from .board import Board, EMPTY, BLACK, WHITE

class SimpleAI:
    def __init__(self, level=0):
        self.level = level

    def select_move(self, board: Board, color):
        """随机选择一个空位下棋"""
        empties = [(r, c) for r in range(board.size) for c in range(board.size)
                   if board.grid[r][c] == EMPTY]
        if not empties:
            return None
        return random.choice(empties)
