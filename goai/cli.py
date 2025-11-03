from goai.game import Game, BLACK, WHITE

def main():
    game = Game(size=9)
    print("Welcome to Solo-Go!")
    print("Enter your move (e.g. D4) or 'q' to quit.\n")

    while True:
        game.board.display()
        move = input("Your move: ").strip().upper()
        if move == 'Q':
            print("Goodbye!")
            break
        if len(move) < 2:
            print("Invalid format.")
            continue

        col = ord(move[0]) - ord('A')
        try:
            row = game.board.size - int(move[1:])
        except ValueError:
            print("Invalid input.")
            continue

        if not game.play(row, col):
            continue
        game.ai_move()

if __name__ == "__main__":
    main()
