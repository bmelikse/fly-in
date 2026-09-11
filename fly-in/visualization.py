import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from parser import Map, parse
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.animation import FuncAnimation


DRONE_ICON_PATH = "assets/drone3.png"
drone_icon = plt.imread(DRONE_ICON_PATH)

def draw_drone(axes, x: float, y: float, drone_id: int) -> None:
    image_box = OffsetImage(drone_icon, zoom=0.09)
    annotation = AnnotationBbox(image_box, (x, y), frameon=False, zorder=5)
    axes.add_artist(annotation)

    axes.text(x, y + 0.2, str(drone_id), ha="center", va="bottom",
              fontsize=10,  color="black", zorder=6)


def position_from_move(world: Map, move_string: str) -> tuple[int, tuple[float, float]]:
    drone_part, location = move_string.split("-", 1)
    drone_id = int(drone_part[1:])

    if location in world.zones:
        zone = world.zones[location]
        return drone_id, (zone.x, zone.y)
    
    zone_a_name, zone_b_name = location.split('-')
    zone_a = world.zones[zone_a_name]
    zone_b = world.zones[zone_b_name]
    midpoint = ((zone_a.x + zone_b.x) / 2, (zone_a.y + zone_b.y) / 2)  # midpoint formula from geometry
    return drone_id, midpoint


def build_position_history(world: Map, turns: list[list[str]]) -> list[dict[int, tuple[float, float]]]:
    history: list[dict[int, tuple[float, float]]] = []
    current_positions: dict[int, tuple[float, float]] = {}

    for i in range(1, world.nb_drones + 1):
        current_positions[i] = (world.start.x, world.start.y)
    
    for turn in turns:
        for move_string in turn:
            drone_id, position = position_from_move(world, move_string)
            current_positions[drone_id] = position
        
        history.append(dict(current_positions))
    
    return history

def resolve_zone_color(raw_color: str | None) -> str:
    if raw_color is None:
        return "lightgray"  # just a gray default

    if raw_color.lower() == "rainbow":
        return "rainbow"  # special, not a default color

    if mcolors.is_color_like(raw_color):  # using the imported mcolors alias
        return raw_color

    return "lightgray"  # anything else


def draw_static_layout(axes, world: Map) -> None:
    for conn in world.connections:
        zone_a = world.zones[conn.zone_a]
        zone_b = world.zones[conn.zone_b]

        if zone_a.zone_type == "restricted" or zone_b.zone_type == "restricted":
            linestyle = "dashed"
        elif zone_a.zone_type == "priority" or zone_b.zone_type == "priority":
            linestyle = "dotted"
        else:
            linestyle = "solid"
        # base 1.5, grows for every extra unit of capacity beyond it
        linewidth = 1.5 + (conn.max_link_capacity - 1) * 0.5 

        axes.plot([zone_a.x, zone_b.x], [zone_a.y, zone_b.y],
                  color="black", linewidth=linewidth, linestyle=linestyle, zorder=1)

    for zone_name in world.zones:
        zone = world.zones[zone_name]
        color = resolve_zone_color(zone.color)

        if zone is world.start:
            marker = "s"  # square!
        elif zone is world.end:
            marker = "*"  # star
        else:
            marker = "h" # hexagon
        
        axes.scatter(zone.x, zone.y, marker=marker, s=1500, c=color,
                     edgecolors="black", zorder=3)
        axes.text(zone.x, zone.y - 0.3, zone.name, ha="center", va="top",
                  fontsize=11, zorder=4)
    

        axes.set_aspect("equal")
        axes.axis("off")

world = parse()
# v window and inside plotting area
figure, axes = plt.subplots(figsize=(20, 20))

draw_static_layout(axes, world)
plt.show()


def animate_simulation(world: Map, history: list[dict[int, tuple[float, float]]],
                       interval_ms: int = 500):
    fig, ax = plt.subplots(figsize=(20, 20))
    draw_static_layout(ax, world)

    drone_artists: dict[int, AnnotationBbox] = {}
    drone_labels: dict[int, plt.text] = {}

    # to be continued

    