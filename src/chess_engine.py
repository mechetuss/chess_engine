import numpy as np
import torch
import pickle
from chess import Board
from model import ChessModel


class ChessEngine:
    def __init__(self, model_path, dict_path):
        with open(dict_path, "rb") as f:
            self.move_encoding_dict = pickle.load(f)
        self.reverse_move_dict = {idx: move_str for move_str, idx in self.move_encoding_dict.items()}

        self.device = torch.device("cpu")

        self.model = ChessModel(num_classes=len(self.move_encoding_dict))
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

        self.board = Board()

    def encode_board_state(self, board):
        encoding = np.zeros((13, 8, 8))
        pieces = board.piece_map()

        for position, chess_piece in pieces.items():
            y, x = divmod(position, 8)
            piece_id = chess_piece.piece_type - 1
            color_offset = 0 if chess_piece.color else 6
            encoding[piece_id + color_offset, y, x] = 1.0

        for possible_move in board.legal_moves:
            target = possible_move.to_square
            y, x = divmod(target, 8)
            encoding[12, y, x] = 1.0

        return encoding

    def create_model_input(self, board):
        encoded_board = self.encode_board_state(board)
        input_tensor = torch.tensor(encoded_board, dtype=torch.float32)
        return input_tensor.unsqueeze(0)

    def set_position(self, fen=None, moves=None):
        if fen:
            self.board = Board(fen)
        else:
            self.board = Board()

        if moves:
            for move_uci in moves:
                self.board.push_uci(move_uci)

    def get_best_move(self):
        input_data = self.create_model_input(self.board).to(self.device)

        with torch.no_grad():
            predictions = self.model(input_data)

        predictions = predictions.squeeze(0)
        move_probabilities = torch.softmax(predictions, dim=0).cpu().numpy()
        allowed_moves = {m.uci() for m in self.board.legal_moves}
        sorted_probs = np.argsort(move_probabilities)[::-1]

        for move_idx in sorted_probs:
            move_candidate = self.reverse_move_dict.get(move_idx)
            if move_candidate in allowed_moves:
                return move_candidate

        legal_moves_list = list(self.board.legal_moves)
        if legal_moves_list:
            return legal_moves_list[0].uci()
        return None
