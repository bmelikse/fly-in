from parser import parse
from pathfinding import neighbors_of, find_shortest_path
from simulation import simulate_single_drone, simulate_all_drones

if __name__ == "__main__":
    try:
        world = parse()
        # print(f"Start zone: {world.start.name}")
        # print(
        #     f"Neighbors of {world.start.name}: {neighbors_of(world, world.start.name)}")
        # print(f"Find shortest path: {find_shortest_path(world)}\n")
        # path = find_shortest_path(world)
        # turns = simulate_single_drone(world, path)
        # for turn in turns:
        #     print(" ".join(turn))
        turns = simulate_all_drones(world)
        for turn in turns:
            print(" ".join(turn))
        print(f"Total turns: {len(turns)}")
    except AttributeError as e:
        print(f"Error: {e}")
