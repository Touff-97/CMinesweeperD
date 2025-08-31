import curses
import random

from curses import wrapper


class Colors:
    BLANK = "\033[38;5;15m"     # White
    ZERO = "\033[38;5;245m"     # Gray
    BOMB = "\033[38;5;52m"      # Dark Red
    ONE = "\033[38;5;4m"        # Dark Blue
    TWO = "\033[38;5;2m"        # Dark Green
    THREE = "\033[38;5;124m"    # Red
    FOUR = "\033[38;5;14m"      # Cyan
    FIVE = "\033[38;5;5m"       # Purple
    SIX = "\033[38;5;6m"        # Teal
    SEVEN = "\033[38;5;3m"      # Dark Yellow
    EIGHT = "\033[38;5;10m"     # Lime Green
    FLAG = "\033[38;5;196m"     # Blue
    WIN = "\033[38;5;10m"       # Green
    LOSE = "\033[38;5;1m"       # Dark Red


class Tile:
    def __init__(self, position, tile_type = " "):
        self.tile_type = tile_type
        self.position = position

    def __repr__(self):
        return "[{}]".format(self.tile_type)

class SafeTile(Tile):
    def __init__(self, position, is_discovered = False, is_flagged = False, tile_type = " "):
        super().__init__(self, position, tile_type)
        self.is_discovered = is_discovered
        self.is_flagged = is_flagged
        self.adjacent_bombs = 0

    def __repr__(self):
        return super.__repr__(self) if self.is_discovered else "[ ]"

    def discover(self):
        if self.is_flagged:
            return True

        self.is_discovered = True
        return True

    def flag(self):
        self.is_flagged = not self.is_flagged


class BombTile(Tile):
    def __init__(self, position, is_discovered = False, is_flagged = False, tile_type = " "):
        super().__init__(self, position, tile_type)
        self.is_discovered = is_discovered
        self.is_flagged = is_flagged

    def __repr__(self):
        return super.__repr__(self) if self.is_discovered else "[ ]"

    def discover(self):
        if self.is_flagged:
            return True

        self.is_discovered = True
        return False

    def flag(self):
        self.is_flagged = not self.is_flagged


class DoorTile(Tile):
    def __init__(self, position, is_discovered = False, tile_type = " "):
        super().__init__(self, position, tile_type)
        self.is_discovered = is_discovered
        self.is_locked = True

    def discover(self):
        if self.is_locked:
            return True

        self.is_discovered = True
        return True

    def get_door_direction(self):
        if self.position[1] == 0:
            return "^"
        elif self.position[1] < self.position[0]:
            return ">"
        elif self.position[1] > self.position[0]:
            return "v"
        elif self.position[0] == 0:
            return "<"

        return "D"


class StairTile(Tile):
    # TODO:
    # Add stair tile to the last room of the dungeon
    # Display it once the board is clear
    # Allow to continue to next floor when in the same room
    pass


