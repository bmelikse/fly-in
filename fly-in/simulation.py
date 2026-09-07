from parser import Map, Zone, Connection
from pathfinding import move_cost, find_shortest_path


class DroneState:
    def __init__(self, drone_id: int, path: list[str]) -> None:
        self.drone_id = drone_id  # D1, D2, D3...
        self.path = path  # full route
        self.path_index = 0  # where the drone currently is
        self.turns_waited = 0
        self.delivered = False  # has it reached the end?
        self.in_transit = False  # is it mid-flight on a 2 turn restricted move?
        self.transit_turns_left = 0  # if in_transit, how many turns until arrival?


def simulate_single_drone(world: Map, path: list[str]) -> list[list[str]]:
    """Returns a list of turns; each turn is a list of movement strings like
     'D1-roof1'."""
    # format is: D<ID>-<zone>
    turns: list[list[str]] = []

    for i in range(len(path) - 1):  # one num per move not zone
        current_zone = path[i]
        next_zone_name = path[i + 1]
        next_zone = world.zones[next_zone_name]
        cost = move_cost(next_zone)

        if cost == 1:
            turns.append([f"D1-{next_zone_name}"])
        elif cost == 2:
            connection_name = f"{current_zone}-{next_zone_name}"
            turns.append([f"D1-{connection_name}"])
            turns.append([f"D1-{next_zone_name}"])

    return turns


def all_delivered(drones: list[DroneState]) -> bool:
    for drone in drones:
        if not drone.delivered:
            return False
    return True


def simulate_all_drones(world: Map) -> list[list[str]]:
    path = find_shortest_path(world)
    if path is None:
        raise ValueError("No path exists between start and end zones")

    drones = []
    for i in range(1, world.nb_drones + 1):
        drone = DroneState(i, path)
        drones.append(drone)

    # way to look up a connection's max link capacity just from its name string:
    connection_capacity: dict[str, int] = {}
    for conn in world.connections:
        connection_capacity[f"{conn.zone_a}-{conn.zone_b}"] = conn.max_link_capacity
        connection_capacity[f"{conn.zone_b}-{conn.zone_a}"] = conn.max_link_capacity

    # live counts:
    # how many drones are currently standing in this zone rn?
    zone_occupancy: dict[str, int] = {world.start.name: world.nb_drones}
    # same but for connections (how many drones are currently mid-transit thru each one)
    connection_occupancy: dict[str, int] = {}
    turns: list[list[str]] = []

    while not all_delivered(drones):
        # movement strings thatll actually get printed for this turn, it appends to the turns at the end
        turn_moves: list[str] = []
        wanting_to_move: list[DroneState] = []

        for drone in drones:
            if drone.delivered:
                continue

            if drone.in_transit:
                drone.transit_turns_left -= 1
                if drone.transit_turns_left == 0:
                    drone.in_transit = False
                    current_zone_name = drone.path[drone.path_index]
                    drone.path_index += 1
                    arrived_zone = drone.path[drone.path_index]
                    connection_name = f"{current_zone_name}-{arrived_zone}"
                    connection_occupancy[connection_name] -= 1
                    zone_occupancy[arrived_zone] = zone_occupancy.get(
                        arrived_zone, 0) + 1
                    turn_moves.append(f"D{drone.drone_id}-{arrived_zone}")
                    if arrived_zone == world.end.name:
                        drone.delivered = True
                continue

            wanting_to_move.append(drone)

        # accounting for same-turn departures, before checking zone capacity:
        # (this now runs ONCE, after wanting_to_move is fully built, not nested per-drone)
        temp_zone_occupancy: dict[str, int] = dict(zone_occupancy)
        for drone in wanting_to_move:
            current_zone_name = drone.path[drone.path_index]
            temp_zone_occupancy[current_zone_name] = temp_zone_occupancy.get(
                current_zone_name, 0) - 1

        # part 2 - build requests
        zone_requests: dict[str, list[DroneState]] = {}
        connection_requests: dict[str, list[DroneState]] = {}

        for drone in wanting_to_move:
            next_zone_name = drone.path[drone.path_index + 1]
            next_zone = world.zones[next_zone_name]
            cost = move_cost(next_zone)
            current_zone_name = drone.path[drone.path_index]

            if cost == 1:
                if next_zone_name not in zone_requests:
                    zone_requests[next_zone_name] = []
                zone_requests[next_zone_name].append(drone)
            else:
                connection_name = f"{current_zone_name}-{next_zone_name}"
                if connection_name not in connection_requests:
                    connection_requests[connection_name] = []
                connection_requests[connection_name].append(drone)

        # next part - granting zone requests, tie-break by longest wait:
        granted: list[DroneState] = []

        for zone_name in zone_requests:
            requesters = zone_requests[zone_name]
            requesters.sort(key=lambda d: d.turns_waited, reverse=True)
            zone = world.zones[zone_name]
            # how much room is actually left
            free_slots = zone.max_drones - \
                temp_zone_occupancy.get(zone_name, 0)

            for drone in requesters:
                if free_slots <= 0:
                    break
                granted.append(drone)
                free_slots -= 1

        # same idea but for connections:
        for connection_name in connection_requests:
            requesters = connection_requests[connection_name]
            requesters.sort(key=lambda d: d.turns_waited, reverse=True)
            max_capacity = connection_capacity[connection_name]
            current_usage = connection_occupancy.get(connection_name, 0)
            free_slots = max_capacity - current_usage
            for drone in requesters:
                if free_slots <= 0:
                    break
                granted.append(drone)
                free_slots -= 1

        # commit: granted drones actually move, everyone else waits
        for drone in wanting_to_move:
            next_zone_name = drone.path[drone.path_index + 1]
            next_zone = world.zones[next_zone_name]
            cost = move_cost(next_zone)
            current_zone_name = drone.path[drone.path_index]

            if drone not in granted:
                drone.turns_waited += 1
                continue

            zone_occupancy[current_zone_name] -= 1
            drone.turns_waited = 0

            if cost == 1:
                drone.path_index += 1
                zone_occupancy[next_zone_name] = zone_occupancy.get(
                    next_zone_name, 0) + 1
                turn_moves.append(f"D{drone.drone_id}-{next_zone_name}")
                if next_zone_name == world.end.name:
                    drone.delivered = True
            else:
                connection_name = f"{current_zone_name}-{next_zone_name}"
                drone.in_transit = True
                drone.transit_turns_left = cost - 1
                connection_occupancy[connection_name] = connection_occupancy.get(
                    connection_name, 0) + 1
                turn_moves.append(f"D{drone.drone_id}-{connection_name}")

        turns.append(turn_moves)

    return turns
