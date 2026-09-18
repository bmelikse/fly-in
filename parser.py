from sys import argv

VALID_ZONE_TYPES = {"normal", "restricted", "priority", "blocked"}


class MapParseError(Exception):
    """Raised when a map file is malformed."""


class Map:
    """Hold the full parsed state of a map: drones, zones, and connections."""

    def __init__(self,
                 nb_drones: int = 0,
                 start: "Zone | None" = None,
                 end: "Zone | None" = None,
                 zones: dict[str, "Zone"] | None = None,
                 connections: list["Connection"] | None = None
                 ) -> None:
        """Initialize an empty or pre-filled map."""
        self.nb_drones = nb_drones
        self.start = start
        self.end = end
        self.zones = zones if zones is not None else {}
        self.connections: list["Connection"] = (
            connections if connections is not None else []
        )


class Zone:
    """A single named zone in the map, with position, type, and capacity."""

    def __init__(self,
                 name: str,
                 zone_type: str = "normal",
                 max_drones: int = 0,
                 x: int = 0,
                 y: int = 0,
                 color: str | None = None
                 ) -> None:
        """Initialize a zone with its attributes."""
        self.name = name
        self.zone_type = zone_type
        self.max_drones = max_drones
        self.color = color
        self.x = x
        self.y = y

    @classmethod
    def from_line(cls, line: str) -> "Zone":
        """Parse one zone definition line into a Zone."""
        fixed_part, metadata = split_metadata(line)
        parts = fixed_part.split()
        if len(parts) != 3:
            raise ValueError(f"expected 'name x y', got '{fixed_part}'")
        name, x, y = parts

        zone_type = metadata.get("zone", "normal")
        if zone_type not in VALID_ZONE_TYPES:
            raise ValueError(f"invalid zone type '{zone_type}'")

        max_drones = int(metadata.get("max_drones", 1))
        if max_drones <= 0:
            raise ValueError(
                f"max_drones must be greater than 0, got {max_drones}")

        return cls(
            name=name,
            x=int(x),
            y=int(y),
            zone_type=zone_type,
            max_drones=max_drones,
            color=metadata.get("color")
        )


class Connection:
    """A bidirectional link between two zones, with a capacity limit."""

    def __init__(self,
                 zone_a: str,
                 zone_b: str,
                 max_link_capacity: int = 1
                 ) -> None:
        """Initialize a connection between two named zones."""
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity

    @classmethod
    def from_line(cls, line: str) -> 'Connection':
        """Parse one connection definition line into a Connection."""
        fixed_part, metadata = split_metadata(line)
        if "-" not in fixed_part:
            raise ValueError(f"expected 'zoneA-zoneB', got '{fixed_part}'")
        zone_a, zone_b = fixed_part.split("-", 1)

        max_link_capacity = int(metadata.get("max_link_capacity", 1))
        if max_link_capacity <= 0:
            raise ValueError(
                f"max_link_capacity must be greater than 0, "
                f"got {max_link_capacity}")

        return cls(zone_a=zone_a, zone_b=zone_b,
                   max_link_capacity=max_link_capacity)


def parse(path: str | None = None) -> Map:
    '''split each line's prefix, give the rest to the right from_line,
    and assemble everything into one Map'''
    file_path = path if path is not None else argv[1]
    world = Map()

    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        raise MapParseError(f"file not found: {file_path}")
    except OSError as e:
        raise MapParseError(f"could not read file: {e}")

    line_number = 0
    for raw_line in lines:
        line_number += 1
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        try:
            if line.startswith("nb_drones:"):
                world.nb_drones = int(line.removeprefix("nb_drones:").strip())
            elif line.startswith("start_hub:"):
                zone = Zone.from_line(line.removeprefix("start_hub:").strip())
                if zone.name in world.zones:
                    raise ValueError(f"duplicate zone name '{zone.name}'")
                world.zones[zone.name] = zone
                world.start = zone
            elif line.startswith("end_hub:"):
                zone = Zone.from_line(line.removeprefix("end_hub:").strip())
                if zone.name in world.zones:
                    raise ValueError(f"duplicate zone name '{zone.name}'")
                world.zones[zone.name] = zone
                world.end = zone
            elif line.startswith("hub:"):
                zone = Zone.from_line(line.removeprefix("hub:").strip())
                if zone.name in world.zones:
                    raise ValueError(f"duplicate zone name '{zone.name}'")
                world.zones[zone.name] = zone
            elif line.startswith("connection:"):
                conn = Connection.from_line(
                    line.removeprefix("connection:").strip())
                world.connections.append(conn)
        except (ValueError, IndexError) as e:
            raise MapParseError(f"line {line_number}: {e}") from None

    validate(world)
    return world


def validate(world: Map) -> None:
    """Check that the parsed map is structurally valid,
    raising MapParseError if not."""
    if world.nb_drones <= 0:
        raise MapParseError("nb_drones must be set and greater than 0")
    if world.start is None:
        raise MapParseError("map is missing a start_hub")
    if world.end is None:
        raise MapParseError("map is missing an end_hub")
    for conn in world.connections:
        if conn.zone_a not in world.zones:
            raise MapParseError(
                f"connection references unknown zone '{conn.zone_a}'")
        if conn.zone_b not in world.zones:
            raise MapParseError(
                f"connection references unknown zone '{conn.zone_b}'")


def split_metadata(line: str) -> tuple[str, dict[str, str]]:
    '''Split mandatory information and optional metadata into a dict'''
    metadata: dict[str, str] = {}
    fixed_part = line

    if "[" in line:
        fixed_part, bracket_part = line.split("[", 1)
        bracket_part = bracket_part.replace("]", "")

        for pair in bracket_part.split():
            if "=" not in pair:
                raise ValueError(
                    f"malformed metadata '{pair}', expected key=value")
            key, value = pair.split("=", 1)
            metadata[key] = value

    return fixed_part.strip(), metadata
