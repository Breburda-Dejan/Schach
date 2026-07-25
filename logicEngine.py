import math
from unittest import case

from ui import Piece, Player,INITIAL_PIECE_POSITION
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
    if move.lower() in ["o-o","o-o-o"]:
        return check_if_player_can_castle(player,pieces,move)
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


def validate_line(line: list[dict[str, int]], pieces, color, is_pawn: bool=False) -> list[dict[str, int]]:
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


def check_if_player_can_castle(player: Player, pieces: list[Piece], move: str) -> (int,Piece,dict[str,int]):
    '''
    This checks if the player can castle by checking if the path between king and rook is clear, there is no ongoing
    checks, there is no check on the squares where the king has to go through or land. It also checks if both rook and king
    haven't moved since the beginning of the game

    :param player: the player that requested the check.
    :param pieces: list of all pieces on the board
    :param move: move-notation from the input of the player. o-o-o for long-castle, o-o for short-castle
    :return:
    '''
    is_long_castle = "o-o-o" == move.lower()

    if is_my_king_in_check(player.king,pieces,player)[0]:
        return 55, None, None

    for piece in player.pieces:
        if piece.type.lower() == "king" and not piece.is_start:
            return 51,None,None
        if piece.type.lower() == "rook" and piece.start_position["file"] == (8,1)[is_long_castle] and not piece.is_start:
            return 52,None,None

    line_of_sight_from_king_to_rook: list[dict[str,int]] = []

    posFile = player.king.position["file"]
    posRank = player.king.position["rank"]
    direction = (1,-1)[is_long_castle]
    for i in range((3,4)[is_long_castle]):
        i += 1
        line_of_sight_from_king_to_rook.append({"file": posFile + i*direction, "rank": posRank})

    corrected_line_of_sight = validate_line(line=line_of_sight_from_king_to_rook,pieces=pieces,color=("b","w")[player.king.is_black])

    if len(corrected_line_of_sight) != (3,4)[is_long_castle]:
        return 53,None,None

    for pos in corrected_line_of_sight[:2]:
        if would_be_check_after_move(pieces,player,player.king,pos)[0]:
            return 54,None,None

    player.king.valid_positions.append(corrected_line_of_sight[1])
    return 0, player.king, corrected_line_of_sight[1]


def is_my_king_in_check(king: Piece, pieces: list[Piece], player: Player) -> tuple[bool,Piece]:
    '''
    This will check if the king, or any Piece-object given in the king-param, is attacked ( in check ). by shooting out lasers in evry direction
    a queen and knight can move and checking if there is a Piece, that could range the original spot of the Piece (king).

    :param king: Piece-object of the King to check
    :param pieces: list of all pieces on the board
    :return: a boolean that indicates if the King is in check, or not (True if yes, False if no) and the piece that's attacking
    '''


    king_pos_list = [king.position["file"], king.position["rank"]]
    line_of_sight_of_king = queen(king, pieces)  # reusing this, because it is already checking all squares in sight, except knight moves.
    line_of_sight_of_king.extend(knight(king, pieces))  # this should include all the possible knigt moves
    pos_to_piece_map: dict[any, Piece] = {f"{piece.position["file"]}-{piece.position["rank"]}": piece for piece in pieces}


    cleaned_line_of_sight_moves = remove_positions_of_own_pieces(clean_moves(line_of_sight_of_king),
                                                                 [piece.position for piece in pieces if piece.color == king.color])


    for pos in cleaned_line_of_sight_moves:
        piece_on_pos = pos_to_piece_map.get(f"{pos["file"]}-{pos["rank"]}")
        if piece_on_pos == None:
            continue
        pos_list = [pos["file"], pos["rank"]]
        raw_vector = [y - x for x, y in zip(king_pos_list, pos_list)]
        vector = [abs(value) for value in raw_vector]
        if vector in [[1, 2], [2, 1]]:  # is knight
            if piece_on_pos.type.lower() == "knight":
                return True,piece_on_pos
        elif vector[0] == vector[1]:
            if piece_on_pos.type.lower() in ["bishop", "queen"]:
                return True,piece_on_pos
        elif vector[0] == 0 or vector[1] == 0:
            if piece_on_pos.type.lower() in ["rook", "queen"]:
                return True,piece_on_pos
        elif raw_vector[1] == (1, -1)[piece_on_pos.is_black] and raw_vector[0] != 0:
            if piece_on_pos.type.lower() == "pawn":
                return True,piece_on_pos
    return False,None


