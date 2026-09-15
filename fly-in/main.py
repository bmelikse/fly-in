from parser import parse
from simulation import simulate_all_drones

if __name__ == "__main__":
    try:
        world = parse()
        turns = simulate_all_drones(world)
        for turn in turns:
            print(" ".join(turn))
        print(f"Total turns: {len(turns)}")
    except AttributeError as e:
        print(f"Error: {e}")
