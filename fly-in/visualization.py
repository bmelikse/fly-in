import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from parser import Map, parse

def resolve_zone_color(raw_color: str | None) -> str:
    if raw_color is None:
        return "lightgray"  # just a gray default

    if raw_color.lower() == "rainbow":
        return "rainbow"  # special, not a default color

    if mcolors.is_color_like(raw_color):  # using the imported mcolors alias
        return raw_color

    return "lightgray"  # anything else


def draw_static_map(world: Map) -> None:
    # v window and inside plotting area
    figure, axes = plt.subplots(figsize=(8, 8))

    for zone_name in world.zones:
        zone = world.zones[zone_name]
        color = resolve_zone_color(zone.color)

        if zone is world.start:
            marker = "s"  # square!
        elif zone is world.end:
            marker = "*"  # star
        else:
            marker = "h" # hexagon
        
        axes.scatter(zone.x, zone.y, marker=marker, s=800, c=color,
                     edgecolors="black", zorder=3)
        axes.text(zone.x, zone.y, zone.name, ha="center", va="center",
                  fontsize=7, zorder=4)
        
    axes.set_aspect("equal")
    axes.axis("off")
    plt.show()


draw_static_map(parse())