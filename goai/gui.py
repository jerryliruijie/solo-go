"""
GUI: 使用 GameManager，不包含 Pass 功能。若一方无合法着法则结束对局（弹窗提示）。
"""
import tkinter as tk
from tkinter import messagebox
import threading
import time

from .board import Board, EMPTY, BLACK, WHITE
from .ai import SimpleAI
from .game_manager import GameManager
from .sound import play_move_sound

CELL_SIZE = 30
MARGIN = 25
STONE_RADIUS = CELL_SIZE // 2 - 2
AI_THINK_TIME = 0.5

class GoGUI(tk.Frame):
    def __init__(self, master=None, board_size=19, ai_level=0):
        super().__init__(master)
        self.master = master
        self.board_size = board_size
        self.ai = SimpleAI(level=ai_level)
        # 默认人执黑；若需要人执白可在创建后改属性并手动触发 AI 先行
        self.game = GameManager(size=board_size, ai=self.ai, human_color=BLACK)

        self.master.title("Solo-Go: GUI vs SimpleAI")
        canvas_size = 2 * MARGIN + CELL_SIZE * (board_size - 1)
        self.canvas = tk.Canvas(self.master, width=canvas_size, height=canvas_size, bg="#DDB87A")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)
        self.status = tk.Label(self.master, text=self._status_text(), anchor="w")
        self.status.pack(fill="x")
        # 去掉 Pass 按钮（用户要求）
        self.reset_button = tk.Button(self.master, text="Reset", command=self.on_reset)
        self.reset_button.pack(side="right")
        self.draw_board()
        self.draw_stones()
        # 若 AI 先行（人执白），则触发 AI
        if not self.game.is_human_turn():
            self.after(100, self.ai_move)

    def _status_text(self):
        who = "Black" if self.game.to_move == BLACK else "White"
        you = "Black" if self.game.human_color == BLACK else "White"
        return f"To move: {who}    (You are {you})"

    def draw_board(self):
        self.canvas.delete("grid")
        size = self.board_size
        for i in range(size):
            x0 = MARGIN + i * CELL_SIZE
            y0 = MARGIN
            x1 = x0
            y1 = MARGIN + (size - 1) * CELL_SIZE
            self.canvas.create_line(x0, y0, x1, y1, width=2, tags="grid")
            x0 = MARGIN
            y0 = MARGIN + i * CELL_SIZE
            x1 = MARGIN + (size - 1) * CELL_SIZE
            y1 = y0
            self.canvas.create_line(x0, y0, x1, y1, width=2, tags="grid")
        if size in (9,13,19):
            pts = []
            if size == 9:
                pts = [(2,2),(2,6),(6,2),(6,6),(4,4)]
            elif size == 13:
                pts = [(3,3),(3,9),(9,3),(9,9),(6,6)]
            else:
                pts = [(3,3),(3,9),(3,15),
                       (9,3),(9,9),(9,15),
                       (15,3),(15,9),(15,15)]
            for (r,c) in pts:
                x = MARGIN + c * CELL_SIZE
                y = MARGIN + r * CELL_SIZE
                self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="black", tags="grid")

    def draw_stones(self):
        self.canvas.delete("stones")
        for r in range(self.board_size):
            for c in range(self.board_size):
                val = self.game.board.grid[r][c]
                if val == EMPTY:
                    continue
                x = MARGIN + c * CELL_SIZE
                y = MARGIN + r * CELL_SIZE
                color = "black" if val == BLACK else "white"
                self.canvas.create_oval(x - STONE_RADIUS, y - STONE_RADIUS,
                                        x + STONE_RADIUS, y + STONE_RADIUS,
                                        fill=color, outline="black", tags="stones")
        self.status.config(text=self._status_text())

    def on_click(self, event):
        # defensive: if game ended ignore clicks
        if self.game.result != GameManagerResultSafe.ONGOING:
            return
        x = event.x
        y = event.y
        c = int(round((x - MARGIN) / CELL_SIZE))
        r = int(round((y - MARGIN) / CELL_SIZE))
        if r < 0 or r >= self.board_size or c < 0 or c >= self.board_size:
            return
        if not self.game.is_human_turn():
            return
        ok, msg = self.game.make_human_move(r, c)
        if not ok:
            # 非法或失败，闪红叉并返回消息
            self.flash_illegal(r, c)
            if msg:
                messagebox.showinfo("Move failed", msg)
            return
        # Play move sound for human move
        try:
            play_move_sound(master=self.master)
        except Exception:
            pass
        # 更新界面
        self.draw_stones()
        # 检查是否对局结束
        if self.game.result != GameManagerResultSafe.ONGOING:
            self._announce_result_and_disable()
            return
        # 若现在轮到 AI，则触发 AI
        if not self.game.is_human_turn():
            self.after(100, self.ai_move)

    def ai_move(self):
        def run():
            time.sleep(AI_THINK_TIME)
            if self.game.result != GameManagerResultSafe.ONGOING:
                return
            moved, msg = self.game.make_ai_move()
            # Update UI on main thread
            self.after(1, self.draw_stones)
            if moved:
                # Play move sound for AI move
                try:
                    play_move_sound(master=self.master)
                except Exception:
                    pass
            if not moved and msg:
                # AI 无法下法 -> 对局结束（AI 投降）
                self.after(50, lambda: messagebox.showinfo("Game over", msg))
                return
            # 若对局结束由 make_ai_move 设置了 result
            if self.game.result != GameManagerResultSafe.ONGOING:
                self.after(50, self._announce_result_and_disable)
                return
        t = threading.Thread(target=run, daemon=True)
        t.start()

    def _announce_result_and_disable(self):
        # 显示结果并禁止继续下子
        winner_text = self.game.get_winner_text()
        messagebox.showinfo("Game Over", winner_text)
        # disable further interaction by unbinding clicks
        self.canvas.unbind("<Button-1>")

    def flash_illegal(self, r, c):
        x = MARGIN + c * CELL_SIZE
        y = MARGIN + r * CELL_SIZE
        tag = "illegal"
        self.canvas.create_line(x-12, y-12, x+12, y+12, fill="red", width=3, tags=tag)
        self.canvas.create_line(x-12, y+12, x+12, y-12, fill="red", width=3, tags=tag)
        self.master.after(300, lambda: self.canvas.delete(tag))

    def on_reset(self):
        if messagebox.askyesno("Reset", "Start a new game?"):
            self.game = GameManager(size=self.board_size, ai=self.ai, human_color=self.game.human_color)
            self.draw_board()
            self.draw_stones()
            # rebind clicks
            self.canvas.bind("<Button-1>", self.on_click)
            if not self.game.is_human_turn():
                self.after(100, self.ai_move)

# small compatibility helpers (so GUI references GameManagerResultSafe)
class GameManagerResultSafe:
    ONGOING = "ongoing"
    BLACK_WINS = "black_wins"
    WHITE_WINS = "white_wins"
    DRAW = "draw"

def main():
    root = tk.Tk()
    gui = GoGUI(master=root, board_size=19, ai_level=0)
    gui.pack()
    root.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()

if __name__ == "__main__":
    main()