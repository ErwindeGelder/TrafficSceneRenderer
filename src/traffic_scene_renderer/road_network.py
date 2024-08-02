"""Constructing a road network.

Author(s): Erwin de Gelder
"""

from typing import List, NamedTuple, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patches
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .connection import Connection
from .crossing import Crossing, CrossingOptions
from .letters import Letters, LettersOptions
from .options import Options
from .static_objects import TurnArrow, TurnArrowOptions
from .traffic_light import TrafficLight, TrafficLightOptions
from .vertex import Vertex
from .way import Way


class CrossingInfo(NamedTuple):
    """Information on crossings."""

    crossing: Crossing
    lam: float
    crossing_at_start: bool


class StopLineOptions(Options):
    """Options for a stop line."""

    stopline: bool = True  # By default, a stop line is added when calling the add_stopline.
    stopsign: bool = False  # By default, no stop sign is added.
    dir_signs: Optional[List[Union[str, None]]] = (
        None  # Whether to add directional signs on the road.
    )
    lonoffset: float = 0  # Further offset of the line from the crossing.


class RoadNetworkOptions(Options):
    """Options for a road network."""

    rightdrive: bool = True
    face_color: Tuple[float, float, float] = (0.8, 1, 0.8)
    face_color_roundabout: Optional[Tuple[float, float, float]] = None
    overrule_colors: bool = True
    line_color: Tuple[float, float, float] = (0, 0, 0)
    marker_border_color: Tuple[float, float, float] = (1, 1, 1)
    marker_fill_color: Tuple[float, float, float] = (1, 1, 1)


class RoadNetworkParameters(Options):
    """Parameters for a road network."""

    def __init__(
        self, **kwargs: Union[List[int], List[TrafficLight], List[TurnArrow], Axes, np.ndarray]
    ) -> None:
        """Initialize the parameters for a road network."""
        self.ivs: List[int] = []
        self.figure, self.axes = plt.subplots(1, 1, figsize=(15, 7))
        self.traffic_lights: List[TrafficLight] = []
        self.turn_arrows: List[TurnArrow] = []
        self.mat_edges: np.ndarray = np.array([])
        self.n_edges_per_vertex: np.ndarray = np.array([])
        Options.__init__(self, **kwargs)