def would_be_check_after_move(pieces: list[Piece], player: Player, piece_to_move: Piece, move: dict[str, int]) -> tuple[bool,Piece]:
    '''
    creates a temporary duplicate of the board, that moves any given piece to any given spot, and checks if this position would result in a check
    for the king.

    :param pieces: list of all pieces on the board.
    :param player: Player-object of the player requesting this check.
    :param piece_to_move: Piece-object of the Piece to move on this temporary board.
    :param move: position that the piece_to_move should move to.
    :return: a boolean that indicates if this move would result in check, or not (True if yes, False if not) and the piece that would be attacking
    '''
    temp_pieces = []
    king = None
    remove_after_copy = False # just a flag so I know when to delete the extra piece


    if piece_to_move.position == INITIAL_PIECE_POSITION:
        remove_after_copy = True
        pieces.append(piece_to_move)

    for piece in pieces:
        temp_pos = piece.position
        if piece.position == move:
            continue
        if piece.position == piece_to_move.position:
            temp_pos = move
        temp_pieces.append(Piece(piece.piece_id, temp_pos))

    if remove_after_copy:
        pieces.remove(piece_to_move)


    if piece_to_move.type.lower() == "king":
        king = [piece for piece in temp_pieces if piece.position == move][0]
    else:
        for temp_piece in temp_pieces:
            if temp_piece.type.lower() == "king" and temp_piece.color == player.color:
                king = temp_piece
                break


    if king == None:
        return False,None

    in_check,attacker = is_my_king_in_check(king, temp_pieces, player)

    for temp_piece in temp_pieces:
        del temp_piece
    del temp_pieces

    return in_check,attacker


def what_squares_to_defend(king: Piece, vector: list[int], attacker: Piece) -> list[dict[str,int]]:
    '''
    This is just to help finding out which squares are left that can be defended against a check

    :param king: Piece-object of the king from the player that requested the check
    :param vector: vector from king to attacker position
    :param attacker: Piece-object of the attacker that attacks the king
    :return: list of possible squares that can be jumped on to defend against the check
    '''
    defend_squares = []

    if attacker.type.lower() == "knight":
        defend_squares.append(attacker.position)
        return defend_squares

    direction_v = [0,0]

    if not 0 in vector:
        direction_v[0] = vector[0]/abs(vector[0])
        direction_v[1] = vector[1]/abs(vector[1])
    else:
        if vector[0] == 0:
            direction_v[1] = vector[1]/abs(vector[1])
        else:
            direction_v[0] = vector[0] / abs(vector[0])

    for i in range(max(abs(vector[0]),abs(vector[1]))):
        i += 1
        temp_pos = {"file": king.position["file"]+i*direction_v[0],"rank": king.position["rank"] + i*direction_v[1]}
        defend_squares.append(temp_pos)

    return defend_squares


def is_this_checkmate(pieces: list[Piece],player: Player) -> bool:
    '''
    This function checks if the player is checkmate, by checking if the king could move, or if any piece
    could block the ongoing check.

    :param pieces: list of all pieces on the board
    :param player: player that requested the check
    :return: A boolean that indicates rather its checkmate or not (True if yes, False if no)
    '''

    ### First of all, lets check if the king is evan in check

    if not is_my_king_in_check(player.king,pieces,player)[0]:
        return False

    ### Now lets see if the king can escape the check

    dumb_king_escapes = king(player.king,pieces)
    somehow_smarter_king_escapes = remove_positions_of_own_pieces(dumb_king_escapes,player.pieces)
    smartest_king_escapes = []
    for escape_pos in somehow_smarter_king_escapes:
        if not would_be_check_after_move(pieces,player,player.king,escape_pos)[0]:
            smartest_king_escapes.append(escape_pos)

    if len(smartest_king_escapes) > 0:
        return False

    ### Well that's bitter, king can't escape... can someone block though?
    ### What evan is attacking my king, and where is it?
    _,attacker = is_my_king_in_check(player.king,pieces,player)
    vector = player.king.calculate_vector(attacker.position)

    defend_squares = what_squares_to_defend(player.king,vector,attacker)

    temp_player = Player(("b","w")[player.king.is_black],[])

    dumb_check_blocks: list[list[dict[str,int]]] = []

    for pos in defend_squares:
        opposite_king = Piece(("B-K", "W-K")[player.king.is_black])
        can_block,piece_that_blocks = would_be_check_after_move(pieces,temp_player,opposite_king,pos)
        if can_block:
            temp_moves = [piece_that_blocks.position.copy(),pos.copy()]
            dumb_check_blocks.append(temp_moves.copy())
        del opposite_king

    ### well we have pieces that can block now, but what if there is check after the piece moves to block?

    for positions in dumb_check_blocks:
        piece_that_blocks = player.game.get_piece_on_position(positions[0])
        if piece_that_blocks.type.lower() == "king":
            continue
        if not would_be_check_after_move(pieces,player,piece_that_blocks,positions[1])[0]:
            return False

    ### finally, if king can't move and nothing can block, it's checkmate ( if I didn't miss anything ... )
    print("ITS CHECKMATE")
    return True


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
    valid_moves.extend(str_to_function_mapper.get(piece_to_move.type.lower(), lambda: [])(piece_to_move, pieces))

    blocked_moves.extend([piece.position for piece in player.pieces])
    valid_moves = clean_moves(valid_moves).copy()

    ### CHECK FOR CHECKS OR WAYS TO BLOCK CHECKS ...
    for move in valid_moves:
        if would_be_check_after_move(pieces, player, piece_to_move, move)[0]:
            blocked_moves.append(move)

    return remove_positions_of_own_pieces(valid_moves, blocked_moves)


if __name__ == '__main__':
    ...
