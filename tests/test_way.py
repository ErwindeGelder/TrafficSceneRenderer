"""Scripts for testing way.py.

Author(s): Erwin de Gelder
"""

from pathlib import Path
from typing import List, Union

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.axes import Axes

from traffic_scene_renderer import Crossing, IndexVertexError, Vertex, Way, WayOptions

from .test_static_objects import save_fig

mpl.use("Agg")


def plot_way(axes: Axes, way: Way) -> None:
    axes.plot(way.parms.left.x_data, way.parms.left.y_data, color=way.options.side_color)
    axes.plot(way.parms.right.x_data, way.parms.right.y_data, color=way.options.side_color)
    if way.parms.plot.lines:
        lines = np.array(way.parms.plot.lines)
        axes.plot(
            [lines[:, 0], lines[:, 2]], [lines[:, 1], lines[:, 3]], color=way.options.line_color
        )
    way.plot_markers(axes)


def test_way_creation() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-5, 5)
    way = Way([Vertex(0, -10, 0), Vertex(1, 10, 0)], WayOptions(line_color=(1, 0, 0)))
    way.process()
    plot_way(axes, way)
    save_fig(fig, axes, Path("way") / "straight.png", 10)
    assert str(way) == "Way[vertices=[0, 1]]"


def test_way_different_types() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-20, 20)
    axes.set_ylim(-30, 20)
    ways = (
        Way([Vertex(0, -20, 18), Vertex(1, 20, 18)], WayOptions(highway="footway")),
        Way(
            [Vertex(2, -20, 13), Vertex(3, 20, 13)],
            WayOptions(maxspeed=40, line_color=(0.5, 0, 0), side_color=(0.5, 0, 0)),
        ),
        Way(
            [Vertex(4, -20, 5), Vertex(5, 20, 5)],
            WayOptions(maxspeed=60, line_color=(0, 0.5, 0), side_color=(0, 0.5, 0)),
        ),
        Way(
            [Vertex(6, -20, -4), Vertex(7, 20, -4)],
            WayOptions(maxspeed=90, line_color=(0, 0, 0.5), side_color=(0, 0, 0.5)),
        ),
        Way(
            [Vertex(8, -20, -14), Vertex(9, 20, -14)],
            WayOptions(maxspeed=110, line_color=(0, 0.5, 0.5), side_color=(0, 0.5, 0.5)),
        ),
        Way(
            [Vertex(10, -20, -24), Vertex(11, 20, -24)],
            WayOptions(
                maxspeed=110, line_color=(0.5, 0.5, 0), side_color=(0.5, 0.5, 0), linetype="solid"
            ),
        ),
    )
    for way in ways:
        way.process()
        plot_way(axes, way)
    axes.text(-8, 18, "Footway")
    axes.text(-8, 13, "Urban road")
    axes.text(-8, 5, "Interurban road")
    axes.text(-8, -4, 'Motorway "low speed"')
    axes.text(-8, -14, 'Motorway "high speed"')
    axes.text(-8, -24, "Motorway solid line")
    save_fig(fig, axes, Path("way") / "different_ways.png", 20)


def test_split_way() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-5, 5)
    way_orig = Way(
        [Vertex(0, -10, 0), Vertex(1, 0, 0), Vertex(2, 10, 0)], WayOptions(line_color=(0, 0, 0))
    )
    way_split = way_orig.split(1)
    way_split.options.line_color = (1, 0, 0)
    way_split.options.side_color = (1, 0, 0)
    for way in (way_orig, way_split):
        way.process()
        plot_way(axes, way)
    save_fig(fig, axes, Path("way") / "split_way.png", 10)


def test_insert_and_pop_vertex() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-10, 10)
    vertex_left = Vertex(0, -10, 6)
    vertex_right = Vertex(1, 10, 6)
    way = Way([vertex_left, vertex_right], WayOptions(line_color=(0, 0, 0)))
    assert way.insert_vertex(Vertex(2, 0, 5), 1) == (False, False)
    way.process()
    plot_way(axes, way)
    assert way.pop_vertex(1) == (False, False)
    vertex_left.ycoordinate = -5
    vertex_right.ycoordinate = -5
    way.process()  # Reprocessing is necessary.
    plot_way(axes, way)
    save_fig(fig, axes, Path("way") / "insert_and_pop_vertex.png", 10)


def test_insert_and_pop_vertex_in_between_crossing() -> None:
    vertices = [
        Vertex(0, -10, 0),
        Vertex(1, 0, 0),
        Vertex(2, 0, 10),
        Vertex(3, 10, 0),
        Vertex(4, 10, 10),
        Vertex(5, 20, 0),
    ]
    ways = [
        Way([vertices[0], vertices[1]]),
        Way([vertices[1], vertices[2]]),
        Way([vertices[3], vertices[1]]),
        Way([vertices[3], vertices[4]]),
        Way([vertices[3], vertices[5]]),
    ]
    Crossing(0, vertices[1], ways[:3])
    Crossing(1, vertices[3], ways[2:])
    assert ways[2].insert_vertex(Vertex(6, 5, 1), 1) == (True, True)
    assert ways[2].pop_vertex(1) == (True, True)


