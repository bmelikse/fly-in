import os
from parser import parse
from simulation import simulate_all_drones
from visualization import build_position_history, animate_simulation


DIFFICULTIES = ["easy", "medium", "hard", "challenger"]
MAPS_ROOT = "maps"


def list_maps(folder: str) -> list[str]:
    filenames = []

    for name in os.listdir(folder):
        path = os.path.join(folder, name)

        if os.path.isfile(path):
            filenames.append(name)

    filenames.sort()
    return filenames


def run_menu() -> None:
    while True:
        print()
        print("Select difficulty:")

        for i, level in enumerate(DIFFICULTIES, start=1):
            print(f"{i}. {level}")

        print("0. Quit")

        choice = input("> ").strip()

        if choice == "0":
            break

        if choice not in ("1", "2", "3", "4"):
            print("Invalid choice.")
            continue

        level = DIFFICULTIES[int(choice) - 1]

        folder = os.path.join(MAPS_ROOT, level)
        maps = list_maps(folder)

        if not maps:
            print(f"No maps found in {folder}")
            continue

        print()
        print(f"Select a map from {level}:")

        for i, name in enumerate(maps, start=1):
            print(f"{i}. {name}")

        map_choice = input("> ").strip()

        if not map_choice.isdigit():
            print("Invalid choice.")
            continue

        map_index = int(map_choice)

        if not (1 <= map_index <= len(maps)):
            print("Invalid choice.")
            continue

        map_name = maps[map_index - 1]
        map_path = os.path.join(folder, map_name)

        print()
        print(f"Loading {map_name}...")

        world = parse(map_path)
        turns = simulate_all_drones(world)
        history = build_position_history(world, turns)

        animate_simulation(
            world,
            history,
            level=level,
            map_name=map_name,
            interval_ms=500
        )


if __name__ == "__main__":
    run_menu()
