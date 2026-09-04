from parser import parse
from pathfinding import neighbors_of

if __name__ == "__main__":
    world = parse()
    print(f"Start zone: {world.start.name}")
    print(
        f"Neighbors of {world.start.name}: {neighbors_of(world, world.start.name)}")
