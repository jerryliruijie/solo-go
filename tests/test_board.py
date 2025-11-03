from goai.board import Board, BLACK, WHITE

def test_capture():
    b = Board(5)
    b.place(2, 2, WHITE)
    b.place(1, 2, BLACK)
    b.place(3, 2, BLACK)
    b.place(2, 1, BLACK)
    assert b.place(2, 3, BLACK)
    # 白子应该被吃掉
    assert b.grid[2][2] == 0
