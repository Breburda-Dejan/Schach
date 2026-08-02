from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import requests
from ui import ChessBoard,Piece

list_of_games:dict[str,Game] = {}

app = Flask(__name__)
app.secret_key = "IDK BRO"
socketio = SocketIO(app)


def game_id_generator():
    import random
    import string
    id =  ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    if id not in list(list_of_games.keys()):
        return id
    else:
        return game_id_generator()

class Game:
    def __init__(self):
        self.game_id = game_id_generator()
        list_of_games[self.game_id] = self
        self.chess_board:ChessBoard = ChessBoard()
        self.next_move_notation = ""
        self.last_move_notation = ""
        self.selected_square = {"file":-1,"rank":-1}
    
    def select_square(self, square):
        piece_on_square = self.chess_board.get_piece_on_position(square)
        if piece_on_square is not None:
            if piece_on_square.color == self.chess_board.current_Player.color:
                self.selected_square = square
                self.next_move_notation = position_to_notation(square["file"],square["rank"])
            else:
                return 41
        else:
            return 93

    def make_a_move(self):
        outcome,player = self.chess_board.gui_input(self.next_move_notation)
        if outcome != "n":
            socketio.emit("gameOutcome",{"result":outcome,"player":player},to=self.game_id)
            list_of_games.pop(self.game_id)
        self.last_move_notation = self.next_move_notation
        self.next_move_notation = ""
        self.selected_square = {"file":-1,"rank":-1}
        self.reload_gui()
        

    def reload_gui(self):
        valid_moves = []
        valid_moves_raw = []
        if self.selected_square != {"file":-1,"rank":-1}:
            piece = self.chess_board.get_piece_on_position(self.selected_square)
            if piece is not None:
                piece.update_valid_moves()
                valid_moves_raw = piece.valid_positions
        
        if len(valid_moves_raw) > 0:
            valid_moves = [f"{pos["file"]},{pos["rank"]}" for pos in valid_moves_raw]

        data = {
            "turn":self.chess_board.current_Player.color,
            "selected_square":self.selected_square,
            "valid_moves": valid_moves
        }
        socketio.emit("reload",{ "positions":location_to_piece_id_list(self.chess_board.pieces),"data": data}, to=self.game_id)
            


field_to_color = {}
for file in range(8):
    if 8-file not in list(field_to_color.keys()):
        field_to_color[8-file] = {}
    for rank in range(8):
        field_to_color[8-file][rank+1] = f"background-color:{('white','gray')[ChessBoard.get_color_of_square({"file":8-file,"rank":rank+1}) == "b"]}"

def location_to_piece_id_list(pieces:list[Piece]):
    pos_to_piece_id = {}
    for f in range(8):
        f+=1
        pos_to_piece_id[f] = {}
        for r in range(8):
            r+=1
            pos_to_piece_id[f][r] = ""

    for piece in pieces:
        pos_to_piece_id[piece.position["file"]][piece.position["rank"]] = piece.piece_id
    return pos_to_piece_id


def position_to_notation(file,rank):
    files = ['a','b','c','d','e','f','g','h']
    return f"{files[file-1]}{rank}"




@app.route('/')
def start_screen():
    return render_template("index.html")


@app.route('/<game_id>/<player>')
def game_view(game_id, player):
    game = list_of_games.get(game_id)
    player = player.lower()
    if game == None:
        return redirect("/")
    if player not in ["w","b","w-b"]:
        return 'Player must be w or b or w-b', 404
    pieces = game.chess_board.pieces
    player_name = {"w":"White","b":"Black","w-b":"Game"}[player.lower()]
    selected_square = [game.selected_square["file"],game.selected_square["rank"]]
    return render_template('game.html', pieces = location_to_piece_id_list(pieces), field_to_color = field_to_color, player=player, player_name = player_name, is_turn = game.chess_board.current_Player.color == player, selected_square = selected_square, game_id = game_id)



@app.route('/handle_click/<game_id>', methods=['POST'])
def handle_click(game_id):
    data = request.get_json()
    f = data['f']
    r = data['r']
    p = " "+data['p'].capitalize()
    print(f"Selected field: file={f}, rank={r}")
    pos = {"file":f,"rank":r}
    game = list_of_games.get(game_id)
    piece_on_pos = game.chess_board.get_piece_on_position(pos)
    
    if game is not None:
        if game.next_move_notation != "" and (piece_on_pos is None or (piece_on_pos is not None and piece_on_pos.color != game.chess_board.current_Player.color)):
            game.next_move_notation += "-"+position_to_notation(f,r)+p
            print(game.next_move_notation)
            game.make_a_move()
        else:
            game.select_square({"file":f,"rank":r})
            print("setting selected square!")
            
    else:
        return "Game doesn't exist", 404        

    game.reload_gui()
    return "", 200


@app.route('/new/<mode>')
def create_game(mode):
    new_game = Game()
    if mode in ["w","w-b"]:
        return redirect(f"/{new_game.game_id}/{mode}")
    return redirect(f"/{new_game.game_id}/w")


@socketio.on('join_game')
def join_game(game_id):
    join_room(game_id)
    game = list_of_games.get(game_id)
    if game is not None:
        game.reload_gui()


if __name__ == '__main__':
    socketio.run(app,debug=True)