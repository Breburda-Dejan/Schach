import glob
import pickle
import re
from collections import Counter
from ui import Piece, Player, ChessBoard, INITIAL_PIECE_POSITION, PIECE_IDS


def load_position_from_file(game: ChessBoard,positions_from_file) -> list[Piece]:
    '''
    helper function to help import positions from a save_dict
    :param game: ChessBoard that requested the load
    :param positions_from_file: save_dict
    :return: list of Pieces
    '''
    pieces: list[Piece] = []
    for pos in list(positions_from_file.keys()):
        if not pos.__contains__("-") and pos.isnumeric():
            game.count = int(pos)
            continue
        file = int(pos.split("-")[0])
        rank = int(pos.split("-")[1])
        piece_id = positions_from_file[pos]["piece_id"]
        start_position = positions_from_file[pos]["start_position"]
        is_start = positions_from_file[pos]["is_start"]
        en_passant_able_on_count = positions_from_file[pos]["en_passant_able_on_count"]
        temp_piece = Piece(piece_id, {"file": file, "rank": rank})
        temp_piece.is_start = is_start
        temp_piece.start_position = start_position
        temp_piece.en_passant_able_on_count = en_passant_able_on_count
        pieces.append(temp_piece)

    return pieces


def exec_cmd(cmd: str,game: ChessBoard):
    '''
    This function is used to add debug functionality by using commands that can do magic

    :param cmd: string typed into the console
    :param game: ChessBoard - object
    :return: returns nothing
    '''
    pieces: list[Piece] = game.pieces
    if cmd.startswith("/show"):
        if "all" in cmd:
            print("showing moves for every piece:")
            for piece in pieces:
                piece.valid_positions =  calculate_valid_moves(pieces,piece,piece.player).copy()
                print(str(piece))
        elif cmd[6:].startswith("b"):
            print("showing valid-moves from black:")
            for piece in game.player2.pieces:
                piece.valid_positions =  calculate_valid_moves(pieces,piece,piece.player).copy()
                print(str(piece))
        elif cmd[6:].startswith("w"):
            print("showing valid-moves from white:")
            for piece in game.player1.pieces:
                piece.valid_positions =  calculate_valid_moves(pieces,piece,piece.player).copy()
                print(str(piece))

    elif cmd.startswith("/move"):
        if len(cmd[6:].strip()) == 5:
            move = cmd[6:].strip()
            valid_move_pattern = r"[a-h][1-8]-[a-h][1-8]"
            if not re.match(valid_move_pattern, move):
                print("not a valid move")
                return
            start_move = move.split("-")[0].lower()
            end_move = move.split("-")[1].lower()
            piece_to_move: Piece = game.get_piece_on_position(map_notation_to_move(start_move))
            piece_on_end: Piece = game.get_piece_on_position(map_notation_to_move(end_move))

            if piece_on_end != None:
                piece_on_end.kill()

            if piece_to_move == None:
                print("No piece to move, do you want to /spawn?")
                return

            piece_to_move.position = map_notation_to_move(end_move)

            print(f"{piece_to_move.name.capitalize()} successfully moved from {start_move} to {end_move}")

    elif cmd.startswith("/spawn"):
        if len(cmd[7:].strip()) == 6:
            piece_id = cmd[7:10].upper()
            if len(cmd[10:].strip()) == 2:
                position = cmd[10:].strip()
                valid_move_pattern = r"[a-h][1-8]"
                if not re.match(valid_move_pattern, position):
                    print("not a valid position")
                    return
            else:
                print("not a valid position")
                return
            position = map_notation_to_move(position)

            piece_on_position = game.get_piece_on_position(position)
            if piece_on_position != None:
                piece_on_position.kill()

            new_piece = Piece(piece_id,position)
            new_piece.game = game
            new_piece.player = (game.player1,game.player2)[new_piece.is_black]
            new_piece.player.pieces.append(new_piece)
            if new_piece.type.lower() == "king":
                new_piece.player.king = new_piece
            game.pieces.append(new_piece)

    elif cmd.startswith("/kill"):
        if len(cmd[6:].strip()) == 2:
            position = cmd[6:].strip()
            valid_move_pattern = r"[a-h][1-8]"
            if not re.match(valid_move_pattern, position):
                print("not a valid position")
                return
            position = map_notation_to_move(position)
            piece_on_position = game.get_piece_on_position(position)
            if piece_on_position != None:
                piece_on_position.kill()

    elif cmd.startswith("/clear"):
        game.pieces = []
        game.player2.pieces = []
        game.player1.pieces = []
        game.player1.king = None
        game.player2.king = None

    elif cmd.startswith("/resign"):
        game.run = False
        print(f"{game.current_Player.name} resigned!")

    elif cmd.startswith("/load"):
        if cmd[6:14].lower() == "position":
            game.count = 0
            game.pieces = []
            game.player2.pieces = []
            game.player1.pieces = []
            name = cmd[15:].strip().lower()
            if not f"data/saved_positions/{name}.pkl" in glob.glob("data/saved_positions/*.pkl"):
                print("position doesn't exist...")
                [print(position[21:-4],end=", ") for position in glob.glob("data/saved_positions/*.pkl")]
                print()
                return

            loaded_position: dict[str,[dict[str,Any]]] = {}
            with open(f"data/saved_positions/{name}.pkl",'rb') as load:
                loaded_position = pickle.load(load)

            pieces: list[Piece] = load_position_from_file(game,loaded_position)
            for piece in pieces:
                piece.set_game(game)
                player: Player = (game.player1, game.player2)[piece.is_black]
                piece.player = player
                player.pieces.append(piece)
                game.pieces.append(piece)
                if piece.type.lower() == "king":
                    player.king = piece

            print("Position set successfully")

        elif cmd[6:10].lower() == "game":
            game.count = -1
            game.pieces = []
            game.player2.pieces = []
            game.player1.pieces = []
            game.game_snapshots_per_count:dict[int,list[Piece]] = {}
            name = cmd[11:].strip().lower()
            if not f"data/saved_games/{name}.pkl" in glob.glob("data/saved_games/*.pkl"):
                print("position doesn't exist...")
                [print(position[17:-4], end=", ") for position in glob.glob("data/saved_games/*.pkl")]
                print()
                return

            loaded_game: dict[str, [dict[str, Any]]] = {}
            with open(f"data/saved_games/{name}.pkl", 'rb') as load:
                loaded_game = pickle.load(load)

            for count, pieces_to_load in loaded_game.items():
                game.game_snapshots_per_count[count] = load_position_from_file(game, pieces_to_load)

            count_to_reset_to = int(list(game.game_snapshots_per_count.keys())[-1])
            if count_to_reset_to in list(game.game_snapshots_per_count.keys()):
                pieces = game.game_snapshots_per_count[count_to_reset_to].copy()
                for piece in pieces:
                    temp_piece = Piece(piece.piece_id, piece.position)
                    if temp_piece.is_black:
                        temp_piece.player = game.player2
                    else:
                        temp_piece.player = game.player1
                    temp_piece.set_game(game)
                    temp_piece.is_start = piece.is_start
                    temp_piece.start_position = piece.start_position
                    temp_piece.en_passant_able_on_count = piece.en_passant_able_on_count
                    if temp_piece.type.lower() == "king":
                        temp_piece.player.king == temp_piece
                    temp_piece.player.pieces.append(temp_piece)
                    game.pieces.append(temp_piece)

                game.current_Player = (game.player1, game.player2)[count_to_reset_to % 2 == 0]
                game.count = count_to_reset_to + 1
                print(f"Successfully reset to position on count {count_to_reset_to}")
                print("Game loaded successfully")
                return

            print("I think something went wrong while loading. mb")

        elif cmd[6:11].lower() == "count":
            game.pieces = []
            game.player2.pieces = []
            game.player1.pieces = []
            game.player1.king = None
            game.player2.king = None

            count_to_reset_to:int = cmd[12:].strip()

            if count_to_reset_to.isnumeric():
                count_to_reset_to = int(count_to_reset_to)
                if count_to_reset_to in list(game.game_snapshots_per_count.keys()):
                    pieces = game.game_snapshots_per_count[count_to_reset_to].copy()
                    for piece in pieces:
                        temp_piece = Piece(piece.piece_id,piece.position)
                        if temp_piece.is_black:
                            temp_piece.player = game.player2
                        else:
                            temp_piece.player = game.player1
                        temp_piece.set_game(game)
                        temp_piece.is_start = piece.is_start
                        temp_piece.start_position = piece.start_position
                        temp_piece.en_passant_able_on_count = piece.en_passant_able_on_count
                        if temp_piece.type.lower() == "king":
                            temp_piece.player.king == temp_piece
                        temp_piece.player.pieces.append(temp_piece)
                        game.pieces.append(temp_piece)

                    game.current_Player = (game.player2,game.player1)[count_to_reset_to % 2 == 0]
                    game.count = count_to_reset_to + 1
                    print(f"Successfully reset to position on count {count_to_reset_to}")
                    return

            print("Something went wrong while resetting")

    elif cmd.startswith("/save"):
        if cmd[6:14].lower() == "position":
            name = cmd[15:].strip().lower()
            name = name.replace(" ","_")
            save_dict:dict[str,dict[str,Any]] = {str(game.count):{}}
            for piece in game.pieces:
                entry = {}
                entry["start_position"] = piece.start_position
                entry["is_start"] = piece.is_start
                entry["piece_id"] = piece.piece_id
                entry["en_passant_able_on_count"] = piece.en_passant_able_on_count
                save_dict[f"{piece.position["file"]}-{piece.position["rank"]}"] = entry

            with open(f"data/saved_positions/{name}.pkl",'wb') as save:
                pickle.dump(save_dict, save)
                print(f"Position saved as {name}")

        elif cmd[6:10].lower() == "game":
            name = cmd[11:].strip().lower()
            name = name.replace(" ","_")
            save_dict:dict[int,dict[str,dict[str,Any]]] = {}
            for count,pieces in game.game_snapshots_per_count.items():
                positions_save_dict = {}
                for piece in pieces:
                    entry = {}
                    entry["start_position"] = piece.start_position
                    entry["is_start"] = piece.is_start
                    entry["piece_id"] = piece.piece_id
                    entry["en_passant_able_on_count"] = piece.en_passant_able_on_count
                    positions_save_dict[f"{piece.position["file"]}-{piece.position["rank"]}"] = entry
                save_dict[count] = positions_save_dict

            with open(f"data/saved_games/{name}.pkl",'wb') as save:
                pickle.dump(save_dict, save)
                print(f"Game saved as {name}")

    elif cmd.startswith("/count"):
        if cmd[7:].split(" ")[0] == "set":
            try:
                game.count = int(cmd[7:].split(" ")[1].strip())
                print(f"Game-count set to {game.count}")
            except:
                print("Game-count not set, there was an error!")

        elif cmd[7:] == "show":
            print(f"Current game-count: {game.count}")
        elif cmd[7:] == "reset":
            game.count = 0
            print(f"Game-count set to {game.count}")

    elif cmd.startswith("/info"):
        if len(cmd[6:].strip()) == 2:
            position = cmd[6:].strip()
            valid_move_pattern = r"[a-h][1-8]"
            if not re.match(valid_move_pattern, position):
                print("not a valid position")
                return
            piece_on_position: Piece = game.get_piece_on_position(map_notation_to_move(position))
            piece_on_position.valid_positions = calculate_valid_moves(game.pieces,piece_on_position,piece_on_position.player)
            print(str(piece_on_position))

    elif cmd.startswith("/switch"):
        if cmd[8:].strip() == "player":
            player1 = game.player1
            player2 = game.player2
            game.current_Player = (player1,player2)[game.current_Player == player1]

    elif cmd.startswith("/reset"):
        game.__init__()
        print("Game Reset!")



