from typing import Any, cast
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.patches import RegularPolygon
from matplotlib.text import Text
import math
import numpy as np
import matplotlib as mpl
from parser import Map


DRONE_ICON_PATH = "assets/drone.png"
drone_icon = plt.imread(DRONE_ICON_PATH)
_HSV_CMAP = mpl.colormaps["hsv"]

# runs once


def build_coord_to_zone(world: Map) -> dict[tuple[float, float], str]:
    """Build a lookup from coordinates to zone names."""
    mapping: dict[tuple[float, float], str] = {}
    for zone_name in world.zones:
        zone = world.zones[zone_name]
        mapping[(zone.x, zone.y)] = zone_name
    return mapping

# v runs per frame


def compute_occupancy(
        positions: dict[int, tuple[float, float]],
        coord_to_zone: dict[tuple[float, float], str]
        ) -> dict[str, int]:
    """Count how many drones are currently in each zone."""
    counts: dict[str, int] = {}
    for drone_id in positions:
        zone_name = coord_to_zone.get(positions[drone_id])
        if zone_name is not None:
            counts[zone_name] = counts.get(zone_name, 0) + 1
    return counts


def generate_rainbow_diagonal(
        size: int = 100
        ) -> np.ndarray[Any, Any]:
    """Generate the diagonal gradient used by rainbow zones."""
    # makes an evenly-spaced list from 0 to 1
    gradient = np.linspace(0, 1, size)
    diagonal = np.add.outer(gradient, gradient)  # make it into a grid
    return cast(np.ndarray[Any, Any], diagonal / diagonal.max())


def draw_rainbow_zone(
        ax: Axes,
        x: float,
        y: float,
        radius: float = 0.23
        ) -> tuple[Any, Any, np.ndarray[Any, Any]]:
    """Draw a rainbow-filled hexagonal zone."""
    diagonal = generate_rainbow_diagonal(size=40)
    hexagon_patch = RegularPolygon(
        (x, y),
        numVertices=6,
        radius=radius,
        edgecolor="black",
        facecolor="none",
        linewidth=2
    )
    ax.add_patch(hexagon_patch)
    image_artist = ax.imshow(
        _HSV_CMAP(diagonal),
        extent=(
            x - radius,
            x + radius,
            y - radius,
            y + radius
        ),
        zorder=3
    )
    image_artist.set_clip_path(hexagon_patch)
    return hexagon_patch, image_artist, diagonal


def draw_drone(
        ax: Axes,
        x: float,
        y: float,
        drone_id: int,
        zoom: float,
        label_offset: float
        ) -> tuple[AnnotationBbox, Text]:
    """Draw one drone and its label."""
    image_box = OffsetImage(drone_icon, zoom=zoom)
    annotation = AnnotationBbox(
        image_box,
        (x, y),
        frameon=False,
        zorder=5
    )
    ax.add_artist(annotation)
    label = ax.text(
        x,
        y + label_offset,
        str(drone_id),
        ha="center",
        va="bottom",
        fontsize=8,
        fontweight="bold",
        zorder=6
    )
    return annotation, label


def position_from_move(
        world: Map,
        move_string: str
        ) -> tuple[int, tuple[float, float]]:
    """Convert a movement string into a drone ID and position."""
    drone_part, location = move_string.split("-", 1)
    drone_id = int(drone_part[1:])
    if location in world.zones:
        zone = world.zones[location]
        return drone_id, (zone.x, zone.y)
    zone_a_name, zone_b_name = location.split('-')
    zone_a = world.zones[zone_a_name]
    zone_b = world.zones[zone_b_name]
    # midpoint formula from geometry
    midpoint = (
        (zone_a.x + zone_b.x) / 2,
        (zone_a.y + zone_b.y) / 2
    )
    return drone_id, midpoint


def build_position_history(
        world: Map,
        turns: list[list[str]]
        ) -> list[dict[int, tuple[float, float]]]:
    """Build the position of every drone for each turn."""

    history: list[dict[int, tuple[float, float]]] = []
    current_positions: dict[int, tuple[float, float]] = {}
    assert world.start is not None
    for i in range(1, world.nb_drones + 1):
        current_positions[i] = (world.start.x, world.start.y)
    for turn in turns:
        for move_string in turn:
            drone_id, position = position_from_move(world, move_string)
            current_positions[drone_id] = position
        history.append(dict(current_positions))
    return history


