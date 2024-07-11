import argparse
import json
from time import sleep

from wfc import core as wfc

def tileset_error() -> None:
    print("Invalid tileset - locked tile reached")
    exit()

def input_file_error() -> None:
    print("Invalid input file")
    exit()

def parse_file(input_file: str, width: int = None, height: int = None) -> tuple[list[wfc.Tile], list[str], int, int] | Exception:
    """ Parses the input file

    :param input_file: The file to parse
    :type input_file: str
    :param width: The output width override, defaults to None
    :type width: int, optional
    :param height: The ouput height override, defaults to None
    :type height: int, optional
    :return: A tuple containing a list of wfc.Tile objects, a list of the strings they represent, and the desired width & height of the output
    :rtype: tuple[list[wfc.Tile], list[str], int, int]
    """
    try: file = open(input_file, "r") # Atempt to open the file
    except:
        print(f"Could not open {input_file}")
        return Exception
    input = json.load(file)
    file.close()
    # returns the output of wfc.parse_input and the inputted tile strings, along with the inputted width and height if they are not overwritten.
    return wfc.parse_input(input), input["tiles"], input["width"] if not width else width, input["height"] if not height else height

def print_map(map: wfc.Map, tile_strings: list[str]) -> None:
    """ Prints the state of the map

    :param map: The map object
    :type map: wfc.Map
    :param tile_strings: The list of strings each tile represents
    :type tile_strings: list[str]
    """
    for i in range(map.height):
        for j in range(map.width):
            # Iterates through the map,
            tile = map.map[i][j].id
            if (tile == 0): print("-", end=" ") # If empty tile (i.e. id 0)
            else: print(tile_strings[tile - 1], end=" ") # If non empty tile
        print()

def animate_map(map: wfc.Map, tile_strings: list[str]) -> None:
    """ Map animation callback

    :param map: The map object
    :type map: wfc.Map
    :param tile_strings: The list of strings each tile represents
    :type tile_strings: list[str]
    """    
    # Calls print_map after clearing the terminal and then sleeps for 5 ms
    print("\x1b[H\x1b[0J")
    print_map(map, tile_strings)
    sleep(0.005)
    
def main(file: str, animate: bool = False, width: int = None, height: int = None, fast: bool = False) -> None:
    """ The CLI entrypoint

    :param file: The input file
    :type file: str
    :param animate: Boolean describing wether or not to animate the generation, defaults to False
    :type animate: bool, optional
    :param width: The output width override, defaults to None
    :type width: int, optional
    :param height: The output height override, defaults to None
    :type height: int, optional
    :param fast: Boolean describing wether or not to use the faster, less stable algorithm, defaults to False
    :type fast: bool, optional
    """
    try: tiles, tile_strings, width, height = parse_file(file, width, height) # Generate tile set
    except: input_file_error()
    map = wfc.Map(tiles, width, height) # Initialise map
    # for i in map.tileset: print(i.sockets)
    try: # Try to generate map
        if animate: map.generate(fast, animate_map, tile_strings) # If animation enabled pass frame callback
        else: map.generate(fast) # If animation disabled
    except wfc.TileSetError: # Locked tile reached (0 possibilities)
        print_map(map, tile_strings)
        if fast: # Fast mode will almost always reach a locked tile if no wildcard tile is present
            print("Hint: try disabling fast mode")
        tileset_error()
    if not animate: print_map(map, tile_strings) # Print map if not animated

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="The input json file to read from.")
    parser.add_argument("-a", "--animate", help="Whether or not to animate the generation process.", action="store_true")
    parser.add_argument("-x", "--width", type=int, help="overrides the width set in the input file.")
    parser.add_argument("-y", "--height", type=int, help="overrides the height set in the input file.")
    parser.add_argument("-f", "--fast", help="Use a faster, less robust algorithm. REQUIRES wildcard tiles (see example tileset 3).", action="store_true")

    args = parser.parse_args()

    filename = args.file
    main(filename, True if args.animate else False, args.width if args.width else None, args.height if args.height else None, True if args.fast else False)
