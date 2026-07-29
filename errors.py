ERRORS = {
    "description":{
        "0 - 10" :"All - Correct",
        "21 - 30":"UI - Errors",
        "31 - 40":"Figure - Errors",
        "41 - 50":"User - Errors",
        "51 - 60":"Castle - Errors",
        "61 - 70":"Promotion - Errors",
        "91 - 100":"Logic - Errors"
    },
    "lookup":{
        0:"Everything ok!",
        1:"Ok, but command executed",
        2:"Ok, but promoted",
        21:"Not a valid Mode",
        31:"Not a Position",
        32:"Not a valid Move",
        33:"Not a valid Piece to promote to",
        41:"You can't Move this piece",
        51:"You can't Castle, your king has moved before",
        52:"You can't Castle, your rook has moved before",
        53:"You can't Castle, there are pieces in the way",
        54:"You can't Castle, there is check in the way",
        55:"You can't Castle, you are in check",
        61:"This is not a promotable piece",
        62:"This pawn is not on a rank where it can promote",
        63:"Not a valid Piece to promote to",
        64:"This pawn has to promote in order to move forward!",
        65:"This pawn can't promote now",
        91:"This Piece can't Promote",
        92:"This is not a Valid Notation",
        93:"There is no Piece to move?!"
    }
}

def error_lookup(error_code) -> str:
    return ERRORS["lookup"][error_code]



if __name__ == '__main__':
    ...