class Board:
    max_bombs = 0

    def __init__(self, position, size, border = 1):
        self.position = position
        self.size = size
        self.border = border
        self.tiles = []

    def __repr__(self):
        board_display = ""
        for i in range(len(self.tiles) - (2 * self.border)):
            board_display += "      {} ".format(chr(65 + i)) if i == 0 else " {} ".format(chr(65 + i)) # Add a letter for each column in the board
        board_display += "\n"
        for x in range(len(self.tiles)):
            board_display += "{: <2s} ".format(str(x - 1)) if not x == 0 and not x == len(
                self.tiles) - 1 else "   "  # Add a number for each row in the board
            for y in range(len(self.tiles[x])):
                board_display += "{}".format(self.tiles[x][y])  # Add each tile to the board
            board_display += "\n"

        return board_display

    def get_playable_rect(self):
        origin = (self.position[0] + self.border, self.position[1] + self.border)
        end = ((self.size[0] - 1) - self.border, (self.size[1] - 1) - self.border) # Pending removal of '- 1' if it's not needed
        return origin, end

    def is_inside_playable_rect(self, pos):
        origin, end = self.get_playable_rect()
        return origin[0] <= pos[0] <= end[0] and origin[1] <= pos[1] <= end[1]

    def populate(self):
        origin, end = self.get_playable_rect()
        playable_positions = [
            (x, y)
            for x in range(origin[0], end[0])
            for y in range(origin[1], end[1])
        ]
        bomb_positions = random.sample(playable_positions, self.max_bombs)

        for x in range(self.size[0]):
            column = []
            for y in range(self.size[1]):
                if self.is_inside_playable_rect((x, y)):
                    if (x, y) in bomb_positions:
                        column.append(BombTile((x, y), tile_type="B"))
                    else:
                        column.append(SafeTile((x, y), tile_type="·"))
                else:
                    mid_x = self.size[0] // 2
                    mid_y = self.size[1] // 2

                    if (x == mid_x and y == 0) or \
                       (x == 0 and y == mid_y) or \
                       (x == mid_x and y == self.size[1] - 1) or \
                       (x == self.size[0] - 1 and y == mid_y):
                        column.append(DoorTile((x, y), tile_type="#"))
                    else:
                        column.append(Tile((x, y), tile_type="#"))
            self.tiles.append(column)

    def get_bombs(self):
        bombs = []
        for col in self.tiles:
            for tile in col:
                if isinstance(tile, BombTile):
                    bombs.append(tile)
        return bombs

    def get_remaining_bombs(self):
        remaining = 0
        for col in self.tiles:
            for tile in col:
                if isinstance(tile, BombTile) and not tile.is_flagged:
                    remaining += 1
        return remaining

    def propagate_discover(self, position):
        neighbouring_tiles = [self.tiles[x][y] for x in range(len(self.tiles)) for y in range(len(self.tiles[0])) if abs(x - position[0]) <= 1 and abs(y - position[1]) <= 0 or abs(x - position[0]) <= 0 and abs(y - position[1]) <= 1]

        for n_tile in neighbouring_tiles:
            if self.is_inside_playable_rect(n_tile.position):
                if not n_tile.is_discovered and not isinstance(n_tile, BombTile):
                    result = n_tile.discover()
                    if not result:
                        return False
                    prop_result = self.propagate_discover(n_tile.position)
                    if not prop_result:
                        return False
        return True

    def reveal(self):
        triggered_bomb = False
        for col in self.tiles:
            for tile in col:
                if hasattr(tile, "discover"):
                    result = tile.discover()
                    if not result:
                        triggered_bomb = True
        return not triggered_bomb


class Room:
    def __init__(self, position):
        self.position = position
        self.connections = [None] * 4  # [N, W, S, E]
        self.board = None

    def __repr__(self):
        return "Room {}\n{}".format(self.position, self.board)


class Dungeon:
    max_rooms = 0

    def __init__(self, size):
        self.size = size
        self.rooms = []

    def __repr__(self):
        dungeon_map = "  "
        for i in range(self.size[0]):
            dungeon_map += "{} ".format(chr(65 + i)) # Add a letter for each column in the board
        dungeon_map += "\n"
        for i in range(self.size[0]):
            dungeon_map += "{} ".format(i)  # Add a number for each row in the board
            for j in range(self.size[1]):
                if self.room_exists_at((j, i)):
                    dungeon_map += ""
                    room = self.get_room_at((j, i))
                    if room.is_start:
                        dungeon_map += "S "
                    elif room.is_end:
                        dungeon_map += "E "
                    else:
                        dungeon_map += "O "
                else:
                    dungeon_map += "X "
            dungeon_map += "\n"
        return dungeon_map

    def room_exists_at(self, position):
        return any(room.position == position for room in self.rooms)

    def get_room_at(self, position):
        for room in self.rooms:
            if room.position == position:
                return room
        return None

    def is_last_room(self, room):
        return self.rooms[-1] == room

    def generate_floor(self):
        print("Generating dungeon floor layout...")
        starting_position = (random.randint(0, self.size[0] - 1), random.randint(0, self.size[1] - 1))
        starting_room = Room(starting_position)
        self.rooms.append(starting_room)

        while len(self.rooms) < self.max_rooms:
            random_room = random.choice(self.rooms)
            adjacency = [(0, -1), (-1, 0), (0, 1), (1, 0)]  # N, W, S, E

            while adjacency:
                random_adj = random.choice(adjacency)

                adjacency_index = adjacency.index(random_adj)
                reverse_index = (adjacency_index + 2) % 4

                adjacency.pop(adjacency_index)

                adj_x = random_room.position[0] + random_adj[0]
                adj_y = random_room.position[1] + random_adj[1]
                new_position = (adj_x, adj_y)

                if (0 <= adj_x < self.size[0] and 0 <= adj_y < self.size[1] and random_room.connections[
                    adjacency_index] is None and
                        not self.room_exists_at(new_position)):
                    new_room = Room(new_position)
                    new_room.connections[reverse_index] = random_room
                    random_room.connections[adjacency_index] = new_room
                    self.rooms.append(new_room)
                    break




