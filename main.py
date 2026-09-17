from sys import exit
from parser import parse, MapParseError
from simulation import simulate_all_drones


if __name__ == "__main__":
    try:
        world = parse()
    except IndexError:
        print("Error: usage: python3 main.py <map_file>")
        exit(1)
    except MapParseError as e:
        print(f"Error: {e}")
        exit(1)

    try:
        turns = simulate_all_drones(world)
    except ValueError as error:
        print(f"Error: {error}")
        exit(1)

    for turn in turns:
        print(" ".join(turn))
    print(f"Total turns: {len(turns)}")