def string_to_bool(string:str) -> bool:
    if string.lower().startswith("f") or (string.isnumeric() and int(string) == 0):
        return False
    return True


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
    if piece_to_move.type.lower() == "king" and abs(piece_to_move.calculate_vector(end_move)[0]) == 2:
        return check_if_player_can_castle(player,pieces,("o-o","o-o-o")[piece_to_move.calculate_vector(end_move)[0] == -2])
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


        en_passant_chek_pawn = pos_to_piece_map.get(key_en_passant)
        if not en_passant_chek_pawn == None:
            if (en_passant_chek_pawn.en_passant_able_on_count + 1 == pawn.game.count and
                en_passant_chek_pawn.color != pawn.color):
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
    

    _,_,short_castle = check_if_player_can_castle(king.player,pieces,"o-o")
    _,_,long_castle = check_if_player_can_castle(king.player,pieces,"o-o-o")

    dumb_king_moves.append(short_castle)
    dumb_king_moves.append(long_castle)

    return dumb_king_moves


def clean_moves(moves: list[dict[str, int]]) -> list[dict[str, int]]:
    '''
    This will clean a list of moves by throwing out positions that are not inside the board.

    :param moves: list of uncleaned positions
    :return: list of cleaned positions
    '''
    if len(moves) == 0:
        return []
    cleaned_moves = []
    allowed_values = [1, 2, 3, 4, 5, 6, 7, 8]
    for move in moves:
        if move is None:
            continue
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
        if all(v<=1 for v in vector) and piece_on_pos.type.lower() == "king":
            return True,piece_on_pos
        elif vector in [[1, 2], [2, 1]] and piece_on_pos.type.lower() == "knight":
            return True,piece_on_pos
        elif vector[0] == vector[1] and piece_on_pos.type.lower() in ["bishop", "queen"]:
            return True,piece_on_pos
        elif (vector[0] == 0 or vector[1] == 0) and piece_on_pos.type.lower() in ["rook", "queen"]:
            return True,piece_on_pos
        elif raw_vector[1] == (-1, 1)[piece_on_pos.is_black] and raw_vector[0] in [1,-1] and piece_on_pos.type.lower() == "pawn":
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
    posFile = piece_to_move.position["file"]
    posRank = piece_to_move.position["rank"]
    en_passanted_pawn = None

    if piece_to_move.position == INITIAL_PIECE_POSITION:
        remove_after_copy = True
        pieces.append(piece_to_move)

    vector = piece_to_move.calculate_vector(move)
    if piece_to_move.type.lower() == "pawn" and abs(vector[0]) == 1 and abs(vector[1]) == 1 and player.game.get_piece_on_position(move) == None:
        if player.game.get_piece_on_position({"file":posFile + vector[0],"rank":posRank}).type.lower() == "pawn":
            en_passanted_pawn = player.game.get_piece_on_position({"file":posFile + vector[0],"rank":posRank})

    for piece in pieces:
        temp_pos = piece.position
        if piece.position == move or (en_passanted_pawn != None and piece.position == en_passanted_pawn.position):
            continue
        elif piece.position == piece_to_move.position:
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