class xTile:
    def __init__(self, board, column, row, is_wall = False, is_door = False, is_discovered = False, is_bomb = False, is_flagged = False):
        self.board = board
        self.column = column
        self.row = row
        self.is_wall = is_wall
        self.is_door = is_door
        self.is_discovered = is_discovered
        self.is_bomb = is_bomb
        self.is_flagged = is_flagged
        self.adjacent_bombs = 0
        self.display = self.update_state()

    def __repr__(self):
        return self.display.format(self.adjacent_bombs)


    def check_door_direction(self):
        mid_x = len(self.board.tiles[0]) // 2
        mid_y = len(self.board.tiles) // 2

        if self.row == 0 and self.column == mid_x:
            return 0  # North
        elif self.column == len(self.board.tiles[0]) - 1 and self.row == mid_y:
            return 1  # East
        elif self.row == len(self.board.tiles) - 1 and self.column == mid_x:
            return 2  # South
        elif self.column == 0 and self.row == mid_y:
            return 3  # West

        return -1

    def update_state(self):
        colors = Colors()
        if self.is_door:
            if not self.board.is_revealed:
                return colors.BLANK + "[#]"
            else:
                directions = ['[<]', '[v]' ,'[>]', '[^]']
                direction_index = self.check_door_direction()
                if direction_index == -1:
                    return colors.SEVEN + "[D]"  # fallback
                return colors.SEVEN + directions[direction_index]
        if self.is_wall:
            return colors.BLANK + "[#]"
        if self.is_flagged:
            return colors.BOMB + "[F]" if self.board.is_revealed and self.is_bomb else colors.FLAG + "[F]"
        if not self.is_discovered:
            return colors.BLANK + "[ ]"
        if self.is_bomb:
            return colors.BOMB + "[B]"
        if self.adjacent_bombs <= 0:
            return colors.ZERO + "[·]"
        number_color = colors.ONE if self.adjacent_bombs == 1 else colors.TWO if self.adjacent_bombs == 2 else colors.THREE if self.adjacent_bombs == 3 else colors.FOUR if self.adjacent_bombs == 4 else colors.FIVE if self.adjacent_bombs == 5 else colors.SIX if self.adjacent_bombs == 6 else colors.SEVEN if self.adjacent_bombs == 7 else colors.EIGHT
        return number_color + "[{}]"

    def discover(self, is_recursive=True):
        self.display = self.update_state()

        if self.is_flagged:
            return True

        self.is_discovered = True
        self.display = self.update_state()

        if self.is_bomb:
            return False

        if is_recursive and self.adjacent_bombs == 0:
            adjacency = [(1, 0), (0, 1), (-1, 0), (0, -1)]
            for dx, dy in adjacency:
                adj_x = self.column + dx
                adj_y = self.row + dy
                if 0 <= adj_x < len(self.board.tiles[0]) and 0 <= adj_y < len(self.board.tiles):
                    adj_tile = self.board.tiles[adj_y][adj_x]
                    if not adj_tile.is_discovered and not adj_tile.is_bomb:
                        result = adj_tile.discover()
                        if not result:
                            return False

        return True

    def flag(self):
        self.is_flagged = not self.is_flagged
        self.display = self.update_state()


