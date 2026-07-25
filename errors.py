ERRORS = {
    "description":{
        "21 - 30":"UI - Errors",
        "31 - 40":"Figure - Errors",
        "41 - 50":"User - Errors",
        "51 - 60":"Castle - Errors",
        "91 - 100":"Logic - Errors"
    },
    "lookup":{
        0:"Everything ok!",
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
        91:"This Piece can't Promote",
        92:"This is not a Valid Notation",
        93:"There is no Piece to move?!"
    }
}

def error_lookup(error_code) -> str:
    return ERRORS["lookup"][error_code]



if __name__ == '__main__':
    for i in range(8):
        print(i)