class RoadNetwork:
    """Rendering a road network.

    Attributes:
        options(RoadNetworkOptions): Options for the road network.
        ways(List[Way]): The ways that are part of the road network.
        vertices(List[Vertex]): The vertices that are part of the road network.
        parms(RoadNetworkParameters): All kinds of parameters of the road network.
        crossings(List[Crossing]): The crossings that are part of the road network.
        connections(List[Connection]): The connections that are part of the road network.
    """

    def __init__(
        self, ways: List[Way], vertices: List[Vertex], options: Optional[RoadNetworkOptions] = None
    ) -> None:
        """Initialize a road network.

        :param ways: List of ways of the roadnetwork.
        :param vertices: List of vertices that are part of the network.
        :param options: Options for the road network, see RoadNetworkOptions.
        """
        self.options = RoadNetworkOptions() if options is None else options
        if self.options.face_color_roundabout is None:
            self.options.face_color_roundabout = self.options.face_color
        self.ways = ways
        self.vertices = vertices
        self.parms = RoadNetworkParameters()
        self.parms.ivs = [vertex.idx for vertex in self.vertices]

        # Compute number of edges.
        n_edges = 0
        for way in self.ways:
            n_edges += len(way.vertices) - 1

        # Create nv-by-ne boolean matrix (nv=#vertices, ne=#edges), where the (i,j)-th entry
        # is True if the i-th vertex belongs to the j-th edge.
        self.parms.mat_edges = np.zeros((len(self.vertices), n_edges), dtype=bool)
        i_edge = 0  # Index of edge.
        for way in self.ways:
            for i_vertex1, i_vertex2 in zip(way.ivs[:-1], way.ivs[1:]):
                self.parms.mat_edges[self.parms.ivs.index(i_vertex1), i_edge] = True
                self.parms.mat_edges[self.parms.ivs.index(i_vertex2), i_edge] = True
                i_edge += 1
        self.parms.n_edges_per_vertex = np.sum(self.parms.mat_edges, axis=1)

        self.split_ways()
        self.crossings = self.construct_crossings()
        self.connections = self.construct_connections()

    def split_ways(self) -> None:
        """Split ways, such that all inner vertices of a way have degree=2.

        A vertex that contains more than 2 edges while the vertex is not at the start or
        the end of a way, the way is split, such that this vertex is only at the start
        and end of a way.
        """
        n_ways = len(self.ways)
        i_way = 0
        while i_way < n_ways:  # A while loop, because number of ways can increase in loop.
            way = self.ways[i_way]
            for i_vertex in range(1, len(way.ivs) - 1):
                if self.parms.n_edges_per_vertex[way.ivs[i_vertex]] != 2:  # noqa: PLR2004
                    self.ways.append(way.split(i_vertex))
                    n_ways += 1
                    break
            i_way += 1

    def construct_crossings(self) -> List[Crossing]:
        """Construct the crossings of the road network.

        If a vertex contains more than 2 edges, a crossing is constructed.

        :return: List of crossings.
        """
        crossings = []
        n_crossings = 0
        for i, index_vertex in enumerate(self.parms.ivs):
            if self.parms.n_edges_per_vertex[i] > 2:  # noqa: PLR2004
                ways = [way for way in self.ways if index_vertex in way.ivs]
                crossings.append(
                    Crossing(
                        n_crossings,
                        self.vertices[i],
                        ways,
                        CrossingOptions(roundabout_inner_color=self.options.face_color_roundabout),
                    )
                )
                n_crossings += 1
        return crossings

    def construct_connections(self) -> List[Connection]:
        """Construct the connections of the road network.

        A connection connects ways that are not connected using a crossing. This is the case
        if a vertex at the start or end of a way is connected to exactly two edges.

        :return: List of connections.
        """
        connections = []
        n_connections = 0
        n_crossings = len(self.crossings)
        for i_way, way in enumerate(self.ways):
            # Check for starting node and end node of way if it is connected to two vertices.
            # That would mean that it is attached to another way. Then we check if it is not
            # already processed.
            if (
                self.parms.n_edges_per_vertex[self.parms.ivs.index(way.ivs[0])] == 2  # noqa: PLR2004
                and way.parms.connection.i_start == -1
            ):
                # We found a connection, but no connection is constructed. So construct connection
                # with other way.
                for j, way2 in enumerate(self.ways):
                    if i_way != j and (way2.ivs[0] == way.ivs[0] or way2.ivs[-1] == way.ivs[0]):
                        connections.append(Connection(n_connections, way, way2))
                        if connections[-1].crossing is not None:
                            connections[-1].crossing.idx = n_crossings
                            n_crossings += 1
                        n_connections += 1
                        break
            if (
                self.parms.n_edges_per_vertex[self.parms.ivs.index(way.ivs[-1])] == 2  # noqa: PLR2004
                and way.parms.connection.i_end == -1
            ):
                # We found a connection, but no connection is constructed. So construct connection
                # with other way
                for j, way2 in enumerate(self.ways):
                    if i_way != j and (way2.ivs[0] == way.ivs[-1] or way2.ivs[-1] == way.ivs[-1]):
                        connections.append(Connection(n_connections, way, way2))
                        if connections[-1].crossing is not None:
                            connections[-1].crossing.idx = n_crossings
                            n_crossings += 1
                        n_connections += 1
                        break
        return connections

    def process(self) -> None:
        """Process the road network to make it ready for plotting."""
        # Process all crossings
        for crossing in self.crossings:
            crossing.process()

        # Process all connections
        for i, connection in enumerate(self.connections):
            new_vertices, i_crossings = connection.process()
            for vertex in new_vertices:
                vertex.idx = np.max(self.parms.ivs) + 1
                self.vertices.append(vertex)
                self.parms.ivs.append(vertex.idx)
            for crossing in self.crossings:
                if crossing.idx in i_crossings:
                    crossing.process()
            for other_connection in self.connections[:i]:
                if (
                    other_connection.crossing is not None
                    and other_connection.crossing.idx in i_crossings
                ):
                    other_connection.process()

        # Process all ways
        for way in self.ways:
            way.process()

    def plot(self) -> Tuple[Figure, Axes]:
        """Plot the road network.

        :return: plot handle.
        """
        self.parms.axes.set_facecolor(self.options.face_color)

        # Plot the crossings
        for crossing in self.crossings:
            if not crossing.parms.part_of_big_crossing:
                crossing.plot(self.parms.axes)

        # Plot connection if it is a crossing
        for connection in self.connections:
            if connection.crossing is not None:
                connection.crossing.plot(self.parms.axes)

        # Plots the roads
        for way in self.ways:
            x_plot = np.array([way.parms.left.x_data, np.flipud(way.parms.right.x_data)])
            y_plot = np.array([way.parms.left.y_data, np.flipud(way.parms.right.y_data)])
            self.parms.axes.add_patch(
                patches.Polygon(
                    np.concatenate(
                        (
                            np.reshape(x_plot, (np.prod(x_plot.shape), 1)),
                            np.reshape(y_plot, (np.prod(y_plot.shape), 1)),
                        ),
                        axis=1,
                    ),
                    color=way.options.color,
                    zorder=way.options.layer,
                )
            )
            if way.options.show_border:
                self.parms.axes.plot(
                    x_plot.T, y_plot.T, color=way.options.side_color, zorder=way.options.layer
                )
            if way.parms.plot.lines != []:
                lines = np.array(way.parms.plot.lines)
                self.parms.axes.plot(
                    [lines[:, 0], lines[:, 2]],
                    [lines[:, 1], lines[:, 3]],
                    zorder=way.options.layer,
                    color=way.options.line_color,
                )
            way.plot_markers(self.parms.axes)

        return self.parms.figure, self.parms.axes

    def find_crossing(self, way: Way) -> Union[CrossingInfo, None]:
        """Find a crossing that is connected to the given way.

        :param way: The way for which a crossing has to be found.
        :return: Information about the crossing (if found), otherwise None.
        """
        if way.parms.crossing.i_start >= 0:
            crossing = next(
                crossing
                for crossing in self.crossings
                if crossing.idx == way.parms.crossing.i_start
            )
            lam = max(way.parms.crossing.start_lambda_left, way.parms.crossing.start_lambda_right)
            return CrossingInfo(crossing=crossing, lam=lam, crossing_at_start=True)
        if way.parms.crossing.i_end >= 0:
            crossing = next(
                crossing for crossing in self.crossings if crossing.idx == way.parms.crossing.i_end
            )
            lam = max(way.parms.crossing.end_lambda_left, way.parms.crossing.end_lambda_right)
            return CrossingInfo(crossing=crossing, lam=lam, crossing_at_start=False)
        return None

    def add_stopline(
        self,
        way: Way,
        info: Optional[CrossingInfo] = None,
        stoplineoptions: Optional[StopLineOptions] = None,
    ) -> bool:
        """Add a stopping line to the given way.

        :param way: The way that needs a stopping line.
        :param info: Optional information about the crossing.
        :param stoplineoptions: Options for the optional stop sign.
        :return: Whether the stopline has been added.
        """
        if stoplineoptions is None:
            stoplineoptions = StopLineOptions()
        if not stoplineoptions.stopline:
            return False
        if info is None:
            info = self.find_crossing(way)
            if info is None:
                return False
        if info.crossing_at_start and way.options.oneway:
            return False

        offset = way.options.nlanes * way.options.lanewidth / 2
        leftoffset = -offset
        if way.options.oneway:
            rightoffset = offset
        else:
            rightoffset = (way.options.nlanes / 2 - way.options.nlanes // 2) * way.options.lanewidth
        if self.options.rightdrive and not way.options.oneway:
            leftoffset, rightoffset = -rightoffset, -leftoffset
        left = info.crossing.start_and_direction(way, leftoffset, left=True)
        right = info.crossing.start_and_direction(way, rightoffset, left=True)
        lamoffset = stoplineoptions.lonoffset / np.hypot(left.x_dir, left.y_dir)
        self.parms.axes.plot(
            [
                left.x_init + (info.lam + lamoffset) * left.x_dir,
                right.x_init + (info.lam + lamoffset) * right.x_dir,
            ],
            [
                left.y_init + (info.lam + lamoffset) * left.y_dir,
                right.y_init + (info.lam + lamoffset) * right.y_dir,
            ],
            color=way.options.line_color,
            zorder=way.options.layer,
        )

        if stoplineoptions.stopsign:
            self.add_stopsign(way, info, lonoffset=stoplineoptions.lonoffset)
        self.add_dirsigns(way, info, stoplineoptions.dir_signs)
        return True

    def add_stopsign(self, way: Way, info: CrossingInfo, lonoffset: float = 0) -> None:
        """Add a stop SIGN to a given way.

        :param way: The way that needs a stopping line.
        :param info: Information about the crossing.
        :param lonoffset: Further offset of the line from the crossing.
        """
        for ilane in range(way.options.nlanes):
            if (
                way.options.oneway
                or (ilane < way.options.nlanes / 2 and not self.options.rightdrive)
                or (ilane >= way.options.nlanes / 2 and self.options.rightdrive)
            ):
                position = info.crossing.start_and_direction(
                    way, way.options.lanewidth * (ilane - way.options.nlanes / 2 + 0.5), left=True
                )
                distance = np.hypot(position.x_dir, position.y_dir)
                lamoffset = lonoffset / distance
                width = way.options.lanewidth - 0.5
                options = LettersOptions(
                    width=width,
                    length=width,
                    face_color=self.options.marker_fill_color,
                    edge_color=self.options.marker_border_color,
                )
                road_sign = Letters(self.parms.axes, "STOP", options=options)
                road_sign.change_pos(
                    position.x_init
                    + (info.lam + lamoffset) * position.x_dir
                    + (width / 2 + 0.5) * position.x_dir / distance,
                    position.y_init
                    + (info.lam + lamoffset) * position.y_dir
                    + (width / 2 + 0.5) * position.y_dir / distance,
                    np.arctan2(-position.x_dir, -position.y_dir),
                )

    def add_dirsigns(
        self, way: Way, info: CrossingInfo, dir_signs: Union[List[Union[str, None]], None]
    ) -> None:
        """Add directional signs to a given way.

        :param way: The way that needs a stopping line.
        :param info: Information about the crossing.
        :param dir_signs: The directional signs.
        """
        if dir_signs is not None:
            for ilane, dir_sign in enumerate(dir_signs):
                if dir_sign:
                    position = info.crossing.start_and_direction(
                        way,
                        way.options.lanewidth * (way.options.nlanes / 2 - ilane - 0.5),
                        left=True,
                    )
                    distance = np.hypot(position.x_dir, position.y_dir)
                    width = way.options.lanewidth - 0.5
                    options = TurnArrowOptions(
                        face_color=self.options.marker_fill_color,
                        edge_color=self.options.marker_border_color,
                    )
                    turn_arrow = TurnArrow(self.parms.axes, direction=dir_sign, options=options)
                    turn_arrow.change_pos(
                        position.x_init
                        + info.lam * position.x_dir
                        + (width + 2.25) * position.x_dir / distance,
                        position.y_init
                        + info.lam * position.y_dir
                        + (width + 2.25) * position.y_dir / distance,
                        np.arctan2(-position.x_dir, -position.y_dir),
                    )
                    self.parms.turn_arrows.append(turn_arrow)

    def add_traffic_lights(
        self,
        crossing: Optional[Crossing] = None,
        leftright: Optional[Tuple[bool, bool]] = None,
        options: Optional[TrafficLightOptions] = None,
        stoplineoptions: Optional[StopLineOptions] = None,
    ) -> List[TrafficLight]:
        """Add the traffic lights. It is only useful to call this function after plot().

        It will add traffic lights on both sides of a way, if a way is connected to a
        crossing and the way contains lane information through the turnlanes field.

        :param crossing: Crossing for adding the traffic lights. If none, all crossings.
        :param leftright: Whether to plot light on the left/right side (default=(True, True)).
        :param options: Options for the traffic light.
        :param stoplineoptions: Options for stopline. If none provided, no stopline is added.
        :return: List of traffic lights that have been added.
        """
        traffic_lights: List[TrafficLight] = []
        if leftright is None or (leftright[0] and leftright[1]):
            location = [False, True]
        elif leftright[0]:
            location = [False]
        elif leftright[1]:
            location = [True]
        else:
            return traffic_lights
        ways = self.ways if crossing is None else crossing.ways
        for way in ways:
            info = self.find_crossing(way)
            if info is None:
                continue

            if info.crossing_at_start and way.options.oneway:
                continue

            offset = way.options.nlanes * way.options.lanewidth / 2 + 1
            for left in location:
                orientation = info.crossing.start_and_direction(way, offset, left=left)
                traffic_light = TrafficLight(self.parms.axes, options=options)
                traffic_lights.append(traffic_light)
                self.parms.traffic_lights.append(traffic_light)
                self.parms.traffic_lights[-1].change_pos(
                    orientation.x_init + info.lam * orientation.x_dir,
                    orientation.y_init + info.lam * orientation.y_dir,
                    np.arctan2(-orientation.x_dir, -orientation.y_dir),
                )

            if stoplineoptions is not None:
                self.add_stopline(way, info=info, stoplineoptions=stoplineoptions)
        return traffic_lights
