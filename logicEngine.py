import math
from unittest import case

from ui import Piece, Player, game
import re


def map_notation_to_move(notation: str) -> dict[str, int]:
    '''
    This function will map notations received from the cli-input to a position-dict-format.
    so "a2" will turn to {"file":1,"rank":2}

    :param notation: half of the input from the cli, so a2-a4 will process a2 and a4 separately
    :return: A dictionary in following format: {"file":[1-8],"rank":[1-8]}
    '''
    letter_to_number = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8}
    letter = notation[0].lower()
    number1 = letter_to_number[letter]
    number2 = int(notation[1])
    return {"file": number1, "rank": number2}


def validate_move(player:Player, pieces, move: str) -> int:
    '''
    This will check if the input given from the user was valid and then proceeds to collect allowed positions for the selected piece to travel to.

    :param player: Player object of the player that made the move
    :param pieces: All the pieces on the chessboard
    :param move: input of the user. format: [a-h][1-8]-[a-h][1-8]
    :return: error_code, Piece-object of the piece that the player wants to move, Move that the Piece should move to.
    '''
    valid_move_pattern = r"[a-h][1-8]-[a-h][1-8]"
    if not re.match(valid_move_pattern, move):
        return 32, None, None
    start_move = move.split("-")[0].lower()
    end_move = move.split("-")[1].lower()
    piece_to_move: Piece = [piece for piece in pieces if piece.position == map_notation_to_move(start_move)]
    if len(piece_to_move) != 1:
        return 93, None, None
    piece_to_move = piece_to_move[0]
    if player.color != piece_to_move.color:
        return 41, None, None
    end_move = map_notation_to_move(end_move)
    piece_to_move.valid_positions = calculate_valid_moves(pieces, piece_to_move, player).copy()
    return 0, piece_to_move, end_move


def validate_line(line: list[dict[str, int]], pieces, color, is_pawn=False) -> list[dict[str, int]]:
    '''
    This function will validate a list of positions ( that are in a straight line ).
    It will go through the list one by one, check if its empty, or if there is a piece and rather it's the same color or not.

    :param line: list of positions.
    :param pieces: all pieces on the board.
    :param color: color of the player that made the move, or rather that requested the move.
    :param is_pawn: a boolean, default False, that tells the function rather the Piece making the move is a pawn, or not. ( relevant because pawns cant take other pieces in a straight line )
    :return: a corrected list of positions that contain all "valid" positions for the piece to travel to.
    '''
    corrected_line: list[dict[str, int]] = []
    pos_to_piece_map: dict[any, Piece] = {f"{piece.position["file"]}-{piece.position["rank"]}": piece for piece in pieces}
    for pos in line:
        pos_key = f"{pos["file"]}-{pos["rank"]}"
        if pos_to_piece_map.get(pos_key) == None:
            corrected_line.append(pos)
            continue
        elif not pos_to_piece_map.get(pos_key).color == color and not is_pawn:
            corrected_line.append(pos)
            return corrected_line.copy()
        else:
            return corrected_line.copy()

    return corrected_line.copy()


