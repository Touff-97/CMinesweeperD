import random

class Tile:
    def __init__(self, board, column, row, is_bomb):
        self.board = board
        self.column = column
        self.row = row
        self.is_discovered = False
        self.is_bomb = is_bomb
        self.is_flagged = False
        self.adjacent_bombs = 0
        self.display = self.update_state()

    def __repr__(self):
        return self.display.format(self.adjacent_bombs)

    def update_state(self):
        if self.is_flagged:
            return "[F]"
        if not self.is_discovered:
            return "[ ]"
        if self.is_bomb:
            return "[B]"
        if self.adjacent_bombs <= 0:
            return "[·]"
        return "[{}]"

    def discover(self, is_recursive = True):
        self.is_discovered = True
        self.display = self.update_state()

        if self.is_bomb:
            return False

        if is_recursive:
            adjacency = [(1, 0), (0, 1), (-1, 0), (0, -1)]
            if self.adjacent_bombs <= 0:
                for adjacent in adjacency:
                    adj_tile = self.board.tiles[(self.column - 1) + adjacent[0]][(self.row - 1) + adjacent[1]]
                    if not adj_tile.is_discovered and not adj_tile.is_bomb:
                        adj_tile.discover()

        return True

    def flag(self):
        self.is_flagged = True
        self.display = self.update_state()

class Board:
    def __init__(self, width, height, max_bombs):
        self.width = width
        self.height = height
        self.max_bombs = max_bombs
        self.bombs = 0
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
            bomb_index = random.randint(0, self.width - 1)
            for y in range(self.height):
                if y == bomb_index:
                    is_bomb = True
                else:
                    is_bomb = False
                column.append(Tile(self, x, y, is_bomb)) # Add a tile to the board
            self.tiles.append(column)

    def count_bombs(self):
        for col in self.tiles:
            print(col)
            for tile in col:
                print("{} center is x:{}, y:{}".format(tile, tile.column, tile.row))
                bombs = 0
                adjacency = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
                for adjacent in adjacency:
                    if not tile.column + adjacent[0] < 0 and not tile.column + adjacent[0] > self.width and not tile.row + adjacent[1] < 0 and not tile.row + adjacent[1] > self.height:
                        bombs += 1 if self.tiles[(tile.column - 1) + adjacent[0]][(tile.row - 1) + adjacent[1]].is_bomb else 0
                tile.adjacent_bombs = bombs
                tile.update_state()

    def discover_all(self):
        for col in self.tiles:
            for tile in col:
                tile.discover(False)

board = Board(10, 10, 10)
board.populate_board()
board.count_bombs()
print(board)
board.tiles[0][1].discover()
print(board.tiles[0][1].display)
print(board.tiles[0][1].is_discovered)
print(board.tiles[0][1].is_bomb)
print(board.tiles[0][1].update_state())
print(board)
board.discover_all()
print(board)
