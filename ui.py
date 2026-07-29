#####################################################################################
#   Well, another project, another few hundred lines of overcomplicated code.
#   I will try my best to document it.
#
#   Breburda Dejan
#####################################################################################

import logicEngine as LE
from errors import error_lookup

settings = {
    "win_condition_check":True
}

INITIAL_PIECE_POSITION = {"file":-1,"rank":-1}      # that's where pieces are placed initially (not really needed tbh)

# In the following dictionary I am storing all Possible Pieces with their own ID
PIECE_IDS = {
    "W-P":{"name":"White Pawn","value":1,"color":"w","type":"pawn"},
    "W-N":{"name":"White Knight","value":3,"color":"w","type":"knight"},
    "W-B":{"name":"White Bishop","value":3,"color":"w","type":"bishop"},
    "W-R":{"name":"White Rook","value":5,"color":"w","type":"rook"},
    "W-Q":{"name":"White Queen","value":9,"color":"w","type":"queen"},
    "W-K":{"name":"White King","value":99,"color":"w","type":"king"},
    "B-P":{"name":"Black Pawn","value":1,"color":"b","type":"pawn"},
    "B-N":{"name":"Black Knight","value":3,"color":"b","type":"knight"},
    "B-B":{"name":"Black Bishop","value":3,"color":"b","type":"bishop"},
    "B-R":{"name":"Black Rook","value":5,"color":"b","type":"rook"},
    "B-Q":{"name":"Black Queen","value":9,"color":"b","type":"queen"},
    "B-K":{"name":"Black King","value":99,"color":"b","type":"king"}
}


class Piece:
    '''
    This is a Piece class that stores information of a chess-piece on the board, like the position, color and value.
    '''
    def __init__(self,piece_id,position = INITIAL_PIECE_POSITION.copy()):
        self.name = PIECE_IDS[piece_id]["name"]
        self.piece_id = piece_id
        self.value = PIECE_IDS[piece_id]["value"]
        self.color = PIECE_IDS[piece_id]["color"]
        self.type = PIECE_IDS[piece_id]["type"]
        self.is_black = self.color == "b"
        self.is_start = True
        self.can_promote = False
        self.game:ChessBoard = None
        self.player:Player = None
        self.en_passant_able_on_count = -1
        self.valid_positions:list[dict] = []
        self.position = position.copy()
        self.start_position = self.position.copy()

    def __str__(self):
        return f"""------------------------------
{self.name=}
{self.piece_id=}
{self.value=}
{self.type=}
{self.is_black=}
{self.player.name=}
{self.en_passant_able_on_count=}
{self.color=}
{self.is_start=}
{self.start_position=}
{self.position=}
{self.valid_positions=}
------------------------------
"""

    def set_game(self,game:ChessBoard):
        '''
        this is a helper function to tell the Piece which chessboard it belongs to (if there ever be more than one)

        :param game: A Chessboard
        :return: Nothing, not evan a return_code for errorhandling.
        '''
        self.game = game

    def calculate_vector(self,end_position: dict[str,int]):
        new_position_list = [end_position["file"], end_position["rank"]]
        current_position_list = [self.position["file"], self.position["rank"]]
        vector = [x - y for x, y in zip(new_position_list, current_position_list)]
        return vector

    def set_position(self,new_position:dict[str,int],piece_on_new_position:Piece = None,count:int=-1) -> int:
        '''
        this function will set the position the Piece to the new position giving in the param [new_position].
        It will also check if the move is in the valid_positions-list of the Piece itself and if the move is a special move, like en-passant

        :param new_position: The Position the Piece will move to. -format: {"file":[number 1-8], "rank":[number 1-8]}
        :param piece_on_new_position: Reference to another Piece-object, that is currently standing on the new_position, can be None.
        :param count: The count of the game, number of total moves since game-start if you will.
        :return: A return_code, that either indicates everything went as expected, 0, or that something went wrong, any other number.
        '''
        try:
            if (new_position not in self.valid_positions or not [True, True] == [0<=v<=8 for v in new_position.values()]) and new_position != INITIAL_PIECE_POSITION:
                print(new_position)
                print(self.valid_positions)
                raise Exception("not-a-valid-position")
        except Exception as e:
            if str(e) == "not-a-valid-position":
                return 32
            return 31


        if piece_on_new_position != None:
            if piece_on_new_position.color != self.color:
                piece_on_new_position.kill()


        elif self.type.lower()=="pawn": # this block checks if the move was an en-passant ( hopefully )
            direction = (1,-1)[self.is_black]
            vector = self.calculate_vector(new_position)
            if not 0 in vector: # it was an en-passant ( I think ...)
                current_position_list = [self.position["file"], self.position["rank"]]
                pos_of_en_passanted_pawn = {"file":current_position_list[0]+vector[0],"rank":current_position_list[1]}
                en_passanted_pawn:Piece = self.game.get_piece_on_position(pos_of_en_passanted_pawn)
                if en_passanted_pawn != None and en_passanted_pawn.en_passant_able_on_count == self.game.count - 1 and en_passanted_pawn.color != self.color:
                    en_passanted_pawn.kill()


        elif self.type.lower() == "king":
            vector = self.calculate_vector(new_position)
            if abs(vector[0]) == 2 and vector[1] == 0: # this would mean castle!
                if vector[0] > 0:
                    rook: Piece = self.game.get_piece_on_position({"file":8,"rank":self.position["rank"]})
                else:
                    rook: Piece = self.game.get_piece_on_position({"file": 1, "rank": self.position["rank"]})
                rook.position["file"] = new_position["file"]-(int(vector[0]/2))
                rook.position["rank"] = new_position["rank"]
                print(rook.position)
                rook.is_start = False

        if self.is_start and new_position["rank"] in [4,5]:
            self.en_passant_able_on_count = count
        self.position["file"] = new_position["file"]
        self.position["rank"] = new_position["rank"]
        self.is_start = False
        return 0


    def kill(self) -> int:
        '''
        This is used to kill a captured pawn, by removing it from the chessboard-pieces-list, so it can't cause any weird artifact problems.

        :return: A return_code, that either indicates everything went as expected, 0, or that something went wrong, any other number.
        '''
        self.game.pieces.remove(self)
        self.player.pieces.remove(self)
        return 0

    def promote(self,promote_to_id,position:dict[str,int]) -> int:
        '''
        This function is to promote a pawn to any other piece of its color that is not a king or a pawn.

        :param promote_to_id: ID of the Piece to promote to
        :param position: Position where the promoted piece should land
        :return: 0 -> everything works, 33 - > something wrong
        '''
        if PIECE_IDS[promote_to_id]["color"] != ("w","b")[self.is_black] or promote_to_id not in PIECE_IDS.keys() or promote_to_id in ["W-P","W-K","B-P","B-K"]:
            return 33
        self.piece_id = promote_to_id
        self.name = PIECE_IDS[promote_to_id]["name"]
        self.start_position = position.copy()
        self.position = position.copy()
        self.value = PIECE_IDS[promote_to_id]["value"]
        self.type = PIECE_IDS[promote_to_id]["type"]
        return 0

    def print_status(self):
        print(f"""
        {self.piece_id=}
        {self.name=}
        {self.value=}
        {self.is_start=}
        {self.is_black=}
        {self.can_promote=}
        {self.position=}
        {self.valid_positions=}
        """)

