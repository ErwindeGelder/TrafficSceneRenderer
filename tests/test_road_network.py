"""Scripts for testing road_network.py.

Author(s): Erwin de Gelder
"""

from pathlib import Path
from typing import Tuple

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from traffic_scene_renderer import (
    RoadNetwork,
    RoadNetworkOptions,
    StopLineOptions,
    Vertex,
    Way,
    WayOptions,
)

from .test_static_objects import save_fig

mpl.use("Agg")


def test_road_network_creation() -> None:
    vertices = [Vertex(1, -10, 0), Vertex(2, 10, 0)]
    ways = [Way(vertices)]
    road_network = RoadNetwork(ways, vertices)
    road_network.process()
    fig, axes = road_network.plot()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-5, 5)
    save_fig(fig, axes, Path("road_network") / "straight_road.png", 10)


def test_automatic_crossing_creation() -> None:
    vertices = [Vertex(0, -10, 0), Vertex(1, 0, 0), Vertex(2, 10, 0), Vertex(3, 0, 10)]
    ways = [Way(vertices[:3]), Way([vertices[1], vertices[3]])]
    road_network = RoadNetwork(ways, vertices)
    road_network.process()
    fig, axes = road_network.plot()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-5, 10)
    save_fig(fig, axes, Path("road_network") / "crossing.png", 10)


def test_automatic_connection_creation() -> None:
    vertices = [
        Vertex(0, -10, 10),
        Vertex(1, -10, 0),
        Vertex(2, 0, 0),
        Vertex(3, 10, 0),
        Vertex(4, 10, 10),
    ]
    ways = [
        Way([vertices[0], vertices[1]], WayOptions(side_color=(1, 0, 0))),
        Way([vertices[2], vertices[1]], WayOptions(side_color=(0, 0, 1))),
        Way([vertices[3], vertices[2]], WayOptions(side_color=(1, 0, 0))),
        Way([vertices[3], vertices[4]], WayOptions(side_color=(0, 0, 1))),
    ]
    road_network = RoadNetwork(ways, vertices)
    road_network.process()
    fig, axes = road_network.plot()
    axes.set_xlim(-14, 14)
    axes.set_ylim(-5, 10)
    save_fig(fig, axes, Path("road_network") / "connections.png", 14)


def test_check_crossing_reprocessing() -> None:
    vertices = [
        Vertex(0, -20, 0),
        Vertex(1, -10, 0),
        Vertex(2, -10, 10),
        Vertex(3, 0, 0),
        Vertex(4, 10, 0),
        Vertex(5, 10, 10),
        Vertex(6, 20, 0),
    ]
    ways = [
        Way([vertices[0], vertices[1]]),
        Way([vertices[1], vertices[2]]),
        Way([vertices[1], vertices[3]]),
        Way([vertices[3], vertices[4]]),
        Way([vertices[4], vertices[5]]),
        Way([vertices[4], vertices[6]]),
    ]
    road_network = RoadNetwork(ways, vertices)
    road_network.process()
    fig, axes = road_network.plot()
    axes.set_xlim(-20, 20)
    axes.set_ylim(-5, 10)
    save_fig(fig, axes, Path("road_network") / "crossing_and_connection.png", 20)


def test_stopline_not_added() -> None:
    vertices = [
        Vertex(0, -10, 0),
        Vertex(1, 0, 0),
        Vertex(2, 10, 0),
        Vertex(3, 20, 0),
        Vertex(4, 0, 10),
    ]
    ways = [
        Way(vertices[:-2]),
        Way(vertices[2:4]),
        Way([vertices[1], vertices[4]], WayOptions(oneway=True)),
    ]
    road_network = RoadNetwork(ways, vertices)
    road_network.process()
    fig, _ = road_network.plot()
    assert not road_network.add_stopline(ways[1])  # Way is not connected to crossing
    assert not road_network.add_stopline(ways[0], stoplineoptions=StopLineOptions(stopline=False))
    assert not road_network.add_stopline(ways[2])  # One way road that starts at crossing
    plt.close(fig)


