import random

class Tile:
    def __init__(self, column, row, is_bomb):
        self.column = column
        self.row = row
        self.display = "[ ]"
        self.is_discovered = True
        self.is_bomb = is_bomb
        self.is_flagged = False
        self.adjacent_bombs = 0
        self.type = self.update_state()
        self.update_display()

    def __repr__(self):
        return self.display.format(self.adjacent_bombs) if self.is_discovered else "[ ]"

    def update_display(self):
        match self.type:
            case 0:
                self.display = "[ ]"
            case 1:
                self.display = "[·]"
            case 2:
                self.display = "[B]"
            case 3:
                self.display = "[F]"
            case 4:
                self.display = "[{}]"

    def update_state(self):
        if not self.is_discovered:
            return 0
        if self.is_flagged:
            return 3
        if self.is_bomb:
            return 2
        if self.adjacent_bombs <= 0:
            return 1
        return 4



class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = []

    def __repr__(self):
        board_display = "  "
        for i in range(len(self.tiles)):
            board_display += " {}  ".format(chr(65 + i)) # Add a letter for each column in the board
        board_display += "\n"
        for x in range(len(self.tiles)):
            board_display += "{} ".format(x) # Add a number for each row in the board
            for y in range(len(self.tiles[x])):
                board_display += "{} ".format(self.tiles[x][y]) # Add each tile to the board
            board_display += "\n"

        return board_display

    def populate_board(self):
        for x in range(self.width):
            column = []
            for y in range(self.height):
                column.append(Tile(x, y, random.randint(0, 4))) # Add a tile to the board
            self.tiles.append(column)

    def count_bombs(self):
        for tile in self.tiles:
            bombs = 0
            for i in range(-1, 1, 1):
                for j in range(-1, 1, 1):
                    bombs += 1 if self.tiles[tile.column + i][tile.row + i].is_bomb else 0
            tile.adjacent_bombs = bombs

board = Board(10, 10)
board.populate_board()
print(board)