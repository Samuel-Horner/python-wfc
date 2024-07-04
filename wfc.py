import math
import random
import json
import sys

class Pos():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Pos(self.x + other.x, self.y + other.y)

class Tile():
    def __init__(self, id, string, sockets):
        self.id = id
        self.string = string
        self.sockets = sockets

    def __str__(self): return self.string
    
    def up(self): return self.sockets[0]
    def right(self): return self.sockets[1]
    def down(self): return self.sockets[2]
    def left(self): return self.sockets[3]

    def add_up(self, x): self.sockets[0].append(x)
    def add_right(self, x): self.sockets[1].append(x)
    def add_down(self, x): self.sockets[2].append(x)
    def add_left(self, x): self.sockets[3].append(x)

class Map():
    offsets = [Pos(0, -1), Pos(1, 0), Pos(0, 1), Pos(-1, 0)]
    # sockets = [up, right, down, left]
    mirror = [2, 3, 0, 1]

    def __init__(self, tileset, width, height):
        self.tileset = tileset
        self.num_tiles = len(tileset)
        self.map = [[0 for i in range(width)] for j in range(height)]
        self.width = width
        self.height = height

    def print_tiles(self):
        for i in self.tileset: print(i, i.up(), i.right(), i.down(), i.left())

    def check_bounds(self, pos):
        if pos.x >= self.width or pos.x < 0 or pos.y >= self.height or pos.y < 0: return False
        return True
    def get_tile(self, pos):
        return self.map[pos.y][pos.x] if self.check_bounds(pos) else 0
    def set_tile(self, pos, tile): self.map[pos.y][pos.x] = tile

    def generate(self):
        min_possibilities_pos = Pos(random.randint(0, self.width - 1), random.randint(0, self.height - 1))
        self.propagation_stack = []
        while True:
            self.propagate(min_possibilities_pos, True)

            self.propagation_stack = []
            while len(self.propagation_stack) > 0:
                self.propagate(self.propagation_stack.pop(), False)

            min_possibilities = math.inf
            min_possibilities_pos = Pos(-1,-1)
            for y in range(self.height):
                for x in range(self.width):
                    pos = Pos(x, y)
                    if self.get_tile(pos) != 0: continue
                    possibilities = len(self.get_possibilities(pos))
                    if possibilities < min_possibilities:
                        min_possibilities = possibilities
                        min_possibilities_pos = pos

            if min_possibilities == 0: tileset_error()
            if min_possibilities == math.inf: break

    def propagate(self, pos, hard):
        if self.get_tile(pos) != 0: return
        if not self.check_bounds(pos): return

        possibilities = self.get_possibilities(pos)
        if len(possibilities) == 0: tileset_error()
        if len(possibilities) == 1: self.set_tile(pos, possibilities[0])
        if hard: self.set_tile(pos, random.choice(possibilities))

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

    def print_map(self):
        for i in range(self.height):
            for j in range(self.width):
                tile = self.map[i][j]
                if (tile == 0): print("-", end=" ")
                else: print(self.tileset[tile - 1], end=" ")
            print()

def tileset_error():
    print("Invalid tileset - locked tile reached")
    exit()

def input_file_error():
    print("Invalid input file")
    exit()

def parse_input(input):
    tiles = input["tiles"]
    input_tiles = input["input_tiles"]
    parsed_tiles = []
    for i in range(len(tiles)): parsed_tiles.append(Tile(i, "\x1b[" + tiles[i] + "\x1b[0m" if input["format"] else tiles[i], [[], [], [], []]))
    
    socket_count = 0
    input_tiles_width = len(input_tiles[0]) - 1
    input_tiles_height = len(input_tiles) - 1
    for y in range(input_tiles_height):
        for x in range(input_tiles_width):
            center_tile = input_tiles[y][x] - 1
            right_tile = input_tiles[y][x + 1] - 1
            down_tile = input_tiles[y + 1][x] - 1
            
            if not [i for i in parsed_tiles[center_tile].right() if i in parsed_tiles[right_tile].left()]:
                parsed_tiles[center_tile].add_right(socket_count)
                parsed_tiles[right_tile].add_left(socket_count)
                socket_count += 1

            if not [i for i in parsed_tiles[center_tile].down() if i in parsed_tiles[down_tile].up()]:
                parsed_tiles[center_tile].add_down(socket_count)
                parsed_tiles[down_tile].add_up(socket_count)
                socket_count += 1


    return parsed_tiles

def parse_file(input_file):
    try: file = open(input_file, "r")
    except: input_file_error()
    input = json.load(file)

    return parse_input(input), input["width"], input["height"]
    
def main(file):
    tiles, width, height = parse_file(file)
    map = Map(tiles, width, height)
    map.generate()
    map.print_map()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Invalid arguments, please pass file name.")
        print("Usage: python wfc.py filename format")
        exit()
    elif len(sys.argv) == 2:
        filename = sys.argv[1]
        main(filename)
    