def pawn(pawn: Piece, pieces: list[Piece]) -> list[dict[str, int]]:
    '''
    A function to check all valid moves from a pawn, without considering if the move would mean check, or be illegal.

    :param pawn: Piece-object of the pawn to move
    :param pieces: list of all pieces on the Board
    :return: a list of positions that the pawn could move to
    '''
    dumb_pawn_moves = []
    direction = (1, -1)[pawn.is_black]
    max = (1, 2)[pawn.is_start]
    posFile = pawn.position["file"]
    posRank = pawn.position["rank"]
    pos_to_piece_map: dict[any, Piece] = {f"{piece.position["file"]}-{piece.position["rank"]}": piece for piece in pieces}

    line = []
    for i in range(max):
        dummy_pos = {"file": posFile, "rank": posRank + (i + 1) * direction}
        line.append(dummy_pos)
    dumb_pawn_moves.extend(validate_line(line, pieces, pawn.color, is_pawn=True))

    positions_list = [
        [posFile - direction, posRank + direction],
        [posFile + direction, posRank + direction]
    ]
    en_passant_check_list = [
        [posFile - direction, posRank],
        [posFile + direction, posRank]
    ]

    for i, pos in enumerate(positions_list):
        temp_pos = {"file": pos[0], "rank": pos[1]}
        key = f"{pos[0]}-{pos[1]}"
        key_en_passant = f"{en_passant_check_list[i][0]}-{en_passant_check_list[i][1]}"

        if (not pos_to_piece_map.get(key) == None and
                pos_to_piece_map.get(key).color != pawn.color):
            dumb_pawn_moves.append(temp_pos)

        if (not pos_to_piece_map.get(key_en_passant) == None and
                pos_to_piece_map.get(key_en_passant).en_passant_able_on_count == pawn.game.count and
                pos_to_piece_map.get(key_en_passant).color != pawn.color):
            dumb_pawn_moves.append(temp_pos)

    return dumb_pawn_moves


def knight(knight: Piece, pieces: list[Piece]) -> list[dict[str, int]]:
    '''
    A function to check all possible moves from a knight without considering if the knight would jump out of the board or
    do any other illegal moves.

    :param knight: Piece-object of the knight to move
    :param pieces: list of all pieces on the board
    :return: a list of all possible positions the knight could move tos
    '''
    dumb_knight_moves = []
    posFile = knight.position["file"]
    posRank = knight.position["rank"]

    up_left_pos = {"file": posFile - 1, "rank": posRank + 2}
    up_right_pos = {"file": posFile + 1, "rank": posRank + 2}
    right_up_pos = {"file": posFile + 2, "rank": posRank - 1}
    right_down_pos = {"file": posFile + 2, "rank": posRank + 1}
    down_right_pos = {"file": posFile + 1, "rank": posRank - 2}
    down_left_pos = {"file": posFile - 1, "rank": posRank - 2}
    left_down_pos = {"file": posFile - 2, "rank": posRank - 1}
    left_up_pos = {"file": posFile - 2, "rank": posRank + 1}

    # no need to excluded spots where own pieces are (will be deleted in the blocked moves section)... I hope...

    dumb_knight_moves.extend(
        [up_left_pos, up_right_pos, right_up_pos, right_down_pos, down_left_pos, down_right_pos, left_up_pos,
         left_down_pos])
    return dumb_knight_moves


def bishop(bishop: Piece, pieces: list[Piece]) -> list[dict[str, int]]:
    '''
    This function will check every position it could move to without considering any illegal moves.

    :param bishop: Piece-object of the Bishop to move
    :param pieces: list of all the pieces on the board
    :return: a list of possible positions the bishop could move to
    '''
    dumb_bishop_moves = []
    posFile = bishop.position["file"]
    posRank = bishop.position["rank"]

    line_up_right = []
    line_right_down = []
    line_down_left = []
    line_left_up = []
    for i in range(8):
        i += 1
        line_up_right.append({"file": posFile + i, "rank": posRank + i})
        line_right_down.append({"file": posFile + i, "rank": posRank - i})
        line_down_left.append({"file": posFile - i, "rank": posRank - i})
        line_left_up.append({"file": posFile - i, "rank": posRank + i})

    dumb_bishop_moves.extend(validate_line(line_up_right, pieces, bishop.color))
    dumb_bishop_moves.extend(validate_line(line_right_down, pieces, bishop.color))
    dumb_bishop_moves.extend(validate_line(line_down_left, pieces, bishop.color))
    dumb_bishop_moves.extend(validate_line(line_left_up, pieces, bishop.color))

    return dumb_bishop_moves


