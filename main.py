import random as rn # For random starting pos
import time

class Pos:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def get_neighbours(self):
        return [Pos(self.x, self.y + 1), Pos(self.x + 1, self.y), Pos(self.x, self.y - 1), Pos(self.x - 1, self.y)]
    
    def __eq__(self, a):
        return self.x == a.x and self.y == a.y

class Rule:
    def __init__(self, tileID: int, dissalowedTiles: list):
        self.tile_id = tileID
        self.dissalowed_tiles = dissalowedTiles

    def check(self, id: int):
        return id not in self.dissalowed_tiles

class RuleSet:
    # 0 is up, 1 is right, 2 is down, 3 is left
    def __init__(self, rules: list): # Args formatted in [Rule UP, Rule RIGHT, ...]
        self.rules = rules

    def check(self, tiles: list):
        for index, rule in enumerate(self.rules):
            if not rule.check(tiles[index]): return False
        return True

class Tile:
    def __init__(self, ruleSet: RuleSet, type: int, char: str):
        self.rule_set = ruleSet
        self.type = type
        self.char = char

    def clone(self):
        return Tile(self.rule_set, self.type, self.char)

class EmptyTile(Tile):
    def __init__(self):
        self.type = 0
        self.rule_set = None
        self.char = '.'


class Grid:
    def __init__(self, size: int, possibleTiles: list):
        self.size = size
        self.possible_tiles = possibleTiles
        self.grid = [[EmptyTile() for i in range(0,size)] for j in range(0, size)]
        self.propagation_stack = []

    def generate(self):
        starting_pos = Pos(rn.randint(0, self.size - 1), rn.randint(0, self.size - 1))
        self.grid[starting_pos.y][starting_pos.x] = rn.choice(self.possible_tiles).clone()
        self.propagation_stack += starting_pos.get_neighbours() # Concat the two lists
        while True:
            self.visited = []
            self.print()
            while len(self.propagation_stack) > 0:
                prop_pos = self.propagation_stack.pop()
                self.propagate(prop_pos)
            
            min_possible = 999
            min_pos_list = []
            for i, row in enumerate(self.grid):
                for j, tile in enumerate(row):
                    posibilites = len(self.get_possible_tiles(Pos(j,i)))
                    if posibilites == 0: continue
                    if posibilites == min_possible:
                        min_pos_list.append(Pos(j,i))
                        continue
                    if posibilites < min_possible:
                        min_possible = posibilites
                        min_pos_list = [Pos(j, i)]

            if len(min_pos_list) == 0:
                break
            
            next_pos = rn.choice(min_pos_list)
            self.grid[next_pos.y][next_pos.x] = rn.choice(self.get_possible_tiles(next_pos)).clone()
            self.propagation_stack += next_pos.get_neighbours()

        print("Done Generating!")

    def propagate(self, prop_pos: Pos):
        self.visited.append(prop_pos)
        if (prop_pos.x >= self.size) or (prop_pos.x < 0) or (prop_pos.y >= self.size) or (prop_pos.y < 0):
            return # OUT OF BOUNDS
        
        if (self.grid[prop_pos.y][prop_pos.x].type != 0): return # TILE ALREADY COLLAPSED

        possible_tiles = self.get_possible_tiles(prop_pos)

        if len(possible_tiles) == 0:
            raise Exception("Invalid rule set - impossible tile reached")
        
        if len(possible_tiles) == 1:
            self.grid[prop_pos.y][prop_pos.x] = possible_tiles[0].clone()

        neighbours_pos = prop_pos.get_neighbours()
        for i in neighbours_pos:
            if (i.x >= self.size) or (i.x < 0) or (i.y >= self.size) or (i.y < 0):
                continue # OUT OF BOUNDS
            if (self.grid[i.y][i.x].type != 0):
                continue # TILE ALREADY COLLAPSED
            if i in self.visited: 
                continue # ALREADY VISITED
            self.propagation_stack.append(i)
        
    def get_possible_tiles(self, pos):
        if self.grid[pos.y][pos.x].type != 0: return [] # TILE ALREADY COLLAPSED

        neighbours = []
        for i in pos.get_neighbours():
            if (i.x >= self.size) or (i.x < 0) or (i.y >= self.size) or (i.y < 0):
                neighbours.append(0)
            else: neighbours.append(self.grid[i.y][i.x].type)
        
        possible_tiles = []
        for i in self.possible_tiles:
            if i.rule_set.check(neighbours): possible_tiles.append(i)

        return possible_tiles

    def print(self):
        output = "\x1b[H\x1b[0J"
        for i in self.grid:
            for j in i:
                output += j.char + "\x1b[0m "
            output += "\n"
        print(output)
        # time.sleep(0.1)

if __name__ == "__main__":
    # Example Tiles
    tile_1 = Tile(RuleSet([Rule(1, [4,5]), Rule(1, [4,5]), Rule(1, [4,5]), Rule(1, [4,5])]), 1, "\x1b[1;34m~\x1b[22m")
    tile_2 = Tile(RuleSet([Rule(2, [1,2,4,5]), Rule(2, [1,2,4,5]), Rule(2, [1,2,4,5]), Rule(2, [1,2,4,5])]), 2, "\x1b[33m=")
    tile_3 = Tile(RuleSet([Rule(3, [2]), Rule(3, [2]), Rule(3, [2]), Rule(3, [2])]), 3, "\x1b[1;32m#\x1b[22m")
    tile_4 = Tile(RuleSet([Rule(4, [1,2]), Rule(4, [1,2]), Rule(4, [1,2]), Rule(4, [1,2])]), 4, "\x1b[32m|")
    tile_5 = Tile(RuleSet([Rule(5, [1,2,3,5]), Rule(5, [1,2,3,5]), Rule(5, [1,2,3,5]), Rule(5, [1,2,3,5])]), 5, "\x1b[37m^")

    # Generate the map
    grid = Grid(20, [tile_1, tile_2, tile_3, tile_4, tile_5])
    grid.generate()
    grid.print()

# NOTES:
#   This implementation uses a stack as python struggles with high depth recursion