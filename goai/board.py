EMPTY, BLACK, WHITE = 0, 1, -1

class Board:
    def __init__(self, size=9):
        self.size = size
        self.grid = [[EMPTY for _ in range(size)] for _ in range(size)]

    def place(self, row, col, color):
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False
        if self.grid[row][col] != EMPTY:
            return False
        self.grid[row][col] = color
        return True

    def display(self):
        print("   " + " ".join([chr(ord('A') + i) for i in range(self.size)]))
        for i in range(self.size):
            row = [self.symbol(self.grid[i][j]) for j in range(self.size)]
            print(f"{self.size - i:2} " + " ".join(row))
        print()

    def symbol(self, v):
        if v == BLACK:
            return "●"
        elif v == WHITE:
            return "○"
        else:
            return "+"

if __name__ == "__main__":
    b = Board(9)
    b.place(4, 4, BLACK)
    b.place(3, 4, WHITE)
    b.display()
