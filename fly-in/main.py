from parser import parse
from pathfinding import neighbors_of, find_shortest_path

if __name__ == "__main__":
    world = parse()
    print(f"Start zone: {world.start.name}")
    print(
        f"Neighbors of {world.start.name}: {neighbors_of(world, world.start.name)}")
    print(f"Find shortest path: {find_shortest_path(world)}")