def resolve_zone_color(raw_color: str | None) -> str:
    """Resolve a map color or return the default color."""
    if raw_color is None:
        return "lightgray"  # just a gray default
    if raw_color.lower() == "rainbow":
        return "rainbow"  # special, not a default color
    if mcolors.is_color_like(raw_color):  # using the imported mcolors alias
        return raw_color
    return "lightgray"  # anything else


def compute_hexagon_radius(world: Map) -> float:
    """Calculate a suitable hexagon radius for the map."""
    if not world.connections:
        return 0.3
    distances: list[float] = []
    for conn in world.connections:
        zone_a = world.zones[conn.zone_a]
        zone_b = world.zones[conn.zone_b]
        distances.append(
            math.hypot(
                zone_a.x - zone_b.x,
                zone_a.y - zone_b.y
            )
        )
    radius = min(distances) * 0.3
    return max(0.12, min(radius, 0.4))


def draw_static_layout(
        axes: Axes,
        world: Map,
        hex_radius: float
        ) -> tuple[
            list[tuple[Any, Any, np.ndarray[Any, Any]]],
            dict[str, Text]
        ]:
    """Draw connections, zones, labels, and the legend."""
    rainbow_zones: list[
        tuple[Any, Any, np.ndarray[Any, Any]]
    ] = []
    zone_labels: dict[str, Text] = {}
    zone_label_offset = hex_radius + 0.15

    for conn in world.connections:
        zone_a = world.zones[conn.zone_a]
        zone_b = world.zones[conn.zone_b]
        if zone_a.zone_type == "restricted" or (
                zone_b.zone_type == "restricted"):
            linestyle = "dashed"
            line_color = "black"
        elif zone_a.zone_type == "priority" or (
                zone_b.zone_type == "priority"):
            linestyle = "-."
            line_color = "indianred"
        else:
            linestyle = "solid"
            line_color = "black"

        linewidth = min(
            5.0,
            1.0 + (conn.max_link_capacity - 1) * 0.3
        )
        axes.plot(
            [zone_a.x, zone_b.x],
            [zone_a.y, zone_b.y],
            color=line_color,
            linewidth=linewidth,
            linestyle=linestyle,
            zorder=1
        )

    rainbow_zones = []
    zone_labels = {}
    zone_label_offset = hex_radius + 0.15

    for zone_name in world.zones:
        zone = world.zones[zone_name]
        color = resolve_zone_color(zone.color)

        if color == "rainbow":
            pieces = draw_rainbow_zone(
                axes,
                zone.x,
                zone.y,
                radius=hex_radius
            )
            rainbow_zones.append(pieces)
        else:
            hexagon = RegularPolygon(
                (zone.x, zone.y),
                numVertices=6,
                radius=hex_radius,
                facecolor=color,
                edgecolor="black",
                zorder=3
            )
            axes.add_patch(hexagon)

        if zone.zone_type == "blocked":
            cross_color = (
                "white" if color.lower() == "black" else "black"
            )
            cross_size = hex_radius * 0.55

            axes.plot(
                [zone.x - cross_size, zone.x + cross_size],
                [zone.y - cross_size, zone.y + cross_size],
                color=cross_color,
                linewidth=4,
                zorder=4
            )
            axes.plot(
                [zone.x - cross_size, zone.x + cross_size],
                [zone.y + cross_size, zone.y - cross_size],
                color=cross_color,
                linewidth=4,
                zorder=4
            )

        capacity = (
            "inf"
            if zone in (world.start, world.end)
            else str(zone.max_drones)
        )
        label = axes.text(
            zone.x,
            zone.y - zone_label_offset,
            f"{zone.name}\n0/{capacity}",
            ha="center",
            va="top",
            fontsize=7,
            fontweight="bold",
            zorder=5
        )
        zone_labels[zone.name] = label

    xs = [zone.x for zone in world.zones.values()]
    ys = [zone.y for zone in world.zones.values()]
    axes.set_aspect("equal")
    axes.axis("off")
    padding = 0.4

    bottom_padding = padding + hex_radius + 0.15
    top_padding = padding + max(
        0.8,
        (max(ys) - min(ys)) * 0.05
    )

    axes.set_xlim(
        min(xs) - padding,
        max(xs) + padding
    )
    axes.set_ylim(
        min(ys) - bottom_padding,
        max(ys) + top_padding
    )
    axes.set_autoscale_on(False)

    legend_elements = [
        Line2D(
            [0],
            [0],
            color="black",
            linestyle="solid",
            label="Normal connection"
        ),
        Line2D(
            [0],
            [0],
            color="black",
            linestyle="dashed",
            label="Restricted zone"
        ),
        Line2D(
            [0],
            [0],
            color="indianred",
            linestyle="-.",
            label="Priority zone"
        ),
        Line2D(
            [0],
            [0],
            color="black",
            marker="x",
            markersize=9,
            markeredgewidth=3,
            linestyle="None",
            label="Blocked zone"
        )
    ]
    axes.legend(
        handles=legend_elements,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.01),
        ncol=4,
        fontsize=8,
        framealpha=0.9
    )
    return rainbow_zones, zone_labels


