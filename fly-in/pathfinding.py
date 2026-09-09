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
                       penalty: int = 1
) -> list[str] | None:
    distances: dict[str, int]= {world.start.name: 0}
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

def move_cost(zone: Zone)-> int:
    if zone.zone_type == "blocked":
        return -1
    if zone.zone_type == "restricted":
        return 2
    return 1

