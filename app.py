from flask import Flask, render_template, request, session, redirect, url_for
import requests
from ui import ChessBoard,Piece


app = Flask(__name__)
app.secret_key = "IDK BRO"

field_to_color = {}
for file in range(8):
    if 8-file not in list(field_to_color.keys()):
        field_to_color[8-file] = {}
    for rank in range(8):
        field_to_color[8-file][rank+1] = f"background-color:{('white','gray')[ChessBoard.get_color_of_square({"file":8-file,"rank":rank+1}) == "b"]}"

def location_to_piece_id_list(pieces:list[Piece]):
    pos_to_piece_id = {}
    for piece in pieces:
        if not piece.position["file"] in list(pos_to_piece_id.keys()):
            pos_to_piece_id[piece.position["file"]] = {}
        pos_to_piece_id[piece.position["file"]][piece.position["rank"]] = f'../static/pieces/{piece.piece_id}.svg'
    return pos_to_piece_id



@app.route('/')
def index():
    return render_template('game.html', pieces = location_to_piece_id_list(test_board.pieces), field_to_color = field_to_color)



if __name__ == '__main__':
    test_board = ChessBoard()
    app.run(debug=True)