def rook(rook: Piece, pieces: list[Piece]) -> list[dict[str, int]]:
    '''
    This will list positions a rook could move to without checking any illegal moves.
    :param rook: Piece-object of the rook to move.
    :param pieces: list of all pieces on the board
    :return: a list of all possible moves a rook could make
    '''
    dumb_rook_moves = []
    posFile = rook.position["file"]
    posRank = rook.position["rank"]

    line_up = []
    line_right = []
    line_down = []
    line_left = []
    for i in range(8):
        i += 1
        line_up.append({"file": posFile, "rank": posRank + i})
        line_right.append({"file": posFile + i, "rank": posRank})
        line_down.append({"file": posFile, "rank": posRank - i})
        line_left.append({"file": posFile - i, "rank": posRank})

    dumb_rook_moves.extend(validate_line(line_up, pieces, rook.color))
    dumb_rook_moves.extend(validate_line(line_right, pieces, rook.color))
    dumb_rook_moves.extend(validate_line(line_down, pieces, rook.color))
    dumb_rook_moves.extend(validate_line(line_left, pieces, rook.color))

    return dumb_rook_moves


def queen(queen: Piece, pieces: list[Piece]) -> list[dict[str, int]]:
    '''
    This will list all available positions a queen could move to by recycling the functions for the rook and bishop.

    :param queen: Piece-object of the queen to move
    :param pieces: list of all pieces on the board
    :return: a list of all available moves a queen could make without considering illegal moves
    '''
    dumb_queen_moves = []
    dumb_queen_moves.extend(bishop(queen,pieces))
    dumb_queen_moves.extend(rook(queen,pieces))
    return dumb_queen_moves


def king(king: Piece, pieces: list[Piece]) -> list[dict[str, int]]:
    '''
    A function that returns a list of possible positions a king could move to.

    :param king: Piece-object of the King to move.
    :param pieces: list of all pieces on the board.
    :return: a list of all available positions of a king.
    '''
    dumb_king_moves = []
    posFile = king.position["file"]
    posRank = king.position["rank"]

    directions_list = [
        [0, 1],  # up
        [1, 1],  # up-right
        [1, 0],  # right
        [1, -1],  # right-down
        [0, -1],  # down
        [-1, -1, ],  # down-left
        [-1, 0],  # left
        [-1, 1]  # left-up
    ]

    for direction in directions_list:
        temp_pos = {"file": posFile + direction[0], "rank": posRank + direction[1]}
        dumb_king_moves.append(temp_pos)

    return dumb_king_moves


def clean_moves(moves: list[dict[str, int]]) -> list[dict[str, int]]:
    '''
    This will clean a list of moves by throwing out positions that are not inside the board.

    :param moves: list of uncleaned positions
    :return: list of cleaned positions
    '''
    cleaned_moves = []
    allowed_values = [1, 2, 3, 4, 5, 6, 7, 8]
    for move in moves:
        if list(move.values())[0] not in allowed_values or list(move.values())[1] not in allowed_values:
            continue
        cleaned_moves.append(move)

    return cleaned_moves


def is_my_king_in_check(king: Piece, pieces: list[Piece]) -> bool:
    '''
    This will check if the king, or any Piece-object given in the king-param, is attacked ( in check ). by shooting out lasers in evry direction
    a queen and knight can move and checking if there is a Piece, that could range the original spot of the Piece (king).

    :param king: Piece-object of the King to check
    :param pieces: list of all pieces on the board
    :return: a boolean that indicates if the King is in check, or not (True if yes, False if no)
    '''
    king_pos_list = [king.position["file"], king.position["rank"]]
    line_of_sight_of_king = queen(king, pieces)  # reusing this, because it is already checking all squares in sight, except knight moves.
    line_of_sight_of_king.extend(knight(king, pieces))  # this should include all the possible knigt moves

    cleaned_line_of_sight_moves = remove_positions_of_own_pieces(clean_moves(line_of_sight_of_king),
                                                                 [piece.position for piece in pieces if piece.color == king.color])

    for pos in cleaned_line_of_sight_moves:
        piece_on_pos = king.game.get_piece_on_position(pos)
        if piece_on_pos == None:
            continue
        pos_list = [pos["file"], pos["rank"]]
        raw_vektor = [y - x for x, y in zip(king_pos_list, pos_list)]
        vektor = [abs(value) for value in raw_vektor]
        if vektor in [[1, 2], [2, 1]]:  # is knight
            if piece_on_pos.type.lower() == "knight":
                return True
        elif vektor[0] == vektor[1]:
            if piece_on_pos.type.lower() in ["bishop", "queen"]:
                return True
        elif vektor[0] == 0 or vektor[1] == 0:
            if piece_on_pos.type.lower() in ["rook", "queen"]:
                return True
        elif raw_vektor[1] == (1, -1)[piece_on_pos.is_black] and raw_vektor[0] != 0:
            if piece_on_pos.type.lower() == "pawn":
                return True
    return False