def draw_info_boxes(
        ax: Axes,
        level: str,
        map_name: str
        ) -> tuple[Text, Text]:
    """Draw the level, map, delivery, and turn information."""
    level_colors = {
        "easy": "#4CAF50",
        "medium": "#FFC107",
        "hard": "#FF5722",
        "challenger": "#9C27B0"
    }
    color = level_colors.get(level, "gray")
    ax.text(
        0.02,
        0.995,
        f"LEVEL: {level.upper()}",
        transform=ax.transAxes,
        fontsize=13,
        fontweight="bold",
        color=color,
        va="top",
        ha="left"
    )
    ax.text(
        0.02,
        0.945,
        f"MAP: {map_name}",
        transform=ax.transAxes,
        fontsize=11,
        va="top",
        ha="left"
    )
    delivered_label = ax.text(
        0.98,
        0.995,
        "DELIVERED: 0/0",
        transform=ax.transAxes,
        fontsize=11,
        fontweight="bold",
        va="top",
        ha="right"
    )
    turn_label = ax.text(
        0.98,
        0.945,
        "TURN: 0",
        transform=ax.transAxes,
        fontsize=11,
        va="top",
        ha="right"
    )
    return delivered_label, turn_label


def spread_clustered_positions(
        positions: dict[int, tuple[float, float]],
        spread_radius: float = 0.25
        ) -> dict[int, tuple[float, float]]:
    """Spread drones that share the same position."""
    groups: dict[tuple[float, float], list[int]] = {}
    for drone_id in positions:
        pos = positions[drone_id]
        if pos not in groups:
            groups[pos] = []
        groups[pos].append(drone_id)

    spread: dict[int, tuple[float, float]] = {}
    for pos in groups:
        drone_ids = groups[pos]
        count = len(drone_ids)
        if count == 1:
            spread[drone_ids[0]] = pos
            continue

        for i in range(count):
            angle = 2 * math.pi * i / count
            offset_x = spread_radius * math.cos(angle)
            offset_y = spread_radius * math.sin(angle)
            spread[drone_ids[i]] = (
                pos[0] + offset_x,
                pos[1] + offset_y
            )
    return spread


# v window and inside plotting area
# figure, axes = plt.subplots(figsize=(20, 20))
# draw_static_layout(axes, world)
# plt.show()
# idea: create each drone's icon and label once before animation starts,
# then each frame you move those
# existing objects to a new position, rather than deleting and recreating them.


