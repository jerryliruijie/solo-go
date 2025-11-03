from .board import Board, BLACK, WHITE
from .ai import SimpleAI

class Game:
    def __init__(self, size=9):
        self.board = Board(size)
        self.ai = SimpleAI(level=0)
        self.to_move = BLACK

    def play(self, row, col):
        ok = self.board.place(row, col, self.to_move)
        if not ok:
            print("Invalid move!")
            return False
        self.to_move = WHITE if self.to_move == BLACK else BLACK
        return True

    def ai_move(self):
        move = self.ai.select_move(self.board, self.to_move)
        if move:
            r, c = move
            self.board.place(r, c, self.to_move)
            print(f"AI plays {chr(ord('A') + c)}{self.board.size - r}")
            self.to_move = WHITE if self.to_move == BLACK else BLACK
