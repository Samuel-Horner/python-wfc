import argparse
import json
from time import sleep

# Hack to inport wfc module here
# ASSUMES that you are running this file from its parent directory, i.e python examples/file.py
import os
import sys
if os.getcwd() not in sys.path: sys.path.append(os.getcwd())

try:
    from wfc import core as wfc
except:
    print("Could not find wfc module. Try running this example from the projects root directory (i.e python-wfc)")
    exit()

def tileset_error():
    print("Invalid tileset - locked tile reached")
    exit()

def input_file_error():
    print("Could not open input file")
    exit()

def parse_file(input_file, width=None, height=None):
    try: file = open(input_file, "r")
    except: input_file_error()
    input = json.load(file)
    return wfc.parse_input(input), input["tiles"], input["width"] if not width else width, input["height"] if not height else height

def print_map(map, tile_strings):
    for i in range(map.height):
        for j in range(map.width):
            tile = map.map[i][j].id
            if (tile == 0): print("-", end=" ")
            else: print(tile_strings[tile - 1], end=" ")
        print()

def animate_map(map, tile_strings):
    print("\x1b[H\x1b[0J")
    for i in range(map.height):
        for j in range(map.width):
            tile = map.map[i][j].id
            if (tile == 0): print("-", end=" ")
            else: print(tile_strings[tile - 1], end=" ")
        print()
    sleep(0.005)
    
def main(file, animate = False, width=None, height=None):
    tiles, tile_strings, width, height = parse_file(file, width, height)
    map = wfc.Map(tiles, width, height)
    try: 
        if animate: map.generate(animate_map, tile_strings)
        else: map.generate()
    except wfc.TileSetError:
        print_map(map, tile_strings) 
        tileset_error()
    if not animate: print_map(map, tile_strings)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="The input json file to read from.")
    parser.add_argument("-a", "--animate", help="Whether or not to animate the generation process.", action="store_true")
    parser.add_argument("-x", "--width", type=int, help="Overides the width set in the input file.")
    parser.add_argument("-y", "--height", type=int, help="Overides the height set in the input file.")

    args = parser.parse_args()

    filename = args.file
    main(filename, True if args.animate else False, args.width if args.width else None, args.height if args.height else None)
