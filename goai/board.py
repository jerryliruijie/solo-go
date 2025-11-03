# goai/board.py
EMPTY, BLACK, WHITE = 0, 1, -1

class Board:
    def __init__(self, size=9):
        self.size = size
        self.grid = [[EMPTY for _ in range(size)] for _ in range(size)]

    # ---------- 基础工具 ----------
    def in_bounds(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size

    def neighbors(self, r, c):
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            rr, cc = r + dr, c + dc
            if self.in_bounds(rr, cc):
                yield rr, cc

    def _group_and_liberties(self, r, c):
        """从 (r,c) 出发求整块及其气集合。返回 (stones_set, liberties_set)。"""
        color = self.grid[r][c]
        assert color != EMPTY
        stack = [(r, c)]
        stones = {(r, c)}
        liberties = set()
        while stack:
            x, y = stack.pop()
            for nx, ny in self.neighbors(x, y):
                v = self.grid[nx][ny]
                if v == EMPTY:
                    liberties.add((nx, ny))
                elif v == color and (nx, ny) not in stones:
                    stones.add((nx, ny))
                    stack.append((nx, ny))
        return stones, liberties

    # ---------- 合法性判定 ----------
    def is_legal(self, row, col, color):
        """判断把 `color` 落在 (row,col) 是否合法（包含提子与自杀判定）。"""
        if not self.in_bounds(row, col):
            return False
        if self.grid[row][col] != EMPTY:
            return False

        # 在一个临时拷贝上模拟此手（先落子→提掉对方无气的块→看己方是否仍无气）
        temp = self._copy()
        temp.grid[row][col] = color

        # 提掉相邻敌块（若无气）
        captured = 0
        for nx, ny in temp.neighbors(row, col):
            if temp.grid[nx][ny] == -color:
                stones, libs = temp._group_and_liberties(nx, ny)
                if not libs:
                    for (sx, sy) in stones:
                        temp.grid[sx][sy] = EMPTY
                    captured += len(stones)

        # 检查己方这块是否有气；若没有且没有提子，则为自杀手→非法
        stones, libs = temp._group_and_liberties(row, col)
        if not libs and captured == 0:
            return False
        return True

    # ---------- 实际落子（含提子） ----------
    def place(self, row, col, color):
        """
        执行一手棋：若非法返回 False；合法则真实落子并完成提子，返回 True。
        （不实现劫规则；后续需要可以在此添加 ko 处理）
        """
        if not self.is_legal(row, col, color):
            return False

        # 真正落子
        self.grid[row][col] = color

        # 提掉相邻敌块（若无气）
        for nx, ny in list(self.neighbors(row, col)):
            if self.grid[nx][ny] == -color:
                stones, libs = self._group_and_liberties(nx, ny)
                if not libs:
                    for (sx, sy) in stones:
                        self.grid[sx][sy] = EMPTY
        return True

    # ---------- 显示 ----------
    def display(self):
        header = "   " + " ".join([chr(ord('A') + i) for i in range(self.size)])
        print(header)
        for r in range(self.size):
            row_cells = [self._symbol(self.grid[r][c]) for c in range(self.size)]
            print(f"{self.size - r:2} " + " ".join(row_cells))
        print()

    def _symbol(self, v):
        if v == BLACK:
            return "●"
        if v == WHITE:
            return "○"
        return "+"

    # ---------- 内部：浅拷贝 ----------
    def _copy(self):
        b = Board(self.size)
        b.grid = [row[:] for row in self.grid]
        return b
