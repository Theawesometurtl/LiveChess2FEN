"""
Predicts board configurations from images.
"""
import glob
import os
import shutil

import cv2
import numpy as np
from keras.preprocessing import image

from lc2fen.detectboard.detect_board import detect
from lc2fen.fen import list_to_board, board_to_fen
from lc2fen.infer_pieces import infer_chess_pieces
from lc2fen.split_board import split_square_board_image


def load_image(img_path, img_size, preprocess_func):
    """
    Loads an image from its path. Intended to use with piece images.

    :param img_path: Image path.
    :param img_size: Size of the input image. For example: 224
    :param preprocess_func: Preprocessing fuction to apply to the input
        image.
    :return: The loaded image.
    """
    img = image.load_img(img_path, target_size=(img_size, img_size))
    img_tensor = image.img_to_array(img)
    img_tensor = np.expand_dims(img_tensor, axis=0)
    return preprocess_func(img_tensor)


def detect_input_board(board_path):
    """
    Detects the input board and stores the result as 'tmp/board_name in
    the folder containing the board. If the folder tmp exists, deletes
    its contents. If not, creates the tmp folder.

    :param board_path: Path to the board to detect. Must have rw permission.
        For example: '../predictions/board.jpg'.
    """
    input_image = cv2.imread(board_path)
    head, tail = os.path.split(board_path)
    tmp_dir = os.path.join(head, "tmp/")
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.mkdir(tmp_dir)
    detect(input_image, os.path.join(head, "tmp", tail))


def obtain_individual_pieces(board_path):
    """
    Obtain the individual pieces of a board.

    :param board_path: Path to the board to detect. Must have rw permission.
        The detected board should be in a tmp folder as done by
        detect_input_board.
        For example: '../predictions/board.jpg'.
    :return: List with the path to each piece image.
    """
    head, tail = os.path.split(board_path)
    tmp_dir = os.path.join(head, "tmp/")
    pieces_dir = os.path.join(tmp_dir, "pieces/")
    os.mkdir(pieces_dir)
    split_square_board_image(os.path.join(tmp_dir, tail), "", pieces_dir)
    return sorted(glob.glob(pieces_dir + "/*.jpg"))


def predict_board(board_path, a1_pos, obtain_pieces_probs):
    """
    Predict the fen notation of a chessboard.

    The obtain_predictions argument allows us to predict using different
    methods (such as Keras, ONNX or TensorRT models) that may need
    additional context.

    :param board_path: Path to the board to detect. Must have rw permission.
        For example: '../predictions/board.jpg'.
    :param a1_pos: Position of the a1 square. Must be one of the
        following: "BL", "BR", "TL", "TR".
    :param obtain_pieces_probs: Function which receives a list with the
        path to each piece image in FEN notation order and returns the
        corresponding probabilities of each piece belonging to each
        class as another list.
    :return: Predicted fen string representing the chessboard.
    """
    detect_input_board(board_path)
    pieces = obtain_individual_pieces(board_path)
    pieces_probs = obtain_pieces_probs(pieces)
    predictions = infer_chess_pieces(pieces_probs, a1_pos)

    board = list_to_board(predictions)
    fen = board_to_fen(board)

    return fen