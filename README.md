My new game: "CMinesweeperD" is a classic terminal roguelike. Become a rogue and uncover all the traps!
Features include:
- Infinite procedurally generated dungeon
- Exploration powered by wave function collapse
- An ability system to uncover and/or flag tiles
- Perma-death
- No meta progression
- Configurable dungeon size and traps number
- Completely done in ASCII
- Colors for legibility

---

The idea for this project will be to make a Minesweeper in the terminal.

The game will behave like this:

- The board will be a square of x by y size:
  
  -- A-B-C-D-E-F-G-H-I  
  1 [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ]  
  2 [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ]  
  3 [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ]  
  4 [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ]  
  5 [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ]  
  6 [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ]  
  7 [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ]  
  8 [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ]  
  9 [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ]

- There will be a counter for the bombs at the top of the board, signaling the amount of bombs left to flag

- There will be 5 states for each tile:

  1.  Undiscovered: the tile is blank and can be clicked
  2.  Blank: the tile is discovered but remains blank
  3.  Bomb: the tile is discovered and has a bomb
  4.  Flagged: the tile is undiscovered and is flagged as a bomb, the bomb counter is reduced by one
  5.  Number: the tile is discovered and displays the number of bombs it's adjacent to

- The player will be able to discover a tile by typing the command 'DXY', where X is the column and Y is the row
- The player will be able to flag a tile by typing the command 'FXY', where X is the column and Y is the row

- When a tile is discovered and is blank, it'll forcefully discover any adjacent tiles which are also blank
- When a tile is discovered and is a bomb, it'll forcefully explode every other bomb and the game will be over

- When every bomb is flagged, the player wins