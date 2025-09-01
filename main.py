import curses
import random
import time

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
        self.position = position
        self.tile_type = tile_type

    def __repr__(self):
        return "[{}]".format(self.tile_type)

class SafeTile(Tile):
    def __init__(self, position, tile_type = " ", is_discovered = False, is_flagged = False):
        super().__init__(position, tile_type)
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
    def __init__(self, position, tile_type = " ", is_discovered = False, is_flagged = False):
        super().__init__(position, tile_type)
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
    def __init__(self, position, tile_type = " ", is_discovered = False):
        super().__init__(position, tile_type)
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

    def quantify_bombs(self):
        for col in self.tiles:
            for tile in col:
                neighbouring_tiles = [
                    self.tiles[x][y]
                    for x in range(max(0, tile.position[0] - 1), min(len(self.tiles), tile.position[0] + 2))
                    for y in range(max(0, tile.position[1] - 1), min(len(self.tiles[0]), tile.position[1] + 2))
                    if (x, y) != self.tiles[x][y].position
                ]
                for n_tile in neighbouring_tiles:
                    if isinstance(n_tile, BombTile) and self.is_inside_playable_rect(n_tile.position):
                        tile.adjacent_bombs += 1
                        tile.tile_type = tile.adjacent_bombs

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


class Character:
    def __init__(self, position, char_type = "@"):
        self.position = position
        self.char_type = char_type


class Game:
    def __init__(self):
        self.is_playing = True
        self.dungeon = None
        self.player = Character((0, 0))
        self.window = None
        wrapper(self.main)

    def __repr__(self):
        pass
    
    def render(self):
        self.window[0].clear()
        self.window[0].addstr(1, 1, "Room: {}, Bombs: {}")
        self.window[0].refresh()

        self.window[1].clear()
        pa_height, pa_width = self.window[1].getmaxyx()
        self.player.position = (pa_width // 2, pa_height // 2)
        for room in self.dungeon.rooms:
            board = room.board = Board(room.position, (10, 10))
            board.max_bombs = 5
            board.populate()
            board.quantify_bombs()

            # This is to account for room's sizes and a border around them
            global_x = room.position[0] * board.size[
                0] * 4  # [X] each tile is 3 characters long plus a space between boards
            global_y = (room.position[1] * board.size[
                1] * 3) // 2  # each tile is 1 character tall plus a space between boards

            camera_offset_x, camera_offset_y = self.get_camera_offset(self.player.position, (pa_width, pa_height))

            global_x -= camera_offset_x
            global_y -= camera_offset_y

            # TODO: Check if the tile is inside the play area and if it is, render it.
            if self.is_inside_viewport(global_x, global_y, pa_width, pa_height):
                self.window[1].addstr(global_y, global_x + 2,
                                      "Room: {}, Bombs: {}".format(room.position, room.board.get_remaining_bombs()))
            for i in range(len(room.board.tiles)):
                col_screen_y = global_y + 1
                col_screen_x = global_x + 5 + (i * 3)
                if self.is_inside_viewport(col_screen_x, col_screen_y, pa_width, pa_height):
                    self.window[1].addstr(col_screen_y, col_screen_x,
                                          "{}".format(chr(65 + i)))  # Column helper indicator (A B C D E...)

                row_screen_y = global_y + 2 + i
                row_screen_x = global_x
                if self.is_inside_viewport(row_screen_x, row_screen_y, pa_width, pa_height):
                    self.window[1].addstr(row_screen_y, row_screen_x,
                                          "  {}".format(i))  # Row helper indicator (0 1 2 3 4...)

            for i in range(len(room.board.tiles)):
                for j in range(len(room.board.tiles[0])):
                    screen_y = global_y + 2 + i
                    screen_x = global_x + 4 + (j * 3)
                    if self.is_inside_viewport(screen_x, screen_y, pa_width, pa_height):
                        self.window[1].addstr(screen_y, screen_x, "{}".format(room.board.tiles[i][j]))

        self.window[1].addstr(pa_height // 2, pa_width // 2,
                              "{}".format(self.player.char_type))  # Render player in the center of the play area
        self.window[1].refresh()

        self.window[2].clear()
        for i in range(self.dungeon.size[0]):
            self.window[2].addstr(0, 5 + (i * 3), "{}".format(chr(65 + i)))
            self.window[2].addstr(1 + i, 0, "  {}".format(i))

        for i in range(self.dungeon.size[0]):
            for j in range(self.dungeon.size[1]):
                position = (i, j)
                if self.dungeon.room_exists_at(position):
                    if self.dungeon.get_room_at(position) == self.dungeon.rooms[0]:
                        self.window[2].addstr(1 + i, 5 + (j * 3), "S")
                    elif self.dungeon.is_last_room(self.dungeon.get_room_at(position)):
                        self.window[2].addstr(1 + i, 5 + (j * 3), "E")
                    else:
                        self.window[2].addstr(1 + i, 5 + (j * 3), "O")
                else:
                    self.window[2].addstr(1 + i, 5 + (j * 3), "·")

        self.window[2].refresh()

        self.window[3].clear()
        self.window[3].addstr(0, 0, "a. Discover tile")
        self.window[3].addstr(1, 0, "b. Flag tile")
        self.window[3].addstr(2, 0, "c. Go to room")
        self.window[3].refresh()
    
    def handle_input(self, event):
        pass
    
    def loop(self, delta):
        pass

    def main(self, stdscr):
        last_time = time.time()

        curses.curs_set(0)
        stdscr.clear()

        height, width = stdscr.getmaxyx()

        self.window = self.init_window(height, width)
        self.dungeon = self.init_dungeon()[0]

        while self.is_playing:
            self.render()

            event = stdscr.getch()
            if event == ord('q'):
                break
            self.handle_input(event)

            current_time = time.time()
            delta = last_time - current_time
            self.loop(delta)
            last_time = current_time

            stdscr.refresh()

    ### Helper functions ###

    def init_dungeon(self):
        dungeon = Dungeon((5, 5))
        dungeon.max_rooms = 10
        dungeon.generate_floor()

        first_room = dungeon.rooms[0]
        board = first_room.board = Board(first_room.position, (10, 10))
        board.max_bombs = 5
        board.populate()
        board.quantify_bombs()

        return dungeon, first_room

    def init_window(self, height, width):
        status_bar = curses.newwin(int(height * 0.05), width, 0, 0)
        play_area = curses.newwin(int(height * 0.6), int(width * 0.6), int(height * 0.1), 0)
        dungeon_map = curses.newwin(int(height * 0.35), int(width * 0.35), int(height * 0.1), int(width * 0.65))
        action_menu = curses.newwin(int(height * 0.25), width, int(height * 0.65), 0)

        return status_bar, play_area, dungeon_map, action_menu

    def get_camera_offset(self, player_pos, viewport_size):
        offset_x = player_pos[0] - viewport_size[0] // 2
        offset_y = player_pos[1] - viewport_size[1] // 2
        return offset_x, offset_y

    def is_inside_viewport(self, x, y, viewport_width, viewport_height):
        return 0 <= x < viewport_width and 0 <= y < viewport_height

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
