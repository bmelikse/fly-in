import heapq
from parser import Map, Zone


def neighbors_of(world: Map, zone_name: str) -> list[str]:
    """Return the names of all zones directly connected to zone_name."""
    result = []
    for connection in world.connections:
        if connection.zone_a == zone_name:
            result.append(connection.zone_b)
        if connection.zone_b == zone_name:
            result.append(connection.zone_a)
    return result


def find_shortest_path(world: Map,
                       usage: dict[str, int] | None = None,
                       penalty: float = 0.1  # 0.03 gives 44 moves
                       ) -> list[str] | None:
    distances: dict[str, int] = {world.start.name: 0}
    previous: dict[str, str] = {}
    queue: list[tuple[int, str]] = [(0, world.start.name)]

    while queue:
        current_cost, current_zone = heapq.heappop(queue)
        if current_zone == world.end.name:
            break

        for neighbor_name in neighbors_of(world, current_zone):
            neighbor_zone = world.zones[neighbor_name]
            cost = move_cost(neighbor_zone)
            if cost == -1:
                continue
            if usage is not None:
                cost += usage.get(neighbor_name, 0) * penalty
            new_cost = current_cost + cost

            if neighbor_name not in distances or new_cost < distances[neighbor_name]:
                distances[neighbor_name] = new_cost
                previous[neighbor_name] = current_zone
                heapq.heappush(queue, (new_cost, neighbor_name))

    # no path existing
    if world.end.name not in previous:
        return None

    # reconstruct path
    path = [world.end.name]
    current = world.end.name
    while current != world.start.name:
        current = previous[current]
        path.append(current)
    path.reverse()
    return path


def move_cost(zone: Zone) -> int:
    if zone.zone_type == "blocked":
        return -1
    if zone.zone_type == "restricted":
        return 2
    return 1


def assign_diverse_paths(world: Map) -> dict[int, list[str]]:
    '''loop through all drones sequentially to build customized routes.'''
    usage: dict[str, int] = {}
    paths: dict[int, list[str]] = {}

    for drone_id in range(1, world.nb_drones + 1):
        path = find_shortest_path(world, usage)
        if path is None:
            raise ValueError(f"No path exists for drone {drone_id}")
        paths[drone_id] = path

        for zone_name in path:
            usage[zone_name] = usage.get(zone_name, 0) + 1

    return paths
