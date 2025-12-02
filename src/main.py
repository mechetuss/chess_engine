import sys
from chess_engine import ChessEngine


def main():
    engine = ChessEngine("models/weights.pth", "models/move_to_int")

    while True:
        line = sys.stdin.readline().strip()
        if not line:
            continue

        parts = line.split()
        command = parts[0]

        if command == "uci":
            print("id name ChessNN")
            print("id author BT")
            print("uciok")
            sys.stdout.flush()

        elif command == "isready":
            print("readyok")
            sys.stdout.flush()

        elif command == "position":
            fen = None
            moves = []

            if "fen" in parts:
                fen_index = parts.index("fen") + 1
                fen_parts = []
                for i in range(fen_index, len(parts)):
                    if parts[i] == "moves":
                        break
                    fen_parts.append(parts[i])
                fen = " ".join(fen_parts)

            if "moves" in parts:
                moves_index = parts.index("moves") + 1
                moves = parts[moves_index:]

            engine.set_position(fen, moves)

        elif command == "go":
            best_move = engine.get_best_move()
            if best_move:
                print(f"bestmove {best_move}")
            else:
                print("bestmove 0000")
            sys.stdout.flush()

        elif command == "quit":
            break

        elif command == "stop":
            best_move = engine.get_best_move()
            if best_move:
                print(f"bestmove {best_move}")
            else:
                print("bestmove 0000")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
