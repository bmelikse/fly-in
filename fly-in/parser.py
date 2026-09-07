from sys import argv


class Map:
    def __init__(self,
                 nb_drones: int = 0,
                 start: "Zone | None" = None,
                 end: "Zone | None" = None,
                 zones: dict[str, "Zone"] | None = None,
                 connections: list["Connection"] | None = None
                 ) -> None:
        self.nb_drones = nb_drones
        self.start = start
        self.end = end
        self.zones = zones if zones is not None else {}
        self.connections: list["Connection"] = (
            connections if connections is not None else []
        )


class Zone:
    def __init__(self,
                 name: str,
                 zone_type: str = "normal",
                 max_drones: int = 0,
                 x: int = 0,
                 y: int = 0,
                 color: str | None = None
                 ) -> None:
        self.name = name
        self.zone_type = zone_type
        self.max_drones = max_drones
        self.color = color
        self.x = x
        self.y = y

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
    def __init__(self,
                 zone_a: str,
                 zone_b: str,
                 max_link_capacity: int = 1
                 ) -> None:
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity

    @classmethod
    def from_line(cls, line: str) -> 'Connection':
        fixed_part, metadata = split_metadata(line)
        zone_a, zone_b = fixed_part.split("-")
        return cls(zone_a=zone_a,
                   zone_b=zone_b,
                   max_link_capacity=int(metadata.get(
                       "max_link_capacity", 1))  # 1 is default value
                   )


def parse() -> Map:
    '''split each line's prefix, give the rest to the right from_line,
    and assemble everything into one Map'''
    world = Map()
    try:
        with open(argv[1], "r") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("nb_drones:"):
                    world.nb_drones = int(line.removeprefix("nb_drones:").strip())
                elif line.startswith("start_hub:"):
                    zone = Zone.from_line(line.removeprefix("start_hub:").strip())
                    world.zones[zone.name] = zone
                    world.start = zone
                elif line.startswith("end_hub:"):
                    zone = Zone.from_line(line.removeprefix("end_hub:").strip())
                    world.zones[zone.name] = zone
                    world.end = zone
                elif line.startswith("hub:"):
                    zone = Zone.from_line(line.removeprefix("hub:").strip())
                    world.zones[zone.name] = zone
                elif line.startswith("connection:"):
                    conn = Connection.from_line(
                        line.removeprefix("connection:").strip())
                    world.connections.append(conn)
    except (IndexError, AttributeError) as e:
        print(f"Error: {e}")
    return world


def split_metadata(line: str) -> tuple[str, dict[str, str]]:
    '''Split mandatory information and optional metadata into a dict'''
    metadata: dict[str, str] = {}
    fixed_part = line

    if "[" in line:
        fixed_part, bracket_part = line.split("[", 1)
        bracket_part = bracket_part.replace("]", "")

        # splits on whitespace in case theres multiple metadata
        for pair in bracket_part.split():
            key, value = pair.split("=")
            metadata[key] = value

    return fixed_part.strip(), metadata

