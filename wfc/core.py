import math
import random

class TileSetError(Exception):
    pass

class Pos():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Pos(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Tile():
    def __init__(self, id,):
        self.id = id
        self.sockets = [[], [], [], []]

    def up(self): return self.sockets[0]
    def right(self): return self.sockets[1]
    def down(self): return self.sockets[2]
    def left(self): return self.sockets[3]

    def add_up(self, x): self.sockets[0].append(x)
    def add_right(self, x): self.sockets[1].append(x)
    def add_down(self, x): self.sockets[2].append(x)
    def add_left(self, x): self.sockets[3].append(x)

class Cell():
    def __init__(self):
        self.id = 0
        self.visited = False

class Map():
    offsets = [Pos(0, -1), Pos(1, 0), Pos(0, 1), Pos(-1, 0)]
    # sockets = [up, right, down, left]
    mirror = [2, 3, 0, 1]

    def __init__(self, tileset, width, height):
        self.tileset = tileset
        self.num_tiles = len(tileset)
        self.map = [[Cell() for i in range(width)] for j in range(height)]
        self.width = width
        self.height = height

    def check_bounds(self, pos):
        if pos.x >= self.width or pos.x < 0 or pos.y >= self.height or pos.y < 0: return False
        return True
    def get_tile(self, pos):
        return self.map[pos.y][pos.x].id if self.check_bounds(pos) else 0
    def set_tile(self, pos, tile): self.map[pos.y][pos.x].id = tile
    def get_visited(self, pos):
        return self.map[pos.y][pos.x].visited if self.check_bounds(pos) else True
    def set_visited(self, pos, state): self.map[pos.y][pos.x].visited = state

    def generate(self, fast=False, pass_callback=None, tile_identifiers=None):
        min_possibilities_pos = Pos(random.randint(0, self.width - 1), random.randint(0, self.height - 1))
        self.propagation_stack = []
        while True:
            self.propagate(min_possibilities_pos, True)
            
            if pass_callback: pass_callback(self, tile_identifiers)

            while len(self.propagation_stack) > 0:
                self.propagate(self.propagation_stack.pop(), fast)
                if fast:
                    if pass_callback: pass_callback(self, tile_identifiers)

            if fast: break

            min_possibilities = math.inf
            min_possibilities_pos = Pos(-1,-1)
            for y in range(self.height):
                for x in range(self.width):
                    pos = Pos(x, y)
                    self.set_visited(pos, False)
                    if self.get_tile(pos) != 0: continue
                    possibilities = len(self.get_possibilities(pos))
                    if possibilities < min_possibilities:
                        min_possibilities = possibilities
                        min_possibilities_pos = pos

            if min_possibilities == 0: raise TileSetError()
            if min_possibilities == math.inf: break

    def propagate(self, pos, hard):
        if self.get_tile(pos) != 0: return
        if not self.check_bounds(pos): return
        if self.get_visited(pos): return
        self.set_visited(pos, True)

        possibilities = self.get_possibilities(pos)
        if len(possibilities) == 0: raise TileSetError()
        if len(possibilities) == 1: self.set_tile(pos, possibilities[0])
        if hard: self.set_tile(pos, random.choice(possibilities))

        random.shuffle(Map.offsets)
        for e in Map.offsets:
            neighbour = pos + e
            self.propagation_stack.append(neighbour)

    def get_possibilities(self, pos):
        possibilities_mask = [True for i in self.tileset]
        for i, e in enumerate(Map.offsets):
            neighbour = self.get_tile(e + pos)
            if neighbour == 0: continue
            for j in range(self.num_tiles):
                if not possibilities_mask[j]: continue
                if not [s for s in self.tileset[j].sockets[Map.mirror[i]] if s in self.tileset[neighbour - 1].sockets[i]]: possibilities_mask[j] = False
        
        possibilities = []
        for i, e in enumerate(possibilities_mask): 
            if e: possibilities.append(i + 1)    
    
        return possibilities
    
def generate_tileset(tiles, example_set):
    socket_count = 0
    example_set_width = len(example_set[0])
    example_set_height = len(example_set)

    for y in range(example_set_height):
        for x in range(example_set_width):
            center_tile = example_set[y][x] - 1

            if x < example_set_width - 1:

                right_tile = example_set[y][x + 1] - 1

                if not [i for i in tiles[center_tile].right() if i in tiles[right_tile].left()]:
                    tiles[center_tile].add_right(socket_count)
                    tiles[right_tile].add_left(socket_count)
                    socket_count += 1

            if y < example_set_height - 1:

                down_tile = example_set[y + 1][x] - 1
    
                if not [i for i in tiles[center_tile].down() if i in tiles[down_tile].up()]:
                    tiles[center_tile].add_down(socket_count)
                    tiles[down_tile].add_up(socket_count)
                    socket_count += 1
    
    return tiles

def parse_input(input):
    example_set = input["input_tiles"]
    max_tile_id = max(map(max, example_set))
    tiles = [Tile(i) for i in range(max_tile_id)]
    tiles = generate_tileset(tiles, example_set)
    return tiles