def test_stopline() -> None:
    vertices = [Vertex(0, -10, 0), Vertex(1, 0, 0), Vertex(2, 10, 0), Vertex(3, 0, 10)]
    ways = [Way(vertices[:3]), Way([vertices[3], vertices[1]], WayOptions(oneway=True))]
    road_network = RoadNetwork(ways, vertices, RoadNetworkOptions(rightdrive=False))
    road_network.process()
    fig, axes = road_network.plot()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-5, 10)
    assert road_network.add_stopline(ways[0])
    assert road_network.add_stopline(ways[1])
    save_fig(fig, axes, Path("road_network") / "stopline.png", 10)


def test_stopsign() -> None:
    vertices = [Vertex(0, -10, 0), Vertex(1, 0, 0), Vertex(2, 10, 0), Vertex(3, 0, 10)]
    ways = [Way(vertices[:3]), Way([vertices[3], vertices[1]])]
    road_network = RoadNetwork(ways, vertices, RoadNetworkOptions(rightdrive=True))
    road_network.process()
    fig, axes = road_network.plot()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-5, 10)
    assert road_network.add_stopline(ways[1], stoplineoptions=StopLineOptions(stopsign=True))
    save_fig(fig, axes, Path("road_network") / "stopsign.png", 10)


def test_dirsign() -> None:
    vertices = [Vertex(0, -10, 0), Vertex(1, 0, 0), Vertex(2, 10, 0), Vertex(3, 0, 13)]
    ways = [Way(vertices[:3]), Way([vertices[3], vertices[1]])]
    road_network = RoadNetwork(ways, vertices)
    road_network.process()
    fig, axes = road_network.plot()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-5, 13)
    assert road_network.add_stopline(
        ways[1], stoplineoptions=StopLineOptions(stopsign=True, dir_signs=["leftright", None])
    )
    save_fig(fig, axes, Path("road_network") / "dirsign.png", 10)


def simple_crossing() -> Tuple[Figure, Axes, RoadNetwork]:
    vertices = [
        Vertex(0, -10, 0),
        Vertex(1, 0, 0),
        Vertex(2, 10, 0),
        Vertex(3, 0, 10),
        Vertex(4, 0, -10),
    ]
    ways = [Way(vertices[:3]), Way([vertices[3], vertices[1], vertices[4]])]
    road_network = RoadNetwork(ways, vertices)
    road_network.process()
    fig, axes = road_network.plot()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-10, 10)
    return fig, axes, road_network


def test_trafficlights_leftright() -> None:
    fig, axes, road_network = simple_crossing()
    road_network.add_traffic_lights()
    save_fig(fig, axes, Path("road_network") / "traffic_lights_left_right.png", 10)


def test_trafficlights_none() -> None:
    fig, _, road_network = simple_crossing()
    assert not road_network.add_traffic_lights(leftright=(False, False))
    plt.close(fig)


def test_traffic_light_with_oneway_road() -> None:
    vertices = [Vertex(0, -10, 0), Vertex(1, 0, 0), Vertex(2, 10, 0), Vertex(3, 0, 10)]
    ways = [Way(vertices[:3]), Way([vertices[1], vertices[3]], WayOptions(nlanes=1, oneway=True))]
    road_network = RoadNetwork(ways, vertices, options=RoadNetworkOptions(rightdrive=False))
    road_network.process()
    fig, axes = road_network.plot()
    road_network.add_traffic_lights(leftright=(True, False))
    axes.set_xlim(-10, 10)
    axes.set_ylim(-5, 10)
    save_fig(fig, axes, Path("road_network") / "crossing.png", 10)


def test_traffic_light_without_crossing() -> None:
    vertices = [Vertex(0, 0, 0), Vertex(1, 10, 0)]
    ways = [Way(vertices)]
    road_network = RoadNetwork(ways, vertices)
    road_network.process()
    fig, _ = road_network.plot()
    assert not road_network.add_traffic_lights()
    plt.close(fig)


def test_traffic_light_with_stoplines() -> None:
    fig, axes, road_network = simple_crossing()
    road_network.add_traffic_lights(leftright=(False, True), stoplineoptions=StopLineOptions())
    plt.close(fig)
