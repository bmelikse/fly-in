from pathlib import Path
from parser import parse, MapParseError
from simulation import simulate_all_drones
from visualization import build_position_history, animate_simulation


MAPS_DIR = Path("maps")
DIFFICULTIES = ["easy", "medium", "hard", "challenger"]


class MenuQuit(Exception):
    """Raised when the user chooses to quit the menu."""


def prompt_choice(options: list[str]) -> int:
    for i, option in enumerate(options, start=1):
        print(f"  {i}. {option}")
    print("  q. Quit")

    while True:
        raw = input("> ").strip().lower()
        if raw in ("q", "quit"):
            raise MenuQuit()
        try:
            choice = int(raw)
        except ValueError:
            print(
                f"Please enter a number between 1 and "
                f"{len(options)}, or 'q' to quit.")
            continue
        if choice < 1 or choice > len(options):
            print(
                f"Please enter a number between 1 and {len(options)}, "
                "or 'q' to quit.")
            continue
        return choice


def choose_difficulty() -> str:
    print("Choose difficulty:")
    choice = prompt_choice(DIFFICULTIES)
    return DIFFICULTIES[choice - 1]


def choose_map(level: str) -> Path:
    level_dir = MAPS_DIR / level
    try:
        entries = list(level_dir.iterdir())
    except FileNotFoundError:
        print(f"Maps directory not found: {level_dir}")
        raise MenuQuit()

    maps = []
    for entry in entries:
        if entry.is_file():
            maps.append(entry)
    maps.sort()

    if not maps:
        print(f"No maps found for {level}.")
        raise MenuQuit()

    print(f"Maps for {level}:")
    map_names = []
    for map_path in maps:
        map_names.append(map_path.name)

    choice = prompt_choice(map_names)
    return maps[choice - 1]


def run_once() -> None:
    level = choose_difficulty()
    map_path = choose_map(level)

    try:
        world = parse(str(map_path))
    except MapParseError as e:
        print(f"Error: {e}")
        return

    turns = simulate_all_drones(world)
    for turn in turns:
        print(" ".join(turn))
    print(f"Total turns: {len(turns)}")

    show_viz = input("Show visualization? (y/n): ").strip().lower()
    if show_viz == "y":
        history = build_position_history(world, turns)
        animate_simulation(world, history, level, map_path.name)


def main() -> None:
    while True:
        try:
            run_once()
        except MenuQuit:
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
