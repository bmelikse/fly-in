from sys import argv

class Map:
    def __init__(self,
                 nb_drones: int = 0,
                 start: "Zone | None" = None,
                 end: "Zone | None" = None,
                 zones: dict | None = None,
                 connections: None = None) -> None:
        self.nb_drones = nb_drones
        self.start = start
        self.end = end
        self.zones = zones if zones is not None else {}
        self.connections: list | None = connections if connections is not None else []

class Zone:
    def __init__(self,
                 name: str = "None",
                 zone_type: None = None,
                 max_drones: int = 0,
                 color: str = "white"
    ) -> None:
        self.name = name
        self.zone_type = zone_type
        self.max_drones = max_drones
        self.color = color

    @classmethod
    def from_line(cls, line: str) -> "Zone":
        fixed_part, metadata = split_metadata(line)
        name, x, y = fixed_part.split()
        return cls(
            name=name,
            x=int(x),
            y=int(y),
            zone_type=metadata.get("zone", "normal"),
            max_drones=int(metadata.get("max_drones", 1)),
            color=metadata.get("color")
        )
class Connection:
    pass


def parse():
    possible_colors = {"green", "blue", "red"}
    try:
        zone = Zone()
        with open(argv[1], "r") as file:
            for line in file:
                if line[0] == "#" or not line.strip():
                    continue
                # if line.startswith("nb_drones: "):
                #     zone.nb_drones = int(line.replace("nb_drones: ", ""))
                #     print(zone.nb_drones)
                # if line.startswith("start_hub: "):
                #     line = line.replace("start_hub: ", "")
                #     if line.startswith("start"):
                #         line = line.replace("start", "")
                #         if line.endswith(f"[color={color for color in possible_colors if color is possible_colors}]"):
                #             line = line.replace(f"[color={color for color in possible_colors if color is possible_colors}]", "")
                #             zone.start = line.strip()
                # #same nonsense for "end_hub"     
    except ValueError as e:
        print(f"Error: {e}")


def split_metadata(line: str) -> tuple[str, dict[str, str]]:
    '''Split mandatory information and optional metadata into a dict'''
    metadata: dict[str, str] = {}
    fixed_part = line

    if "[" in line:
        fixed_part, bracket_part = line.split("[", 1)
        bracket_part = bracket_part.replace("]", "")

        for pair in bracket_part.split():  # splits on whitespace in case theres multiple metadata
            key, value = pair.split("=")
            metadata[key] = value

    return fixed_part.strip(), metadata


if __name__ == "__main__":
    parse()
    print(split_metadata("start 0 0 [color=green]"))