# This map holds the initial Game-position by putting the Piece-IDs into any fields
initial_position = {
    8: {1: "B-R", 2: "B-N", 3: "B-B", 4: "B-Q", 5: "B-K", 6: "B-B", 7: "B-N", 8: "B-R"},
    7: {1: "B-P", 2: "B-P", 3: "B-P", 4: "B-P", 5: "B-P", 6: "B-P", 7: "B-P", 8: "B-P"},
    6: {1: "   ", 2: "   ", 3: "   ", 4: "   ", 5: "   ", 6: "   ", 7: "   ", 8: "   "},
    5: {1: "   ", 2: "   ", 3: "   ", 4: "   ", 5: "   ", 6: "   ", 7: "   ", 8: "   "},
    4: {1: "   ", 2: "   ", 3: "   ", 4: "   ", 5: "   ", 6: "   ", 7: "   ", 8: "   "},
    3: {1: "   ", 2: "   ", 3: "   ", 4: "   ", 5: "   ", 6: "   ", 7: "   ", 8: "   "},
    2: {1: "W-P", 2: "W-P", 3: "W-P", 4: "W-P", 5: "W-P", 6: "W-P", 7: "W-P", 8: "W-P"},
    1: {1: "W-R", 2: "W-N", 3: "W-B", 4: "W-Q", 5: "W-K", 6: "W-B", 7: "W-N", 8: "W-R"}
}


class Player:
    '''
    This Player class holds information about the player, like pieces that belong to them and a Reference to their king,
    since that's their most important Piece.
    '''
    def __init__(self,color,pieces):
        self.color = color
        self.name = ("Player white","Player black")[self.color == "b"]
        self.is_turn = False
        self.is_in_check = False
        self.did_castle = False
        self.can_castle = False
        self.run = False
        self.game:ChessBoard = None
        self.pieces:list[Piece] = [piece for piece in pieces if piece.color == self.color]
        for piece in self.pieces:
            piece.player = self
        try:
            self.king:Piece = [piece for piece in self.pieces if piece.type == "king"][0]
        except IndexError:
            self.king:Piece = None


