"""Constructing a connection, which is used to connect two ways.

Author(s): Erwin de Gelder
"""

from typing import List, Tuple

import numpy as np

from .crossing import Crossing
from .options import Options
from .vertex import Vertex
from .way import Way


class ConnectionParameters(Options):
    """All kinds of parameters of the connection are contained in this class."""

    hlength_merge: float = 5
    connection_at_start: Tuple[bool, bool] = (True, True)
    angle: float = 0
    distance: Tuple[float, float] = (0, 0)
    xoffset_left: float = 0
    yoffset_left: float = 0
    xoffset_right: float = 0
    yoffset_right: float = 0


class InvalidConnectionError(Exception):
    """Error in case an invalid connection is created.

    A connection is only valid if either the start or end of one way has the same vertex as the
    start or end of the other way.
    """

    def __init__(self) -> None:
        """Description of error."""
        super().__init__(
            "Invalid connection. Two ways do not share a vertex at their start or endpoints."
        )


class Connection:
    """Connection that is used to connect two ways with each other.

    Attributes:
        idx (int): The index of connection.
        way1 (Way): The first way of this connection.
        way2 (Way): The second way of this connection.
        parms (ConnectionParameters): All kinds of parameters that are used for processing.
        vertex (Vertex): The vertex that is shared among the two ways.
        crossing (Crossing): In case the connection is modelled as crossing.
    """

    def __init__(self, index: int, way1: Way, way2: Way) -> None:
        """Create a connection to connect two ways.

        :param index: Index of the connection.
        :way1: First way.
        :way2: Second way.
        """
        self.idx = index
        self.parms = ConnectionParameters()
        # Make sure that ways is ordered in terms of number of lanes
        if way1.options.nlanes > way2.options.nlanes:
            self.way1, self.way2 = way2, way1
        else:
            self.way1, self.way2 = way1, way2

        # Set connection reference in ways
        if self.way1.ivs[0] == self.way2.ivs[0]:
            self.way1.parms.connection.i_start = self.idx
            self.way2.parms.connection.i_start = self.idx
            self.parms.connection_at_start = (True, True)
        elif self.way1.ivs[-1] == self.way2.ivs[0]:
            self.way1.parms.connection.i_end = self.idx
            self.way2.parms.connection.i_start = self.idx
            self.parms.connection_at_start = (False, True)
        elif self.way1.ivs[0] == self.way2.ivs[-1]:
            self.way1.parms.connection.i_start = self.idx
            self.way2.parms.connection.i_end = self.idx
            self.parms.connection_at_start = (True, False)
        elif self.way1.ivs[-1] == self.way2.ivs[-1]:
            self.way1.parms.connection.i_end = self.idx
            self.way2.parms.connection.i_end = self.idx
            self.parms.connection_at_start = (False, False)
        else:
            raise InvalidConnectionError

        # Set the vertex
        if self.parms.connection_at_start[0]:
            self.vertex = self.way1.vertices[0]
        else:
            self.vertex = self.way1.vertices[-1]

        # If the angle is more than 45 degrees, than just treat connection as a crossing
        self.crossing = None
        dx1, dy1 = self.direction(0)
        dx2, dy2 = self.direction(1)
        self.parms.angle = np.arccos(
            (dx1 * dx2 + dy1 * dy2) / (np.hypot(dx1, dy1) * np.hypot(dx2, dy2))
        )
        if np.abs(self.parms.angle) <= 3 * np.pi / 4:
            self.crossing = Crossing(0, self.vertex, [self.way1, self.way2])

    def process(self) -> Tuple[List[Vertex], List[int]]:
        """Process the connection for rendering.

        :return: List of new vertices and list of indices of the crossings that need to be
                 reprocessed.
        """
        # If connection can be treated as a crossing, process the crossing and we are done
        if self.crossing is not None:
            self.crossing.process()
            return [], []

        self.check_for_offset()
        vertices, i_crossings = self.compute_distance_to_next_vertex()
        self.compute_offset()
        self.set_offset()

        return vertices, i_crossings

    def check_for_offset(self) -> None:
        """Check if we need to apply an offset to correctly connect the ways."""
        diff_nlanes = self.way2.options.nlanes - self.way1.options.nlanes
        if diff_nlanes == 1:
            # As this is checked when creating this object, we know that way2 has more lanes than
            # way1.
            offset = diff_nlanes / 2 * self.way2.options.lanewidth

            # If there is a lane going to the left, we assume that there is an extra lane to
            # go to the left. Otherwise, assume that lane needs to be added to the right.
            if self.way2.options.turnlanes is not None and (
                self.way2.options.turnlanes.startswith("left")
                or self.way2.options.turnlanes.endswith("left")
            ):
                offset *= -1
            if self.parms.connection_at_start[1]:
                self.way2.apply_offset([-offset, 0])
            else:
                self.way2.apply_offset([0, offset])

    def compute_single_distance(
        self, i_way: int, way: Way, vertices: List[Vertex], i_crossings: List[int]
    ) -> float:
        """Compute distance from a single way from starting vertex to the next one.

        :param i_way: Index of the way (0 or 1).
        :param way: The way for which to calculate the distance.
        :param vertices: List of new vertices.
        :param i_crossings: List if indices of the crossings that need to be reprocessed.
        :return: Distance from connection to the next vertex.
        """
        if self.parms.connection_at_start[i_way]:
            x1_way, y1_way = way.vertices[0].xcoordinate, way.vertices[0].ycoordinate
            x2_way, y2_way = way.vertices[1].xcoordinate, way.vertices[1].ycoordinate
        else:
            x1_way, y1_way = way.vertices[-1].xcoordinate, way.vertices[-1].ycoordinate
            x2_way, y2_way = way.vertices[-2].xcoordinate, way.vertices[-2].ycoordinate
        distance = np.hypot(x2_way - x1_way, y2_way - y1_way)
        if distance > self.parms.hlength_merge:
            xnew = self.parms.hlength_merge / distance * (x2_way - x1_way) + x1_way
            ynew = self.parms.hlength_merge / distance * (y2_way - y1_way) + y1_way
            vertices.append(Vertex(-1, xnew, ynew))
            index = 1 if self.parms.connection_at_start[i_way] else -1
            redo_start, redo_end = way.insert_vertex(vertices[-1], index)
            if redo_start:
                i_crossings.append(way.parms.crossing.i_start)
            if redo_end:
                i_crossings.append(way.parms.crossing.i_end)
            distance = self.parms.hlength_merge
        return distance

    def compute_distance_to_next_vertex(self) -> Tuple[List[Vertex], List[int]]:
        """Compute the distance from the vertex of the connection to the next vertex of the ways.

        :return: List of new vertices and list of indices of the crossings that need to be
                 reprocessed.
        """
        vertices = []  # type: List[Vertex]
        i_crossings = []  # type: List[int]
        self.parms.distance = (
            self.compute_single_distance(0, self.way1, vertices, i_crossings),
            self.compute_single_distance(1, self.way2, vertices, i_crossings),
        )
        return vertices, i_crossings

    def compute_offset(self) -> None:
        """Compute the outer points of the ways at the connection."""
        xoffsets, yoffsets = np.zeros((2, 2)), np.zeros((2, 2))
        for i_way, way in enumerate([self.way1, self.way2]):
            # Find outer points of both ways
            if self.parms.connection_at_start[i_way]:
                x1_way, y1_way = way.vertices[0].xcoordinate, way.vertices[0].ycoordinate
            else:
                x1_way, y1_way = way.vertices[-1].xcoordinate, way.vertices[-1].ycoordinate
            x_difference, y_difference = self.direction(i_way)
            x_normal = -y_difference / np.hypot(x_difference, y_difference)
            y_normal = x_difference / np.hypot(x_difference, y_difference)
            if self.parms.connection_at_start[i_way]:
                offset = way.parms.offset[0]
            else:
                offset = -way.parms.offset[-1]
            xoffsets[0, i_way] = x1_way + x_normal * (offset + way.parms.hwidth)
            yoffsets[0, i_way] = y1_way + y_normal * (offset + way.parms.hwidth)
            xoffsets[1, i_way] = x1_way + x_normal * (offset - way.parms.hwidth)
            yoffsets[1, i_way] = y1_way + y_normal * (offset - way.parms.hwidth)

        # Compute weighted average of end points.
        self.parms.xoffset_left = (
            xoffsets[0, 0] * self.parms.distance[1] + xoffsets[1, 1] * self.parms.distance[0]
        ) / np.sum(self.parms.distance)
        self.parms.xoffset_right = (
            xoffsets[1, 0] * self.parms.distance[1] + xoffsets[0, 1] * self.parms.distance[0]
        ) / np.sum(self.parms.distance)
        self.parms.yoffset_left = (
            yoffsets[0, 0] * self.parms.distance[1] + yoffsets[1, 1] * self.parms.distance[0]
        ) / np.sum(self.parms.distance)
        self.parms.yoffset_right = (
            yoffsets[1, 0] * self.parms.distance[1] + yoffsets[0, 1] * self.parms.distance[0]
        ) / np.sum(self.parms.distance)

    def set_offset(self) -> None:
        """Set the offset as parameters for the ways, such that they are plotted correctly."""
        if self.parms.connection_at_start[0]:
            self.way1.parms.connection.x_left_start = self.parms.xoffset_left
            self.way1.parms.connection.x_right_start = self.parms.xoffset_right
            self.way1.parms.connection.y_left_start = self.parms.yoffset_left
            self.way1.parms.connection.y_right_start = self.parms.yoffset_right
        else:
            self.way1.parms.connection.x_left_end = self.parms.xoffset_right
            self.way1.parms.connection.x_right_end = self.parms.xoffset_left
            self.way1.parms.connection.y_left_end = self.parms.yoffset_right
            self.way1.parms.connection.y_right_end = self.parms.yoffset_left
        if self.parms.connection_at_start[1]:
            self.way2.parms.connection.x_left_start = self.parms.xoffset_right
            self.way2.parms.connection.x_right_start = self.parms.xoffset_left
            self.way2.parms.connection.y_left_start = self.parms.yoffset_right
            self.way2.parms.connection.y_right_start = self.parms.yoffset_left
        else:
            self.way2.parms.connection.x_left_end = self.parms.xoffset_left
            self.way2.parms.connection.x_right_end = self.parms.xoffset_right
            self.way2.parms.connection.y_left_end = self.parms.yoffset_left
            self.way2.parms.connection.y_right_end = self.parms.yoffset_right

    def direction(self, i: int) -> Tuple[float, float]:
        """Compute the direction (i.e., (dx, dy)) of the way.

        :param i: index of way, either 0 or 1.
        :return: (x, y)-direction.
        """
        way = self.way1 if i == 0 else self.way2
        if self.parms.connection_at_start[i]:
            x_dir = way.vertices[1].xcoordinate - way.vertices[0].xcoordinate
            y_dir = way.vertices[1].ycoordinate - way.vertices[0].ycoordinate
        else:
            x_dir = way.vertices[-2].xcoordinate - way.vertices[-1].xcoordinate
            y_dir = way.vertices[-2].ycoordinate - way.vertices[-1].ycoordinate
        return x_dir, y_dir
