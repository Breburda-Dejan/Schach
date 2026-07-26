# Chess

---
I thought this was going to be easy, turns out programing chess is way more complicated than i thought.

Well, I will do it anyway. Without using any AI btw.

---
## Installation

1. ```bash
   git clone https://github.com/Breburda-Dejan/Schach.git
   ```
2. Well that's it, just open the folder and run `python ui.pi`

---
## How to play
> All pieces have their own ID:<br>
> **W-P**  -> White Pawn <br>
> **W-N**  -> White Knight <br>
> **W-B**  -> White Bishop <br>
> **W-R**  -> White Rook <br>
> **W-Q**  -> White Queen <br>
> **W-K**  -> White King
> 
> Black pieces have the same ID with the W swapped to an B, so **B-P, B-N, ...**

> If you want to move pawn e2 to e4, type **e2-e4**
> 
> You can also castle by typing: <br>
> **o-o**  -> short castle<br>
> **o-o-o** -> long castle


---
## Commands
I Implemented some commands for debugging and testing:

---

### `/show`


+ `/show all` -> Will show every valid position for every piece on the board
+ `/show white` -> Will show every valid position for every white piece on the board
+ `/show black` -> Will show every valid position for every black piece on the board
---
### `/move [a-h][1-8]-[a-h][1-8]`
+ `/move h1-c4` -> Will force-move the piece without checking for checks or other pieces on the board

---
### `/spawn [Piece_ID] [a-h][1-8]`
+ `/spawn B-Q c4` -> Will force-create a Piece with the given ID on the given square, and delete any other 
Piece on the target square
---
### `/kill [a-h][1-8]`
+ `/kill c4` -> Will force-kill the Piece on the given square
---
### `/clear`
+ `/clear` -> Will delete every piece on the screen
---
### `/resign`
+ `/resign` -> Will make the player, who's turn it is, resign
---
### `/load`
+ `/load position [position-name]` -> Will load a saved position
  + empty name to get a list of saved positions
+ `/load game [game-name]` -> Will load a saved game
  + empty name to get a list of saved games
+ `/load count [game-count]` -> Will restore a previous position in this game
  + count -> Integer that starts from 0, +1 added after every move played (**/move** ***excluded***)
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
+ `/info c4` -> Will give infos of the Piece standing on the c4-square

---
## Requirements for a working chess-game:

- [x] Displayable Chessboard on the CLI
- [x] Different Pieces that are also displayed with start-positions
- [x] A form of Input to move a piece
- [x] Validation system that checks if the Move is possible by the piece performing it
- [x] Checking if the own king is in check
- [x] Check for Possible moves that would result in check, and filter them
- [x] Implement En-Passant
- [x] Implement Castle
- [x] Check for Checkmate
- [x] Check for Draw
  - [x] Check for Draw by unsufficient material
  - [x] Check for Draw by being unable to move
  - [x] Check for Draw by repetition

  