class ChessBoard:
    '''
    This ChessBoard class is used to create a virtual chessboard, setup the initial positions and run the main loop.
    '''
    def __init__(self):
        self.pieces:list[Piece] = []
        for rank in initial_position:
            for file in initial_position[rank]:
                piece_id = initial_position[rank][file]
                if piece_id == "" or piece_id == "   ":
                    continue
                piece = Piece(piece_id,{"file":file,"rank":rank})
                piece.set_game(self)
                self.pieces.append(piece)
        self.player1 = Player("w", self.pieces)
        self.player1.game = self
        self.player2 = Player("b", self.pieces)
        self.player2.game = self
        self.current_Player = self.player1
        self.count = 0
        self.game_snapshots_per_count: dict[int,list[Piece]] = {}


    def get_piece_on_position(self,pos:dict[str,int]) -> Piece:
        '''
        This is a helper function that is used to get a Piece-object of the Piece that is standing on a specific position on the board.

        :param pos: Position - format: {"file":[number 1-8], "rank":[number 1-8]}
        :return: Piece-object
        '''
        piece_of_pos = [piece for piece in self.pieces if piece.position == pos]
        if len(piece_of_pos) == 1:
            return piece_of_pos[0]
        return None


    def display_cli(self,pieces:list[Piece]=None):
        '''
        This is used to display the cli-version of the chessboard.

        :param pieces: a list of all Pieces on the chessboard
        :return: Nothing. not evan a single bit
        '''
        if pieces == None:
            pieces = self.pieces
        xy_piece_lookup = {f"{p.position["file"]},{p.position["rank"]}":p.piece_id for p in pieces}
        for r in range(8):
            r = 8-r
            print(f"{r} : ",end="")
            for f in range(8):
                if f"{f+1},{r}" in xy_piece_lookup:
                    print(f"|{xy_piece_lookup[f"{f+1},{r}"]}|",end="")
                else:
                    print("|   |",end="")
            print()
        print("r/f | A || B || C || D || E || F || G || H |")

    def get_color_of_square(self,position) -> str:
        '''
        This will output the color of a chosen square.

        :param position: Position -> {"file":[1-8],"rank":[1-8]}
        :return: "w" -> square is white, "b" -> square is black
        '''
        if position["file"] % 2 == 0:
            if position["rank"] % 2 != 0:
                return "w"
            else:
                return "b"
        else:
            if position["rank"] % 2 == 0:
                return "w"
            else:
                return "b"

    def snapshot(self):
        '''
        This will create a snapshot of the chessboard by creating new Piece-objects and putting them in a list.

        :return: the newly created list
        '''
        temp_list: list[Piece] = []
        for piece in self.pieces:
            temp_piece = Piece(piece.piece_id,piece.position)
            temp_piece.start_position = piece.start_position
            temp_piece.en_passant_able_on_count = piece.en_passant_able_on_count
            temp_piece.is_start = piece.is_start
            temp_list.append(temp_piece)
        return temp_list.copy()


    def wait_for_cli_input(self) -> int:
        '''
        This will get the input from the user playing this game from the cli in the format:
        [a-h][1-8]-[a-h][1-8]
        for example:
        if you want to move the pawn from E2 to E4, you type e2-e4
        Input is case-insensitive

        :return: A return_code, that either indicates everything went as expected, 0, or that something went wrong, any other number.
        '''
        print("""
Example move Pawn G7 to G5:
G7-G5

You can castle by typing:
o-o     -> short-castle
o-o-o   -> long-castle

You can Promote by typing:
e7-e8 [Piece-ID]

Piece-IOs ->
W-K -> White King\tW-P -> White Pawn\tW-R -> White Rook
W-Q -> White Queen\tW-N -> White Knight\tW-B -> White Bishop

B-K -> Black King\tB-P -> Black Pawn\tB-R -> Black Rook
B-Q -> Black Queen\tB-N -> Black Knight\tB-B -> Black Bishop

        """)
        move = input(f"{['White','Black'][self.current_Player == self.player2]}> ").lower()

        if move.startswith("/"):
            LE.exec_cmd(move,self)
            return 1

        if len(move.strip()) == 9:
            return_code,piece_to_promote,end_position,id_to_promote_to = LE.check_for_promotion(self.current_Player,move.strip().split(" ")[0],move.strip().split(" ")[1].upper())
            if return_code == 2:
                piece_to_promote.promote(id_to_promote_to,end_position)
                return 0
            print(error_lookup(return_code))

        return_code,piece_to_move,where_to_move = LE.validate_move(self.current_Player, self.pieces, move)
        if return_code == 0: ### -1 -> this check is disabled enable by replacing with 0
            if where_to_move["rank"] in [1,8] and piece_to_move.type.lower() == "pawn":
                return 64
            return_code = piece_to_move.set_position(where_to_move,piece_on_new_position=self.get_piece_on_position(where_to_move),count=self.count)
            if return_code == 0:
                self.game_snapshots_per_count[self.count] = self.snapshot()
                self.count += 1
            return return_code
        else:
            return return_code


    def start_cli(self):
        '''
        This will start the main-loop of the cli-version

        :return: not evan an empty string
        '''
        self.run=True
        action = ""
        while self.run:
            self.display_cli()
            return_code = self.wait_for_cli_input()
            if return_code != 0:
                print(error_lookup(return_code))
                continue
            self.current_Player = (self.player1,self.player2)[self.current_Player == self.player1]

            action, player = LE.check_for_win_or_draw(self)
            if action in ["w","d"]:
                self.run = False

        self.display_cli()
        if action == "w":
            print(f"{player.name} Won!")
        elif action == "d":
            print("It's a draw!")


if __name__ == '__main__':
    game = ChessBoard()
    game.start_cli()
