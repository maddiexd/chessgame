# Chess game
This is a python chess game I made back in 2024/2025 for my A-level computer science project. The move generation is slow, but functional. As far as I can tell, this follows all of the rules of chess.
If this does **not** follow any rule of chess, submit an issue and I may fix it later on.

---
## Features:
- Built-in rules button made by yours truly
- Ability to play against stockfish at custom difficulty and select team for yourself.
- Ability to play with your friends locally with pass and play.
- Ability to play from a custom layout
- Customisable chess clock which is pretty accurate
- Ability to play previous games back.
- Ability to export your game as a semi-compliant PGN
- Ability to import a list of PGNs as a game.
- Games are auto-saved, with the ability to resume from previous position and timer.
- Running game.py will have two stockfishes play against each other.
---
## How to play:
1. Install dependencies with ``` pip install -r requirements.txt ```
2. Install stockfish on your system and add it to your PATH as ```stockfish``` **OR** Add the path to your stockfish binary to the top of ```stockfishes.txt```
3. Run the game with ```python menu.py```
