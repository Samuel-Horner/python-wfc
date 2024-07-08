import argparse
import json

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

def parse_file(input_file):
    try: file = open(input_file, "r")
    except: input_file_error()
    input = json.load(file)
    tile_strings = ["\x1b[" + input["tiles"][i] + "\x1b[0m" if input["format"] else input["tiles"][i] for i in range(len(input["tiles"]))]

    return wfc.parse_input(input), tile_strings, input["width"], input["height"]

def print_map(map, tile_strings):
    for i in range(map.height):
        for j in range(map.width):
            tile = map.map[i][j]
            if (tile == 0): print("-", end=" ")
            else: print(tile_strings[tile - 1], end=" ")
        print()
    
def main(file):
    tiles, tile_strings, width, height = parse_file(file)
    map = wfc.Map(tiles, width, height)
    try: map.generate()
    except wfc.TileSetError:
        print_map(map, tile_strings) 
        tileset_error()
    print_map(map, tile_strings)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="The input json file to read from.")
    args = parser.parse_args()

    filename = args.file 
    main(filename)