def would_be_check_after_move(pieces: list[Piece], player: Player, piece_to_move: Piece, move: dict[str, int]) -> bool:
    '''
    creates a temporary duplicate of the board, that moves any given piece to any given spot, and checks if this position would result in a check
    for the king.

    :param pieces: list of all pieces on the board.
    :param player: Player-object of the player requesting this check.
    :param piece_to_move: Piece-object of the Piece to move on this temporary board.
    :param move: position that the piece_to_move should move to.
    :return: a boolean that indicates if this move would result in check, or not (True if yes, False if not)
    '''
    temp_pieces = []
    king = None
    for piece in pieces:
        temp_pos = piece.position
        if piece.position == move:
            continue
        if piece.position == piece_to_move.position:
            temp_pos = move
        if piece.type.lower() == "king" and piece.color == piece_to_move.color:
            king = piece
        temp_pieces.append(Piece(piece.piece_id, temp_pos))

    if king == None:
        return False

    return is_my_king_in_check(king, temp_pieces)


def remove_positions_of_own_pieces(moves: list[dict[str, int]], positions_of_own_pieces: list[dict[str, int]]) -> list[dict[str, int]]:
    '''
    A function that helps to remove any Position in a list that contains a Piece of the own color.

    :param moves: list of positions to be cleaned
    :param positions_of_own_pieces: list of positions of pieces from the same Player
    :return: a subtracted list that only includes Positions from the moves-list that are not also in the positions_of_own_pieces-list.
    '''
    return [move for move in moves if move not in positions_of_own_pieces]


def calculate_valid_moves(pieces: list[Piece], piece_to_move: Piece, player: Player) -> list[dict[str, int]]:
    '''
    This function will map the piece to move to a dedicated function that will list available moves for that specific type of Piece.

    :param pieces: list of all pieces on the board
    :param piece_to_move: Piece-object of the piece to move.
    :param player: Player-object of the player that requested the check
    :return: a list of Valid positions the selected Piece can move to.
    '''
    valid_moves: list[dict[str, int]] = []
    blocked_moves: list[dict[str, int]] = []
    str_to_function_mapper = {
        "pawn": pawn,
        "knight": knight,
        "bishop": bishop,
        "rook": rook,
        "queen": queen,
        "king": king
    }
    valid_moves.extend(str_to_function_mapper.get(piece_to_move.type.lower(), lambda: [])(piece_to_move, pieces))  # -> calls the function with the pieces type-name

    blocked_moves.extend([piece.position for piece in player.pieces])
    valid_moves = clean_moves(valid_moves).copy()

    #### CHECK FOR CHECKS OR WAYS TO BLOCK CHECKS ... ####
    is_check = is_my_king_in_check(player.king, pieces)
    for move in valid_moves:
        if would_be_check_after_move(pieces, player, piece_to_move, move):
            blocked_moves.append(move)
    ######################################################

    return remove_positions_of_own_pieces(valid_moves, blocked_moves)


if __name__ == '__main__':
    ...