def check_for_win_or_draw(game: ChessBoard) -> tuple[str,Player]:
    '''
    Checks for win, by checkmate, or a draw.

    :param game: ChessBoard - object of the game that requested the check
    :return: string ("w","d","n") for win, draw, nothing; Player that won, else None
    '''

    players = [game.player1,game.player2]

    for player in players:
        total_valid_moves = []
        for piece in player.pieces:
            total_valid_moves.extend(calculate_valid_moves(game.pieces,piece,player))
        if len(total_valid_moves) == 0:
            if is_my_king_in_check(player.king,game.pieces,player)[0]:
                return "w",players[game.player1 == player]
            else:
                return "d",None

    #check for draw by repetition
    board_positions_to_count: list[str] =  []
    for pieces in list(game.game_snapshots_per_count.values()):
        simple_pos_id_string: str = ""
        for piece in pieces:
            simple_pos_id_string += f"{piece.position["file"]}-{piece.position["rank"]} = {piece.piece_id},"
        board_positions_to_count.append(simple_pos_id_string)
    count_of_positions_on_board = dict(Counter(board_positions_to_count))
    if 3 in list(count_of_positions_on_board.values()):
        return "d",None

    #check for draw by insufficient material
    list_of_all_ids_left = [piece.piece_id for piece in game.pieces]
    if len(list_of_all_ids_left) == 2: # only the 2 kings left?
        kings = ["W-K","B-K"]
        if all(id in kings for id in list_of_all_ids_left):
            return "d",None

    elif len(list_of_all_ids_left) == 3: # 2 kings one other
        insufficient_on_its_own = ["W-N","W-B","B-N","B-B"]
        if any(id in insufficient_on_its_own for id in list_of_all_ids_left):
            return "d",None

    elif len(list_of_all_ids_left) == 4: # well, that's a little bit more complicated
        list_of_p1_ids_left = [(piece.piece_id, piece) for piece in game.player1.pieces]
        list_of_p2_ids_left = [(piece.piece_id, piece) for piece in game.player2.pieces]
        insufficient_on_its_own = ["knight","bishop"]
        if len(list_of_p1_ids_left) == 2 == len(list_of_p2_ids_left):
            if (any(piece.type.lower() in insufficient_on_its_own for id,piece in list_of_p1_ids_left) and
                any(piece.type.lower() in insufficient_on_its_own for id,piece in list_of_p2_ids_left)):
                return "d",None
        elif len(list_of_p1_ids_left) == 3 or len(list_of_p2_ids_left) == 3:
            type_count_of_p1 = dict(Counter([piece.type for _, piece in list_of_p1_ids_left]))
            type_count_of_p2 = dict(Counter([piece.type for _, piece in list_of_p2_ids_left]))
            if (type_count_of_p1.get("knight", 0) == 2 or
                type_count_of_p2.get("knight", 0) == 2):
                return "d",None
            elif (type_count_of_p1.get("bishop", 0) == 2 or
                type_count_of_p2.get("bishop", 0) == 2):
                white_bishops = 0
                for piece in pieces:
                    if piece.type.lower() == "bishop" and game.get_color_of_square(piece.position) == "w":
                        white_bishops += 1
                if white_bishops != 1:
                    return "d",None
    return "n",None


def check_for_promotion(player:Player, move:str, id_to_promote) -> tuple[int,Piece,dict[str,int],str]:
    '''
    This will check if a pawn can promote.

    :param player: player that requested the check
    :param move: Move notations [a-h][1-8]-[a-h][1-8]
    :param id_to_promote: id of the piece to promote to
    :return: return_code, pawn to move as object, position where promoted pawn will land, id of the piece to promote to
    '''
    return_code, piece_to_promote, end_position = validate_move(player,player.game.pieces,move)
    if return_code != 0:
        return return_code,None,None,None
    if not id_to_promote in list(PIECE_IDS.keys()):
        return 63,None,None,None
    if piece_to_promote.type.lower() != "pawn":
        return 61,None,None,None
    if not piece_to_promote.position["rank"] in [2,7]:
        return 62,None,None,None
    if not end_position["rank"] in [1,8]:
        return 65,None,None,None
    if id_to_promote in ["W-P","W-K","B-P","B-K"]:
        return 63,None,None,None
    if PIECE_IDS[id_to_promote]["color"] != player.color:
        return 63,None,None,None

    return 2, piece_to_promote,end_position,id_to_promote


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
