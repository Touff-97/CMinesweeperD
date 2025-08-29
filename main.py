import random

class Colors:
    BLANK = "\033[38;5;15m"
    ZERO = "\033[38;5;245m"
    BOMB = "\033[38;5;1m"
    ONE = "\033[38;5;4m"
    TWO = "\033[38;5;2m"
    THREE = "\033[38;5;9m"
    FOUR = "\033[38;5;14m"
    FIVE = "\033[38;5;5m"
    SIX = "\033[38;5;6m"
    SEVEN = "\033[38;5;3m"
    EIGHT = "\033[38;5;10m"
    FLAG = "\033[38;5;12m"
    WIN = "\033[38;5;10m"
    LOSE = "\033[38;5;1m"

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
        colors = Colors()
        if self.is_flagged:
            return colors.BOMB + "[F]"
        if not self.is_discovered:
            return colors.BLANK + "[ ]"
        if self.is_bomb:
            return colors.BOMB + "[B]"
        if self.adjacent_bombs <= 0:
            return colors.ZERO + "[·]"
        number_color = colors.ONE if self.adjacent_bombs == 1 else colors.TWO if self.adjacent_bombs == 2 else colors.THREE if self.adjacent_bombs == 3 else colors.FOUR if self.adjacent_bombs == 4 else colors.FIVE if self.adjacent_bombs == 5 else colors.SIX if self.adjacent_bombs == 6 else colors.SEVEN if self.adjacent_bombs == 7 else colors.EIGHT
        return number_color + "[{}]"

    def discover(self, is_recursive=True):
        if self.is_flagged:
            return True

        self.is_discovered = True
        self.display = self.update_state()

        if self.is_bomb:
            return False

        if is_recursive and self.adjacent_bombs <= 0:
            adjacency = [(1, 0), (0, 1), (-1, 0), (0, -1)]
            for dx, dy in adjacency:
                adj_x = self.column + dx
                adj_y = self.row + dy
                if 0 <= adj_x < self.board.width and 0 <= adj_y < self.board.height:
                    adj_tile = self.board.tiles[adj_x][adj_y]
                    if not adj_tile.is_discovered and not adj_tile.is_bomb:
                        adj_discover = adj_tile.discover()
                        if not adj_discover:
                            return False

        return True

    def flag(self):
        self.is_flagged = not self.is_flagged
        self.display = self.update_state()


class Board:
    def __init__(self, width, height, max_bombs):
        self.width = width
        self.height = height
        self.max_bombs = max_bombs
        self.bombs = 0
        self.tiles = []

    def __repr__(self):
        colors = Colors()
        board_display = "  "
        for i in range(len(self.tiles)):
            board_display += colors.BLANK + " {} ".format(chr(65 + i)) # Add a letter for each column in the board
        board_display += "\n"
        for x in range(len(self.tiles)):
            board_display += colors.BLANK + "{} ".format(x) # Add a number for each row in the board
            for y in range(len(self.tiles[x])):
                board_display += "{}".format(self.tiles[x][y]) # Add each tile to the board
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
            for tile in col:
                bombs = 0
                adjacency = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
                for dx, dy in adjacency:
                    adj_x = tile.column + dx
                    adj_y = tile.row + dy
                    if 0 <= adj_x < self.width and 0 <= adj_y < self.height:
                        if self.tiles[adj_x][adj_y].is_bomb:
                            bombs += 1
                tile.adjacent_bombs = bombs
                tile.display = tile.update_state()

    def discover_all(self):
        for col in self.tiles:
            for tile in col:
                result = tile.discover(False)
                if not result:
                    return False
        return True

board = Board(10, 10, 10)
board.populate_board()
board.count_bombs()

is_playing = True
colors = Colors()

while is_playing:
    print("Bombs left: {}".format(board.max_bombs - board.bombs))
    print(board)
    print(colors.BLANK + "\nPlease select your next action:")
    print("\n - 'DXY' to discover a tile (where XY is column and row)")
    print("\n - 'FXY' to flag a tile (where XY is column and row)")
    player_input = input().upper()
    tile_x = ord(player_input[1:2]) - 65
    tile_y = int(player_input[2:])
    if 0 <= tile_x < board.width and 0 <= tile_y < board.height:
        if player_input.startswith("D"):
            is_safe = board.tiles[tile_y][tile_x].discover()
            if not is_safe:
                board.discover_all()
                print("Bombs left: {}".format(board.max_bombs - board.bombs))
                print(board)
                print(colors.LOSE + "\nBOOM!")
                print(colors.LOSE + "\nYou triggered a bomb and died!")
                is_playing = False
        elif player_input.startswith("F"):
            if not board.tiles[tile_y][tile_x].is_discovered:
                board.tiles[tile_y][tile_x].flag()
                board.bombs += 1 if board.tiles[tile_y][tile_x].is_flagged else -1
        else:
            print(colors.LOSE + "Error: Invalid Input")

    if board.max_bombs - board.bombs <= 0:
        result = board.discover_all()
        print("Bombs left: {}".format(board.max_bombs - board.bombs))
        print(board)
        if not result:
            print(colors.LOSE + "\nBOOM!")
            print(colors.LOSE + "\nYou've failed to flag every bomb and died!")
            is_playing = False
        print(colors.WIN + "\nYou correctly flagged every bomb and lived!")
        is_playing = False

