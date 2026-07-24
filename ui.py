#####################################################################################
#   Well, another project, another few hundred lines of overcomplicated code.
#   I will try my best to document it.
#
#   Breburda Dejan
#####################################################################################

from errors import error_lookup
import logicEngine as LE

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


    def __str__(self):
        return self.piece_id

    def set_game(self,game:ChessBoard):
        '''
        this is a helper function to tell the Piece which chessboard it belongs to (if there ever be more than one)

        :param game: A Chessboard
        :return: Nothing, not evan a return_code for errorhandling.
        '''
        self.game = game

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
                raise Exception("not-a-valid-position")
            if piece_on_new_position != None:
                if piece_on_new_position.color != self.color:
                    piece_on_new_position.kill()
            elif self.type.lower()=="pawn": # this block checks if the move was an en-passant ( hopefully )
                direction = (1,-1)[self.is_black]
                new_position_list = [new_position["file"],new_position["rank"]]
                current_position_list = [self.position["file"],self.position["rank"]]
                vector = [x - y for x,y in zip(new_position_list,current_position_list)]
                if not 0 in vector: # it was an en-passant ( i think ...)
                    pos_of_en_passanted_pawn = {"file":current_position_list[0]+vector[0],"rank":current_position_list[1]}
                    en_passanted_pawn:Piece = self.game.get_piece_on_position(pos_of_en_passanted_pawn)
                    if en_passanted_pawn != None and en_passanted_pawn.en_passant_able_on_count == self.game.count - 1 and en_passanted_pawn.color != self.color:
                        en_passanted_pawn.kill()

            if self.is_start and new_position["rank"] in [4,5]:
                self.en_passant_able_on_count = count
            self.position["file"] = new_position["file"]
            self.position["rank"] = new_position["rank"]
            self.is_start = False
            return 0
        except Exception as e:
            if str(e) == "not-a-valid-position":
                return 32
            return 31

    def kill(self) -> int:
        '''
        This is used to kill a captured pawn, by removing it from the chessboard-pieces-list, so it can't cause any weird artifact problems.

        :return: A return_code, that either indicates everything went as expected, 0, or that something went wrong, any other number.
        '''
        self.game.pieces.remove(self)
        return 0

    def promote(self,promote_to_id) -> int:
        '''
        This function is for promoting a Piece to a Piece of choice by giving it the ID of the Piece it should promote to.

        :param promote_to_id: ID of the Piece it should promote to
        :return: A return_code, that either indicates everything went as expected, 0, or that something went wrong, any other number.
        '''
        if not self.can_promote:
            return 91
        if PIECE_IDS[promote_to_id]["color"] != ("w","b")[self.is_black] or promote_to_id not in PIECE_IDS.keys() or promote_to_id in ["W-P","W-K","B-P","B-K"]:
            return 33
        self.piece_id = promote_to_id
        self.name = PIECE_IDS[promote_to_id]["name"]
        self.can_promote = False
        self.value = PIECE_IDS[promote_to_id]["value"]
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
    8:{1:"B-R",2:"B-N",3:"B-B",4:"B-Q",5:"B-K",6:"B-B",7:"B-N",8:"B-R"},
    7:{1:"B-P",2:"B-P",3:"B-P",4:"B-P",5:"B-P",6:"B-P",7:"B-P",8:"B-P"},
    6:{1:"",2:"",3:"",4:"",5:"",6:"",7:"",8:""},
    5:{1:"",2:"",3:"",4:"",5:"",6:"",7:"",8:""},
    4:{1:"",2:"",3:"",4:"",5:"",6:"",7:"",8:""},
    3:{1:"",2:"",3:"",4:"",5:"",6:"",7:"",8:""},
    2:{1:"W-P",2:"W-P",3:"W-P",4:"W-P",5:"W-P",6:"W-P",7:"W-P",8:"W-P"},
    1:{1:"W-R",2:"W-N",3:"W-B",4:"W-Q",5:"W-K",6:"W-B",7:"W-N",8:"W-R"}
}

# This is a Testing position for debugging, so I don't have to play through a normal chess-game in order to test one feature
test_position = {
    8:{1:"B-R",2:"B-N",3:"B-B",4:"B-Q",5:"B-K",6:"B-B",7:"B-N",8:"B-R"},
    7:{1:"B-P",2:"B-P",3:"B-P",4:"B-P",5:"B-P",6:"B-P",7:"B-P",8:"B-P"},
    6:{1:"",2:"",3:"",4:"",5:"",6:"",7:"",8:""},
    5:{1:"",2:"",3:"",4:"",5:"",6:"",7:"",8:""},
    4:{1:"",2:"",3:"",4:"",5:"",6:"",7:"",8:"B-B"},
    3:{1:"",2:"",3:"",4:"",5:"",6:"",7:"",8:""},
    2:{1:"W-P",2:"W-P",3:"W-P",4:"W-P",5:"W-P",6:"",7:"W-P",8:"W-P"},
    1:{1:"W-R",2:"W-N",3:"W-B",4:"W-Q",5:"W-K",6:"W-B",7:"W-N",8:"W-R"}
}


class Player:
    '''
    This Player class holds information about the player, like pieces that belong to them and a Reference to their king,
    since that's their most important Piece.
    '''
    def __init__(self,color,pieces):
        self.color = color
        self.is_turn = False
        self.is_in_check = False
        self.did_castle = False
        self.can_castle = False
        self.run = False
        self.game:ChessBoard = None
        self.pieces = [piece for piece in pieces if piece.color == self.color]
        for piece in self.pieces:
            piece.player = self
        self.king:Piece = [piece for piece in self.pieces if piece.type == "king"][0]


class ChessBoard:
    '''
    This ChessBoard class is used to create a virtual chessboard, setup the initial positions and run the main loop.
    '''
    def __init__(self):
        self.pieces = []
        initial_position = test_position # This is for testing
        for rank in initial_position:
            for file in initial_position[rank]:
                piece_id = initial_position[rank][file]
                if piece_id == "":
                    continue
                piece = Piece(piece_id,{"file":file,"rank":rank})
                piece.set_game(self)
                self.pieces.append(piece)
        self.player1 = Player("w", self.pieces)
        self.player1.game = self
        self.player2 = Player("b", self.pieces)
        self.player2.game = self
        self.current_Player = self.player1
        self.count = -1


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
        """)
        move = input(f"{['White','Black'][self.current_Player == self.player2]}> ").lower()
        return_code,piece_to_move,where_to_move = LE.validate_move(self.current_Player, self.pieces, move)
        if return_code == 0: ### -1 -> this check is disabled enable by replacing with 0
            self.count += 1
            return piece_to_move.set_position(where_to_move,piece_on_new_position=self.get_piece_on_position(where_to_move),count=self.count)
        else:
            print(error_lookup(return_code))
            return return_code


    def start_cli(self):
        '''
        This will start the main-loop of the cli-version

        :return: not evan an empty string
        '''
        self.run=True
        while self.run:
            self.display_cli()
            if self.wait_for_cli_input() != 0:
                continue
            self.current_Player = (self.player1,self.player2)[self.current_Player == self.player1]


if __name__ == '__main__':
    game = ChessBoard()
    game.start_cli()
