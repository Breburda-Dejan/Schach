from __future__ import annotations
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_socketio import SocketIO, send, emit, join_room, leave_room,rooms
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from threading import Lock
import requests, os, time
from ui import ChessBoard,Piece
import logicEngine as LE

list_of_games:dict[str,Game] = {}

open_groups:dict[str,list[str]] = {}
open_groups_lock = Lock()

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]
socketio = SocketIO(app,ping_timeout=60,ping_interval = 10)


def game_id_generator():
    import random
    import string
    id =  ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    if id not in list(list_of_games.keys()):
        return id
    else:
        return game_id_generator()

class Game:
    def __init__(self,name):
        self.game_id = game_id_generator()
        self.game_name = name
        list_of_games[self.game_id] = self
        self.chess_board:ChessBoard = ChessBoard()
        self.next_move_notation = ""
        self.last_move_notation = ""
        self.white_player = None
        self.black_player = None
        self.users = []
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
        return_code,outcome,player = self.chess_board.gui_input(self.next_move_notation)
        if outcome != "n":
            socketio.emit("gameOutcome",{"result":outcome,"player":player},to=self.game_id)
            list_of_games.pop(self.game_id)
        if return_code == 0:
            self.last_move_notation = self.next_move_notation
        self.next_move_notation = ""
        self.selected_square = {"file":-1,"rank":-1}
        self.reload_gui()
        

    def reload_gui(self):
        valid_moves = []
        valid_moves_raw = []
        last_move = [{"file":-1,"rank":-1},{"file":-1,"rank":-1}]
        pos_of_check = {"file":-1,"rank":-1}
        if self.selected_square != {"file":-1,"rank":-1}:
            piece = self.chess_board.get_piece_on_position(self.selected_square)
            if piece is not None:
                piece.update_valid_moves()
                valid_moves_raw = piece.valid_positions
        
        if len(valid_moves_raw) > 0:
            valid_moves = [f"{pos["file"]},{pos["rank"]}" for pos in valid_moves_raw]


        if self.last_move_notation != "":
            move = self.last_move_notation[:5].strip()
            start = move[:2]
            end = move[3:]
            start_pos = LE.map_notation_to_move(start)
            end_pos = LE.map_notation_to_move(end)
            last_move = [start_pos,end_pos]

        if self.chess_board.player1.is_in_check:
            print("p1 in check")
            pos_of_check = self.chess_board.player1.king.position
        elif self.chess_board.player2.is_in_check:
            print("p2 in check")
            pos_of_check = self.chess_board.player2.king.position


        data = {
            "turn":self.chess_board.current_Player.color,
            "selected_square":self.selected_square,
            "valid_moves": valid_moves,
            "last_move": last_move,
            "in_check_square": pos_of_check
        }
        socketio.emit("reload",{ "positions":location_to_piece_id_list(self.chess_board.pieces),"data": data}, to=self.game_id)
            


field_to_color = {}
for file in range(8):
    if 8-file not in list(field_to_color.keys()):
        field_to_color[8-file] = {}
    for rank in range(8):
        field_to_color[8-file][rank+1] = f"{('light_square','dark_square')[ChessBoard.get_color_of_square({"file":8-file,"rank":rank+1}) == "b"]}"

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


@app.route('/<game_id>/<player>', methods=['GET','POST'])
def game_view(game_id, player):
    print(game_id)
    print(player)
    game = list_of_games.get(game_id)
    player = player.lower()
    if game == None:
        print("lets go back")
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


@app.route('/new/<mode>',methods=['POST'])
def new_game(mode):
    data = request.get_json()
    print(data)
    name = data["name"]
    print(name)
    new_game = Game(name)
    return jsonify({"redirect":f"/{new_game.game_id}/{mode}"})


@app.route('/create-game',methods=['GET'])
def create_game():
    name = request.args.get("name")
    mode = ("w","b")[request.args.get("player").lower() == "black"]
    print(name)
    new_game = Game(name)
    return redirect(f"/{new_game.game_id}/{mode}")


@app.route('/available_games',methods=['GET'])
def available_games():
    game_ids_to_name  = []
    with open_groups_lock:
        snapshot = open_groups.copy()

    for game_id, game in snapshot.items():
        full = [False,False]
        for i,color in enumerate(["w","b"]):
            full[i] = any([c.get("color").lower().__contains__(color) or color.__contains__(c.get("color").lower()) for c in open_groups[game_id].values() if type(c) == dict])
        if not all(full):
            game_ids_to_name.append({"id":game_id,"name":list_of_games[game_id].game_name})    

        
    return game_ids_to_name


@app.route('/join/<game_id>',methods=['GET'])
def join(game_id):
    print("-_"*30)
    print(game_id)
    with open_groups_lock:
        for color in ["w","b"]:
            print(color)
            print(open_groups)
            if any([c.get("color").lower().__contains__(color) or color.__contains__(c.get("color").lower()) for c in open_groups[game_id].values() if type(c) == dict]):
                print("continue")
                continue
            print("redirect to game view")
            return jsonify({"redirect":f"/{game_id}/{color}"})

    return redirect("/")



@socketio.on('disconnect')
def on_disconnect():
    print("-"*20)
    sid = request.sid
    print(sid)
    print("disconnect")
    with open_groups_lock:
        for key, value in open_groups.items():
            value.pop(sid, None)


@socketio.on('join_game')
def join_game(data):
    game_id = data["game_id"]
    choosen_color = data.get("color")
    game = list_of_games.get(game_id)
    sid = request.sid
    if game is not None:
        with open_groups_lock:
            if game_id not in open_groups.keys():
                open_groups[game_id] = {"last-seen":0}
            for color in [[choosen_color],["w","b"]][choosen_color == None]:
                print(color)
                print(open_groups)
                if any([c.get("color").lower().__contains__(color) or color.__contains__(c.get("color").lower()) for c in open_groups[game_id].values() if type(c) == dict]) and open_groups[game_id].get(sid,{"color":""}).get("color") != color:
                    print("continue")
                    continue
                print("thats fine")
                open_groups[game_id][sid] = {"color":color}
                open_groups[game_id]["last-seen"] = current_milli_time()
                join_room(game_id)
                game.reload_gui()
                return


@socketio.on('heart_beat')
def heart_neat():
    sid = request.sid
    with open_groups_lock:
        for game in open_groups.values():
            if sid in game:
                game["last-seen"] = current_milli_time()
    

def current_milli_time():
    return round(time.time() * 1000)


def check_for_games_with_0_player():
    print("checking...")
    with open_groups_lock:
        snapshot = open_groups.copy()
    print(snapshot)

    for game_id,game in open_groups.items():
        if len(game) <= 1:
            print("noone is playing that shit...\nCan i delete?")
            if current_milli_time() >= game["last-seen"] + 30*60*1000:
                print("ye. lets delete...")
                del list_of_games[game_id]
                list_of_games.pop(game_id,None)
                with open_groups_lock:
                    open_groups.pop(game_id)
            else:
                print("nah, its to early")



if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_for_games_with_0_player,"interval",minutes=10)
    scheduler.start()
    socketio.run(app,port=5808)