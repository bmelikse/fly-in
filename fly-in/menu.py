from pathlib import Path
from parser import parse
from simulation import simulate_all_drones
from visualization import build_position_history, animate_simulation


MAPS_DIR = Path("maps")
DIFFICULTIES = ["easy", "medium", "hard", "challenger"]


def choose_difficulty() -> str:
    print("Choose difficulty:")
    for i, level in enumerate(DIFFICULTIES, start=1):
        print(f"  {i}. {level}")
    choice = input("> ").strip()
    index = int(choice) - 1
    return DIFFICULTIES[index]


def choose_map(level: str) -> Path:
    level_dir = MAPS_DIR / level
    maps = sorted(p for p in level_dir.iterdir() if p.is_file())
    print(f"Maps for {level}:")
    for i, map_path in enumerate(maps, start=1):
        print(f"  {i}. {map_path.name}")
    choice = input("> ").strip()
    index = int(choice) - 1
    return maps[index]


def main() -> None:
    level = choose_difficulty()
    map_path = choose_map(level)

    world = parse(str(map_path))
    turns = simulate_all_drones(world)
    for turn in turns:
        print(" ".join(turn))
    print(f"Total turns: {len(turns)}")

    show_viz = input("Show visualization? (y/n): ").strip().lower()
    if show_viz == "y":
        history = build_position_history(world, turns)
        animate_simulation(world, history, level, map_path.name)


if __name__ == "__main__":
    main()
