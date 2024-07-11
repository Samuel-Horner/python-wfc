"""
wfc.core
Contains all the neccesary framework to setup and run the wfc algorithm.

Classes:

    - TileSetError(Exception)
    - Pos
    - Tile
    - Cell
    - Map

Functions:

    - generate_tileset
    - parse_input
"""

import math
import random

class TileSetError(Exception):
    """ Class to define a TileSetError, i.e. a tile with 0 possibilities
    """
    pass

class Pos():
    """ A Class containing an x and y position

    :param x: X component, defaults to 0
    :type x: int, optional
    :param y: Y component, defaults to 0
    :type y: int, optional
    """

    def __init__(self, x: int = 0, y: int = 0) -> None:
        """ Constructor method
        """
        self.x = x
        self.y = y

    def __add__(self, other: "Pos") -> "Pos":
        """ Adds two Pos objects together element wise

        :param other: The other pos object
        :type other: Pos
        :return: The result of the addition
        :rtype: Pos
        """
        return Pos(self.x + other.x, self.y + other.y)

    def __eq__(self, other: object) -> bool:
        """ Determines element wise equality

        :param other: The other object
        :type other: object
        :return: Boolean describing whether or the objects are equal element wise
        :rtype: bool
        """        
        if not isinstance(other, Pos): return NotImplemented
        return self.x == other.x and self.y == other.y

class Tile():
    """ Class containing tile id and sockets

    :param id: Integer tile id (!= 0)
    :type id: int
    """
    def __init__(self, id: int) -> None:
        """ Constructor method
        """
        self.id = id
        self.sockets = [[], [], [], []]

    def up(self) -> list[int]: return self.sockets[0]
    def right(self) -> list[int]: return self.sockets[1]
    def down(self) -> list[int]: return self.sockets[2]
    def left(self) -> list[int]: return self.sockets[3]

    def add_up(self, x) -> None: self.sockets[0].append(x)
    def add_right(self, x) -> None: self.sockets[1].append(x)
    def add_down(self, x) -> None: self.sockets[2].append(x)
    def add_left(self, x) -> None: self.sockets[3].append(x)

class Cell():
    """ Class containing an id and a boolean visited flag
    """    
    def __init__(self) -> None:
        """ Constructor method
        """        
        self.id = 0
        self.visited = False

class Map():
    """ Class containing the actual grid with generation and propagation methods

    :param tileset: The tile set to be used
    :type tileset: list[Tile]
    :param width: The map width
    :type width: int
    :param height: The map height
    :type height: int

    :raises TileSetError: Invalid tile set (0 possibilities)
    :raises TileSetError: Invalid tile set (0 possibilities)
    """
    offsets = [Pos(0, -1), Pos(1, 0), Pos(0, 1), Pos(-1, 0)]
    """ A list of offsets used when finding neighbours """
    mirror = [2, 3, 0, 1]
    """ Mirror indexes used to query sockets """

    def __init__(self, tileset: list[Tile], width: int, height: int) -> None:
        """ Constructor method
        """        
        self.tileset = tileset
        self.num_tiles = len(tileset)
        self.map = [[Cell() for i in range(width)] for j in range(height)]
        self.width = width
        self.height = height

    def check_bounds(self, pos: Pos) -> bool:
        """ Checks if a given position is in bounds

        :param pos: Possition to check
        :type pos: Pos
        :return: Whether or not the position is in bounds
        :rtype: bool
        """        
        if pos.x >= self.width or pos.x < 0 or pos.y >= self.height or pos.y < 0: return False
        return True
    def get_tile(self, pos: Pos) -> int:
        """ Gets cell ID at a given position, if out of bounds returns 0

        :param pos: The given position
        :type pos: Pos
        :return: The cell ID
        :rtype: int
        """        
        return self.map[pos.y][pos.x].id if self.check_bounds(pos) else 0
    def set_tile(self, pos: Pos, tile: int) -> None:
        """ Sets the ID of a cell

        :param pos: The position of the cell
        :type pos: Pos
        :param tile: The id to set
        :type tile: int
        """
        self.map[pos.y][pos.x].id = tile
    def get_visited(self, pos: Pos) -> bool:
        """ Returns the visited flag of a cell, if out of bounds returns True

        :param pos: The cell's position
        :type pos: Pos
        :return: The visited flag of the cell
        :rtype: bool
        """        
        return self.map[pos.y][pos.x].visited if self.check_bounds(pos) else True
    def set_visited(self, pos: Pos, state: bool) -> None:
        """ Sets the visited flag of a cell

        :param pos: The cell's position
        :type pos: Pos
        :param state: The state to set the flag to
        :type state: bool
        """         
        self.map[pos.y][pos.x].visited = state

    def generate(self, fast: bool = False, pass_callback: callable = None, tile_identifiers: list[str] = None) -> None:
        """ Performs the wave function collapse on the map

        :param fast: Whether or not to use the fast algorithm, defaults to False
        :type fast: bool, optional
        :param pass_callback: The callback called after every pass, with :param tile_identifiers: and self passed in, defaults to None
        :type pass_callback: callable, optional
        :param tile_identifiers: The list of tile strings passed to :param pass_callback:, defaults to None
        :type tile_identifiers: list[str], optional
        :raises TileSetError: Invalid tile set reached, 0 possibilities
        """        
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

    def propagate(self, pos: Pos, hard: bool) -> None:
        """ Propagates a change

        :param pos: The posistion to propagate
        :type pos: Pos
        :param hard: Whether or not to forcefully select a random possible tile
        :type hard: bool
        :raises TileSetError: Invalid tile set, 0 possibilities reached
        """        
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

    def get_possibilities(self, pos: Pos) -> list[int]:
        """ Returns a list of possible tile IDs at pos

        :param pos: The position to check
        :type pos: Pos
        :return: A list of possible tile IDs
        :rtype: list[int]
        """        
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
    
def generate_tileset(tiles: list[Tile], example_set: list[list[int]]) -> list[Tile]:
    """ Calculates sockets based on the example set and applies them to the given tile set

    :param tiles: The given set of tiles
    :type tiles: list[Tile]
    :param example_set: The example tile set
    :type example_set: list[list[int]]
    :return: The modified set of tiles with sockets calculated
    :rtype: list[Tile]
    """    
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

def parse_input(input: dict) -> list[Tile]:
    """ Creates a list of tiles from a JSON input containing an example set

    :param input: The JSON input, containing "input_tiles" (the example set)
    :type input: dict
    :return: A list of tiles with sockets
    :rtype: list[Tile]
    """    
    example_set = input["input_tiles"]
    max_tile_id = max(map(max, example_set))
    tiles = [Tile(i) for i in range(max_tile_id)]
    tiles = generate_tileset(tiles, example_set)
    return tiles
