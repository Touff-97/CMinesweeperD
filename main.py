
class Tile:
    def __init__(self):
        self.display = "[ ]"
        self.state = "undiscovered"
        self.type = "blank"

    def __repr__(self):
        return self.display


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
                column.append(Tile())
            self.tiles.append(column)

board = Board(10, 10)
board.populate_board()
print(board)