def animate_simulation(
        world: Map,
        history: list[dict[int, tuple[float, float]]],
        level: str,
        map_name: str,
        interval_ms: int = 1500
        ) -> FuncAnimation:
    """Animate the simulated drone movements."""
    assert world.start is not None
    assert world.end is not None

    coord_to_zone = build_coord_to_zone(world)
    xs = [zone.x for zone in world.zones.values()]
    ys = [zone.y for zone in world.zones.values()]
    map_width = max(xs) - min(xs)
    map_height = max(ys) - min(ys)

    label_offset = min(
        0.35,
        max(0.08, max(map_width, map_height) * 0.015)
    )
    fig_width = max(14.0, map_width * 1.3)
    fig_height = max(10.0, map_height * 1.3)

    fig, ax = plt.subplots(
        figsize=(fig_width, fig_height)
    )
    hex_radius = compute_hexagon_radius(world)
    rainbow_zones, zone_labels = draw_static_layout(
        ax,
        world,
        hex_radius
    )
    delivered_label, turn_label = draw_info_boxes(
        ax,
        level,
        map_name
    )

    fig.canvas.draw()
    origin_px = ax.transData.transform((0, 0))
    edge_px = ax.transData.transform(
        (hex_radius, 0)
    )
    hex_radius_px = abs(
        edge_px[0] - origin_px[0]
    )
    icon_zoom = max(
        0.03,
        min(
            0.2,
            (hex_radius_px * 1.6) / drone_icon.shape[1]
        )
    )

    manager = plt.get_current_fig_manager()
    manager.set_window_title("FLY-IN SIMULATION")
    if hasattr(manager, "window"):
        manager.window.report_callback_exception = lambda *args: None

    fig.subplots_adjust(
        left=0.02,
        right=0.98,
        bottom=0.02,
        top=0.84
    )

    drone_artists: dict[int, Any] = {}
    drone_labels: dict[int, Text] = {}

    for drone_id in range(1, world.nb_drones + 1):
        x, y = history[0][drone_id]
        annotation, label = draw_drone(
            ax,
            x,
            y,
            drone_id,
            icon_zoom,
            label_offset
        )
        drone_artists[drone_id] = annotation
        drone_labels[drone_id] = label

    def update(frame_index: int) -> None:
        """Update drone positions and simulation labels."""
        positions = history[frame_index]
        occupancy = compute_occupancy(
            positions,
            coord_to_zone
        )
        delivered_count = 0
        assert world.end is not None
        end_zone = world.zones[world.end.name]
        end_pos = (end_zone.x, end_zone.y)

        for drone_id in positions:
            if positions[drone_id] == end_pos:
                delivered_count += 1

        delivered_label.set_text(
            f"DELIVERED: {delivered_count}/{world.nb_drones}"
        )
        turn_label.set_text(
            f"TURN: {frame_index + 1}/{len(history)}"
        )

        for zone_name in world.zones:
            zone = world.zones[zone_name]
            count = occupancy.get(zone_name, 0)
            capacity = (
                "inf"
                if zone in (world.start, world.end)
                else str(zone.max_drones)
            )
            zone_labels[zone_name].set_text(
                f"{zone_name}\n{count}/{capacity}"
            )

        for drone_id in positions:
            x, y = positions[drone_id]
            if drone_id not in drone_artists:
                annotation, label = draw_drone(
                    ax,
                    x,
                    y,
                    drone_id,
                    icon_zoom,
                    label_offset
                )
                drone_artists[drone_id] = annotation
                drone_labels[drone_id] = label
                continue

            drone_artists[drone_id].xy = (x, y)
            drone_artists[drone_id].xybox = (x, y)
            drone_labels[drone_id].set_position(
                (x, y + label_offset)
            )

    rainbow_offset: dict[str, float] = {"value": 0.0}

    def update_rainbow(frame_index: int) -> list[Any]:
        """Update the animated rainbow zone colors."""
        rainbow_offset["value"] = (
            rainbow_offset["value"] - 0.15
        ) % 1.0
        updated_artists: list[Any] = []

        for hexagon_patch, image_artist, diagonal in rainbow_zones:
            shifted = (
                diagonal + rainbow_offset["value"]
            ) % 1.0
            image_artist.set_data(
                _HSV_CMAP(shifted)
            )
            updated_artists.append(image_artist)

        return updated_artists

    anim = FuncAnimation(
        fig,
        update,
        frames=len(history),
        interval=interval_ms,
        repeat=False
    )

    rainbow_anim = FuncAnimation(
        fig,
        update_rainbow,
        interval=50,
        cache_frame_data=False,
        blit=False
    )

    def on_close(event: Any) -> None:
        try:
            anim.pause()
        except AttributeError:
            pass
        try:
            rainbow_anim.pause()
        except AttributeError:
            pass

    fig.canvas.mpl_connect("close_event", on_close)

    plt.show()
    return anim
