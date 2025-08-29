import random

class Tile:
    def __init__(self, tile_type):
        self.display = "[ ]"
        self.state = "undiscovered"
        self.type = tile_type
        self.adjacent_bombs = 0
        self.update_display()

    def __repr__(self):
        return self.display.format(self.adjacent_bombs)

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
                column.append(Tile(random.randint(0, 4))) # Add a tile to the board
            self.tiles.append(column)

board = Board(10, 10)
board.populate_board()
print(board)