class xBoard:
    def __init__(self, room, width, height, border = 1, max_bombs = 10):
        self.room = room
        self.width = width
        self.height = height
        self.border = border
        self.max_bombs = max_bombs
        self.bombs = 0
        self.tiles = []

        self.is_revealed = False

    def __repr__(self):
        colors = Colors()
        board_display = "      "
        for i in range(len(self.tiles) - (2 * self.border)):
            board_display += colors.BLANK + " {} ".format(chr(65 + i)) # Add a letter for each column in the board
        board_display += "\n"
        for x in range(len(self.tiles)):
            board_display += colors.BLANK + "{: <2s} ".format(str(x - 1)) if not x == 0 and not x == len(self.tiles) - 1 else colors.BLANK + "   "# Add a number for each row in the board
            for y in range(len(self.tiles[x])):
                board_display += "{}".format(self.tiles[x][y]) # Add each tile to the board
            board_display += "\n"

        return board_display

    def populate_board(self):
        total_width = self.width + (2 * self.border)
        total_height = self.height + (2 * self.border)
        mid_x = total_width // 2
        mid_y = total_height // 2

        playable_positions = [
            (x, y)
            for x in range(self.border, total_width - self.border)
            for y in range(self.border, total_height - self.border)
        ]

        bomb_positions = random.sample(playable_positions, self.max_bombs)

        for x in range(total_width):
            column = []
            for y in range(total_height):
                is_bomb = (x, y) in bomb_positions
                tile = Tile(self, x, y, is_bomb=is_bomb)

                if self.border <= x < total_width - self.border and self.border <= y < total_height - self.border:
                    tile.is_wall = False
                else:
                    tile.is_wall = True

                if self.room is not None:
                    if (x == mid_x and y == 0 and self.room.connections[0]) or \
                       (x == 0 and y == mid_y and self.room.connections[1]) or \
                       (x == mid_x and y == total_height - 1 and self.room.connections[2]) or \
                       (x == total_width - 1 and y == mid_y and self.room.connections[3]):
                        tile.is_door = True
                        tile.is_wall = False

                column.append(tile)
            self.tiles.append(column)

    def count_bombs(self):
        for col in self.tiles:
            for tile in col:
                bombs = 0
                adjacency = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
                for dx, dy in adjacency:
                    adj_x = tile.column + dx
                    adj_y = tile.row + dy
                    if 0 + self.border <= adj_x < len(self.tiles[0]) - self.border and 0 + self.border <= adj_y < len(self.tiles) - self.border:
                        if self.tiles[adj_x][adj_y].is_bomb:
                            bombs += 1
                tile.adjacent_bombs = bombs
                tile.display = tile.update_state()

    def discover_all(self):
        triggered_bomb = False
        for col in self.tiles:
            for tile in col:
                result = tile.discover(False)
                if not result:
                    triggered_bomb = True
        return not triggered_bomb

    def is_cleared(self):
        for col in self.tiles:
            for tile in col:
                if tile.is_bomb and not tile.is_discovered:
                    return False
        return True


class xRoom:
    def __init__(self, position, is_start = False, is_end = False):
        self.position = position
        self.is_start = is_start
        self.is_end = is_end
        self.connections = [] # [N, W, S, E]
        self.initialize_directions()
        self.board = None

    def initialize_directions(self):
        self.connections = [None] * 4

    def __repr__(self):
        return "Room {}\n{}".format(self.position, self.board)


class xDungeon:
    def __init__(self, width, height, max_rooms):
        self.level = 0
        self.width = width
        self.height = height
        self.max_rooms = max_rooms
        self.rooms = []

    def __repr__(self):
        colors = Colors()
        dungeon_map = "  "
        for i in range(self.width):
            dungeon_map += colors.BLANK + "{} ".format(chr(65 + i)) # Add a letter for each column in the board
        dungeon_map += "\n"
        for i in range(self.width):
            dungeon_map += colors.BLANK + "{} ".format(i)  # Add a number for each row in the board
            for j in range(self.height):
                if self.room_exists_at((j, i)):
                    dungeon_map += ""
                    room = self.get_room_at((j, i))
                    if room.is_start:
                        dungeon_map += colors.ONE + "S "
                    elif room.is_end:
                        dungeon_map += colors.THREE + "E "
                    else:
                        dungeon_map += colors.SEVEN + "O "
                else:
                    dungeon_map += colors.ZERO + "X "
            dungeon_map += "\n"
        return dungeon_map

    def room_exists_at(self, position):
        return any(room.position == position for room in self.rooms)

    def get_room_at(self, position):
        for room in self.rooms:
            if room.position == position:
                return room
        return None

    def generate_dungeon(self):
        print("Generating dungeon layout...")
        starting_position = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
        starting_room = Room(starting_position, is_start=True)
        self.rooms.append(starting_room)

        while len(self.rooms) < self.max_rooms:
            random_room = random.choice(self.rooms)
            adjacency = [(0, -1), (-1, 0), (0, 1), (1, 0)] # N, W, S, E

            while adjacency:
                random_adj = random.choice(adjacency)

                adjacency_index = adjacency.index(random_adj)
                reverse_index = (adjacency_index + 2) % 4

                adjacency.pop(adjacency_index)

                adj_x = random_room.position[0] + random_adj[0]
                adj_y = random_room.position[1] + random_adj[1]
                new_position = (adj_x, adj_y)

                if (0 <= adj_x < self.width and 0 <= adj_y < self.height and random_room.connections[adjacency_index] is None and
                        not self.room_exists_at(new_position)):
                    new_room = Room(new_position)
                    new_room.connections[reverse_index] = random_room
                    random_room.connections[adjacency_index] = new_room
                    self.rooms.append(new_room)
                    break

        self.rooms[-1].is_end = True # Mark the last room as the ending