def test_warning_lambda() -> None:
    vertices = [
        Vertex(0, -10, 0),
        Vertex(1, 0, 0),
        Vertex(2, 0, 10),
        Vertex(3, 1, 0),
        Vertex(4, 10, 0),
        Vertex(5, 20, 10),
        Vertex(6, 20, 0),
    ]
    ways = [
        Way([vertices[0], vertices[1]]),
        Way([vertices[1], vertices[2]]),
        Way([vertices[1], vertices[3], vertices[4]]),
        Way([vertices[4], vertices[5]]),
        Way([vertices[4], vertices[6]]),
    ]
    crossing1 = Crossing(0, vertices[1], ways[:3])
    crossing2 = Crossing(1, vertices[4], ways[2:])
    crossing1.process()
    crossing2.process()
    with pytest.warns(UserWarning):
        ways[2].get_xy()
    vertices[3].xcoordinate = 9
    crossing1.process()
    crossing2.process()
    with pytest.warns(UserWarning):
        ways[2].get_xy()


def test_vertex_invalid_index_error() -> None:
    way = Way([Vertex(0, 0, 0), Vertex(1, 10, 0)])
    try:
        way.insert_vertex(Vertex(2, 5, 0), -2)
    except IndexVertexError:
        pass
    else:
        pytest.fail("IndexInsertVertexError should be raised.")
    try:
        way.pop_vertex(0)
    except IndexVertexError:
        pass
    else:
        pytest.fail("IndexInsertVertexError should be raised.")


def test_set_nlanes() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-5, 5)
    way = Way([Vertex(0, -10, 0), Vertex(1, 10, 0)], WayOptions(line_color=(1, 0, 0), lanewidth=2))
    way.set_nlanes(4)
    way.process()
    plot_way(axes, way)
    save_fig(fig, axes, Path("way") / "fourlanes.png", 10)


def plot_way_with_offset(axes: Axes, y_orig: int, offset: Union[float, List[float]]) -> None:
    way = Way(
        [Vertex(0, -10, y_orig), Vertex(1, 0, y_orig), Vertex(2, 10, y_orig)],
        WayOptions(line_color=(0.9, 0.9, 0.9), side_color=(0.9, 0.9, 0.9)),
    )
    way.process()
    plot_way(axes, way)
    way.apply_offset(offset)
    way.process()
    way.options.side_color = (0, 0, 0)
    way.options.line_color = (0, 0, 0)
    plot_way(axes, way)


def test_apply_offset() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-12, 12)
    plot_way_with_offset(axes, 7, [0.5, 1, 2])
    plot_way_with_offset(axes, -1, [0.5, 2])
    plot_way_with_offset(axes, -8, 1)
    save_fig(fig, axes, Path("way") / "apply_offset.png", 10)


def test_road_markers() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-5, 5)
    way = Way(
        [Vertex(0, -10, 0), Vertex(1, 0, 0), Vertex(2, 10, 0)],
        WayOptions(line_color=(1, 0, 0), turnlanes="none|right", marker_border_color=(0, 0, 0.5)),
    )
    way.process()
    plot_way(axes, way)
    way.plot_markers(axes)
    save_fig(fig, axes, Path("way") / "way_with_markers.png", 10)


def test_warning_markers_vs_nr_of_lanes() -> None:
    fig, axes = plt.subplots()
    way = Way([Vertex(0, -10, 0), Vertex(1, 10, 0)], WayOptions(turnlanes="through", nlanes=2))
    with pytest.warns(UserWarning):
        way.plot_markers(axes)
    plt.close(fig)


def test_get_n_markers_without_xy_data() -> None:
    way = Way([Vertex(0, -10, 0), Vertex(1, 10, 0)], WayOptions(marker_interval=100))
    assert way.get_n_markers() == 1


def test_plot_marker_single_lane() -> None:
    fig, axes = plt.subplots()
    axes.set_xlim(-10, 10)
    axes.set_ylim(-5, 5)
    way = Way(
        [Vertex(0, -10, 0), Vertex(1, 10, 0)],
        WayOptions(line_color=(1, 0, 0), n_markers=8, marker_border_color=(0, 0, 0.5)),
    )
    way.plot_markers_lane(axes, 1, "through")
    way.plot_markers_lane(axes, 0, "rev_through")
    way.process()
    plot_way(axes, way)
    save_fig(fig, axes, Path("way") / "way_with_reversed_markers.png", 10)


def test_compute_position_markers() -> None:
    way = Way(
        [Vertex(0, -10, 0), Vertex(1, 10, 0)],
        WayOptions(line_color=(1, 0, 0), n_markers=2, nlanes=1),
    )
    easting, northing, angle = way.compute_position_markers(0)
    assert easting[0] == pytest.approx(-5.0)
    assert easting[1] == pytest.approx(5.0)
    assert northing[0] == pytest.approx(0.0)
    assert northing[1] == pytest.approx(0.0)
    assert angle[0] == pytest.approx(np.pi / 2)
    assert angle[1] == pytest.approx(np.pi / 2)


def test_non_unique_vertex_ids() -> None:
    with pytest.warns(UserWarning):
        Way([Vertex(0, 0, 0), Vertex(0, 10, 0)])
