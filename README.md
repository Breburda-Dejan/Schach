# Chess

I thought this was going to be easy, turns out programming chess is way more complicated than i thought.

---
## Installation

1. Download the [latest release](https://github.com/Breburda-Dejan/Schach/releases/latest) ZIP
2. Unzip the downloaded file
3. Navigate to the project directory in your terminal
4. Install dependencies:
```bash
   pip install -r requirements.txt
```
5. Run the application:
```bash
   python app.py
```

---
## How to play
1. Open `127.0.0.1:5000`
2. Play

<!--
## Commands
I implemented a few commands for debugging and testing:

---

### `/show`


+ `/show all` -> Shows every legal move for every piece on the board.
+ `/show white` -> Shows every legal move for every white piece on the board.
+ `/show black` -> Shows every legal move for every black piece on the board.
---
### `/move [a-h][1-8]-[a-h][1-8]`
+ `/move h1-c4` -> Force-moves a piece without checking for checks or blocking pieces.
---
### `/spawn [Piece_ID] [a-h][1-8]`
+ `/spawn B-Q c4` -> Force-spawns a piece with the given ID on the given square, and delete any other 
Piece on the target square.
---
### `/kill [a-h][1-8]`
+ `/kill c4` -> Removes the piece on the given square.
---
### `/clear`
+ `/clear` -> Removes every piece on the board.
---
### `/resign`
+ `/resign` -> Makes the current player resign.
---
### `/load`
+ `/load position [position-name]` -> Will load a saved position
  + Leave the name empty to list all saved positions.
+ `/load game [game-name]` -> Will load a saved game
  + Leave the name empty to list all saved games.
+ `/load count [game-count]` -> Will restore a previous position in this game
  + The count starts at `0` and increases by `1` after every normal move (`/move` does **not** increment it).
---
###  `/save`
+ `/save position [position-name]` -> Will save a position
+ `/save game [game-name]` -> Will save a game
---
### `/count`
+ `/count show` -> Will show the current game-count
+ `/count set [game-count]` -> Sets the Game-count to a given Integer
+ `/count reset` -> Sets the Game-count to 0
---
### `/info [a-h][1-8]`
+ `/info c4` -> Displays information about the piece on `c4`
---
### `/switch`
+ `/switch player` -> Changes the Player that has to play.
---
### `/reset`
+ `/reset` -> Resets the board to the default position.
---
## Features:

- [x] Displayable Chessboard on the CLI
- [x] Different Pieces that are also displayed with start-positions
- [x] A form of Input to move a piece
- [x] Validation system that checks if the Move is possible by the piece performing it
- [x] Checking if the own king is in check
- [x] Check for possible moves that would result in check, and filter them
- [x] Implement En-Passant
- [x] Implement Castle
- [x] Implement Promotion
- [x] Check for Checkmate
- [x] Check for draw
  - [x] Check for draw by insufficient material
  - [x] Check for draw by being unable to move
  - [x] Check for draw by repetition
-->
  