class Game:
    def __init__(self):
        wrapper(self.main)

    def __repr__(self):
        pass

    def main(self, stdscr):
        curses.curs_set(0)
        stdscr.clear()

        dungeon = Dungeon((5, 5))
        dungeon.max_rooms = 10

        stdscr.refresh()
        stdscr.getch()


game = Game()

#
#
# dungeon = Dungeon(5, 5, 10)
# dungeon.generate_dungeon()
# print(dungeon)
#
# current_room = dungeon.rooms[0]
# board = current_room.board = Board(current_room,5, 5, max_bombs=5)
# board.populate_board()
# board.count_bombs()
#
# is_playing = True
# colors = Colors()
#
# while is_playing:
#     board = current_room.board
#     print(colors.BLANK + "Room: {}, Bombs left: {}".format(current_room.position, board.max_bombs - board.bombs))
#     print(board)
#     print(colors.BLANK + "\nPlease select your next action:")
#     print("\n - 'DXY' to discover a tile (where XY is column and row)")
#     print("\n - 'FXY' to flag a tile (where XY is column and row)")
#     player_input = input()
#     tile_x = (ord(player_input[1:2]) - 65) + board.border
#     tile_y = (int(player_input[2:])) + board.border
#     if 0 <= tile_x < len(board.tiles[0]) and 0 <= tile_y < len(board.tiles):
#         if player_input.startswith("D"):
#             is_safe = board.tiles[tile_y][tile_x].discover()
#             print(is_safe)
#             if not is_safe:
#                 board.is_revealed = True
#                 board.discover_all()
#                 print(colors.BLANK + "Room: {}, Bombs left: {}".format(current_room.position, board.max_bombs - board.bombs))
#                 print(board)
#                 print(colors.LOSE + "\nBOOM!")
#                 print(colors.LOSE + "\nYou triggered a bomb and died!")
#                 is_playing = False
#         elif player_input.startswith("F"):
#             if not board.tiles[tile_y][tile_x].is_discovered:
#                 board.tiles[tile_y][tile_x].flag()
#                 board.bombs += 1 if board.tiles[tile_y][tile_x].is_flagged else -1
#         else:
#             print(colors.LOSE + "Error: Invalid Input")
#
#     if board.max_bombs - board.bombs <= 0:
#         board.is_revealed = True
#         result = board.discover_all()
#         print(colors.BLANK + "Room: {}, Bombs left: {}".format(current_room.position, board.max_bombs - board.bombs))
#         print(board)
#         if not result:
#             print(colors.LOSE + "\nBOOM!")
#             print(colors.LOSE + "\nYou've failed to flag every bomb and died!")
#             is_playing = False
#         print(colors.WIN + "\nYou correctly flagged every bomb and lived!")
#         print(colors.BLANK + "\nPlease select your next action:")
#         print("\n - DIR to traverse to room (where DIR is: '^', '>', 'v', '<')")
#         player_input = input()
#         directions = ['^', '>', 'v', '<']
#         if player_input in directions:
#             door_index = directions.index(player_input)
#             new_room = current_room.connections[door_index]
#             current_room = new_room
#             board = current_room.board = Board(current_room, 5, 5, max_bombs=5)
#             board.populate_board()
#             board.count_bombs()
