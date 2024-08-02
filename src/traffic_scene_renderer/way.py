"""Constructing ways.

Author(s): Erwin de Gelder
"""

import copy
import warnings
from typing import List, Optional, Tuple, Union

import numpy as np
from matplotlib.axes import Axes

from .options import Options
from .static_objects import TurnArrow, TurnArrowOptions
from .vertex import Vertex

DEFAULT_LANE_WIDTH = 2.8  # [m]
FOOTWAY_LANE_WIDTH = 1.5  # [m]
INTERURBAN_LANE_WIDTH = 3  # [m]
HIGHWAY_LANE_WIDTH = 3.5  # [m] Default for Dutch motorways
MAX_URBAN_SLOW_SPEED = 30
MAX_URBAN_SPEED = 50
MAX_INTERURBAN_SPEED = 80
MAX_MOTORWAY_SLOW_SPEED = 100


class WayOptions(Options):
    """The default values of the options of a way object."""

    highway: Optional[str] = None
    maxspeed: Optional[float] = None
    nlanes: int = 0
    lanewidth: float = -1
    layer: int = 0
    oneway: bool = False
    turnlanes: Optional[str] = None
    linetype: Optional[str] = None
    line_color: Tuple[float, float, float] = (1, 1, 1)
    marker_border_color: Tuple[float, float, float] = (1, 1, 1)
    show_border: bool = True
    marker_interval: float = 10
    n_markers: Optional[int] = None
    marker_fill_color: Tuple[float, float, float] = (1, 1, 1)
    color: Tuple[float, float, float] = (-1, -1, -1)
    side_color: Tuple[float, float, float] = (-1, -1, -1)
    line_interval: float = -1
    line_length: float = -1

    def __init__(self, **kwargs: Union[bool, float, str, Tuple[float, float, float]]) -> None:
        """Create a container for all options for a way.

        :param kwargs: Use kwargs to set any option other then the default option.
        """
        Options.__init__(self, **kwargs)
        if self.lanewidth == -1:
            self.lanewidth = self._compute_lane_width()
        if self.nlanes == 0:
            self.nlanes = self._compute_nlanes()
        if self.line_interval == -1 or self.line_length == -1:
            # They both need to be set, otherwise they are calculated.
            self.line_interval, self.line_length = self._compute_line_info()
        if self.color == (-1, -1, -1):
            self.color = self._determine_color()
        if self.side_color == (-1, -1, -1):
            self.side_color = self._determine_side_color()

    def _compute_lane_width(self) -> float:
        """Determine the lanewidth, based on the maxspeed.

        :return: lane width.
        """
        if self.maxspeed is None:
            if self.highway == "footway":
                return FOOTWAY_LANE_WIDTH
            return DEFAULT_LANE_WIDTH
        if self.maxspeed <= MAX_URBAN_SPEED:
            return DEFAULT_LANE_WIDTH
        if self.maxspeed <= MAX_INTERURBAN_SPEED:
            return INTERURBAN_LANE_WIDTH
        # For simplicity, assume highway
        return HIGHWAY_LANE_WIDTH

    def _compute_nlanes(self) -> int:
        """Determine the number of lanes; always 2, unless it is a footway (then 1).

        :return: Number of lanes.
        """
        if self.highway == "footway":
            return 1
        return 2  # Assume it is a bidirectional road

    def _compute_line_info(self) -> Tuple[float, float]:
        """Compute line information.

        :return: line interval and line length.
        """
        if self.maxspeed is None or self.maxspeed <= MAX_URBAN_SLOW_SPEED:
            line_interval, line_length = 3.0, 1.0
        elif self.maxspeed <= MAX_URBAN_SPEED:
            line_interval, line_length = 5.0, 5 / 3
        elif self.maxspeed <= MAX_INTERURBAN_SPEED:
            line_interval, line_length = 8.0, 8 / 3
        elif self.maxspeed <= MAX_MOTORWAY_SLOW_SPEED:
            line_interval, line_length = 10.0, 10 / 3
        else:
            line_interval, line_length = 12.0, 4.0

        if self.linetype == "solid":
            # It is a dirty solution, but we make the line interval similar to the line length.
            return line_interval, line_interval
        return line_interval, line_length

    def _determine_color(self) -> Tuple[float, float, float]:
        """Determine the color of the road.

        :return: RGB tuple.
        """
        if self.highway == "footway":
            return 1, 0.9, 0.8
        return 0.8, 0.8, 0.8

    def _determine_side_color(self) -> Tuple[float, float, float]:
        """Determine the side color of the road.

        :return: RGB tuple.
        """
        if self.highway == "footway":
            return 0.8, 1, 0.8
        return 0, 0, 0


class WayConnection(Options):
    """Class containing parameters of a way object concerning its connections."""

    i_start: int = -1
    i_end: int = -1
    x_left_start: float = 0
    x_right_start: float = 0
    y_left_start: float = 0
    y_right_start: float = 0
    x_left_end: float = 0
    x_right_end: float = 0
    y_left_end: float = 0
    y_right_end: float = 0


class WayCrossing(Options):
    """Class containing parameters of a way object concerning its crossings."""

    i_start: int = -1
    i_end: int = -1
    start_lambda_left: float = 0
    start_lambda_right: float = 0
    end_lambda_left: float = 0
    end_lambda_right: float = 0


class XYData(Options):
    """Class containing xy-data that is used for way objects."""

    def __init__(self, **kwargs: np.ndarray) -> None:
        """Create an object with x_data and y_data stored in numpy array.

        :param kwargs: x_data and y_data may be already provided.
        """
        self.x_data = np.array([])
        self.y_data = np.array([])
        Options.__init__(self, **kwargs)


class WayPlotData(Options):
    """Class containing plot data of a way object."""

    i_interval: int = 0

    def __init__(self, **kwargs: Union[List, List[TurnArrow], np.ndarray]) -> None:
        """Create an object to store all plotting information of a way.

        :param kwargs: Any parameters that are to be set can be passed via kwargs.
        """
        self.lines: List = []
        self.arrows: List[TurnArrow] = []  # For turning arrows.
        self.lengths = np.array([])
        self.xyline = np.array([])
        Options.__init__(self, **kwargs)


class WayParameters(Options):
    """Class containing parameters of a way object."""

    hwidth: float = 0

    def __init__(
        self, **kwargs: Union[float, List[float], WayConnection, WayCrossing, XYData, WayPlotData]
    ) -> None:
        """Create an object to store all parameters for a way.

        :param kwargs: Any parameters that are to be set can be passed via kwargs.
        """
        self.offset: List[float] = []
        self.connection: WayConnection = WayConnection()
        self.crossing: WayCrossing = WayCrossing()
        self.left: XYData = XYData()
        self.right: XYData = XYData()
        self.plot: WayPlotData = WayPlotData()
        Options.__init__(self, **kwargs)


class IndexVertexError(Exception):
    """Error to be raised in case the index of the vertex is invalid."""

    def __init__(self, index: int, maxindex: int) -> None:
        """Description of error."""
        super().__init__(f"Index should be in range 1 to {maxindex}, but is {index}'.")


class Way:
    """A way of a road network.

    Attributes:
        options (WayOptions): All options. For a detailed description, see above.
        vertices (List[Vertex]): All vertices of the way.
        ivs (List[int]): The indices of all vertices of the way.
        parms (WayParameters): All parameters that are used for rendering the way.
    """

    def __init__(self, vertices: List[Vertex], options: Optional[WayOptions] = None) -> None:
        """Initializes a Way object.

        :param vertices: List of vertices of the way.
        :param options: possible options
        """
        self.options = WayOptions() if options is None else options
        self.vertices = vertices

        # Make list of indices of the vertices.
        self.ivs = [v.idx for v in self.vertices]

        # Check if vertices have a unique ID.
        if len(self.ivs) != len(set(self.ivs)):
            warnings.warn(
                "The ID of the vertices of this way are not unique. "
                "This may lead to strange results.",
                stacklevel=2,
            )

        self.parms = WayParameters()
        self.parms.offset = [0.0 for _ in self.ivs]  # Offset per node, right is positive.
        self._compute_hwidth()

    def split(self, index: int) -> "Way":
        """Split way into two ways.

        :param index: index of vertex that belong to new way.
        :return: way that is cut off.
        """
        way = copy.deepcopy(self)
        self.vertices = self.vertices[: index + 1]
        way.vertices = way.vertices[index:]
        self.ivs = self.ivs[: index + 1]
        way.ivs = way.ivs[index:]
        self.parms.offset = self.parms.offset[: index + 1]
        way.parms.offset = way.parms.offset[index:]
        return way

    def insert_vertex(self, vertex: Vertex, index: int) -> Tuple[bool, bool]:
        """Insert a vertex.

        :param vertex: Vertex to be inserted.
        :param index: Index of vertex of the way where the given index will be inserted before.
        :return: Two booleans, tellings whether the start or end crossings need to be processed
                 again.
        """
        # Convert index to a positive number on the interval [0, len(self.ivs)-1).
        # This is done, such that the index refers to the index that the new vertex will have
        # (this is not the case if index=-1).
        if index < 0:
            index += len(self.ivs)
        if index == 0 or abs(index) >= len(self.ivs):
            raise IndexVertexError(index, len(self.ivs) - 1)
        self.vertices.insert(index, vertex)
        self.ivs.insert(index, vertex.idx)
        dist1 = np.hypot(
            self.vertices[index - 1].xcoordinate - self.vertices[index].xcoordinate,
            self.vertices[index - 1].ycoordinate - self.vertices[index].ycoordinate,
        )
        dist2 = np.hypot(
            self.vertices[index].xcoordinate - self.vertices[index + 1].xcoordinate,
            self.vertices[index].ycoordinate - self.vertices[index + 1].ycoordinate,
        )
        self.parms.offset.insert(
            index,
            (self.parms.offset[index - 1] * dist2 + self.parms.offset[index] * dist1)
            / (dist1 + dist2),
        )
        process_start_again = False
        process_end_again = False
        if index == 1 and self.parms.crossing.i_start >= 0:
            process_start_again = True
        if index == len(self.ivs) - 2 and self.parms.crossing.i_end >= 0:
            process_end_again = True
        return process_start_again, process_end_again

    def pop_vertex(self, index: int) -> Tuple[bool, bool]:
        """Remove a vertex from this road.

        Note that this vertex cannot be at the start or at the end of the way.

        :param index: Index of vertex to be removed.
        :return: Two booleans, tellings whether the start or end crossings need to be processed
                 again.
        """
        # Check if index is correct.
        if index == 0 or abs(index) >= len(self.ivs) - 1:
            raise IndexVertexError(index, len(self.ivs) - 1)

        # Check if crossing needs to be processed again. This is the case when the vertex
        # is used for constructing the crossing (i.e. the second or second-last vertex).
        process_start_again = False
        process_end_again = False
        if index % len(self.ivs) == 1 and self.parms.crossing.i_start >= 0:
            process_start_again = True
        if index % len(self.ivs) == len(self.ivs) - 2 and self.parms.crossing.i_end >= 0:
            process_end_again = True

        # Remove vertex
        self.vertices.pop(index)
        self.ivs.pop(index)
        self.parms.offset.pop(index)
        return process_start_again, process_end_again

    def get_xy(self) -> np.ndarray:
        """Get the x-y coordinates of the vertices.

        :return: np.array with x,y coordinates
        """
        # Get (x,y) coordinates. First and last coordinates may differ, depending on whether
        # they are attached to a crossing/connection.
        xy_data = np.array([[v.xcoordinate, v.ycoordinate] for v in self.vertices])
        xy_tmp = xy_data[-2].copy()  # We need this later, but xy[-2] might change, so we store it.
        if self.parms.crossing.i_start >= 0:
            lamb = max(
                self.parms.crossing.start_lambda_left, self.parms.crossing.start_lambda_right
            )
            if lamb > 1:
                warnings.warn(
                    f"Lambda > 1, this will result in faulty roads! (lambda = {lamb:.2f})",
                    stacklevel=2,
                )
            xy_data[0] = xy_data[0] + lamb * (xy_data[1] - xy_data[0])
        if self.parms.crossing.i_end >= 0:
            lamb = max(self.parms.crossing.end_lambda_left, self.parms.crossing.end_lambda_right)
            if lamb > 1:
                warnings.warn(
                    f"Lambda > 1, this will result in faulty roads! (lambda = {lamb:.2f})",
                    stacklevel=2,
                )
            xy_data[-1] = xy_data[-1] + lamb * (xy_tmp - xy_data[-1])

        # Apply offset
        return apply_offset(xy_data, self.parms.offset)

    def set_nlanes(self, nlanes: int) -> None:
        """Set the number of lanes of the way.

        This function needs to be used instead of setting directly self.options.nlanes,
        because this function will recalculate the hwidth.

        :param nlanes: The number of lanes.
        """
        self.options.nlanes = nlanes
        self._compute_hwidth()

    def process(self) -> None:
        """Process way to make it suitable for plotting.

        Note that corresponding crossings need to be processed before processing the road.
        """
        xy_data = self.get_xy()
        xy_left = apply_offset(xy_data, self.parms.hwidth)
        xy_right = apply_offset(xy_data, -self.parms.hwidth)
        self.parms.left.x_data, self.parms.left.y_data = xy_left[:, 0], xy_left[:, 1]
        self.parms.right.x_data, self.parms.right.y_data = xy_right[:, 0], xy_right[:, 1]

        # Check if we need to correct final point, because of a connection.
        if self.parms.connection.i_start >= 0 and self.parms.crossing.i_start == -1:
            self.parms.left.x_data[0] = self.parms.connection.x_left_start
            self.parms.right.x_data[0] = self.parms.connection.x_right_start
            self.parms.left.y_data[0] = self.parms.connection.y_left_start
            self.parms.right.y_data[0] = self.parms.connection.y_right_start
        if self.parms.connection.i_end >= 0 and self.parms.crossing.i_end == -1:
            self.parms.left.x_data[-1] = self.parms.connection.x_left_end
            self.parms.right.x_data[-1] = self.parms.connection.x_right_end
            self.parms.left.y_data[-1] = self.parms.connection.y_left_end
            self.parms.right.y_data[-1] = self.parms.connection.y_right_end

        # Generate lines
        if (
            self.options.nlanes is not None
            and self.options.nlanes > 1
            and self.options.linetype != "none"
        ):
            self.parms.plot.lines = []  # Empty list, even if process() is called again.
            for ilane in range(1, self.options.nlanes):
                self.generate_lane_lines(ilane, xy_data)

    def generate_lane_lines(self, ilane: int, xy_data: np.ndarray) -> None:
        """Compute the coordinates of the line markers of a specific lane.

        The start and the end of road will have a line of half the specified length, e.g.
        # |-   --   --   --   --   -|  (e.g., line_length=2, line_interval=5, nlines=6).
        The line information is stored in self.parms.plot.lines. Hence, nothing is returned.

        :param ilane: Index of the lane, ranging from 1 to the number of lanes minus 1.
        :param xy_data: (x,y) data of the lane, obtained using self.get_xy().
        """
        self.parms.plot.xyline = apply_offset(
            xy_data, self.options.lanewidth * (ilane - self.options.nlanes / 2)
        )
        self.parms.plot.lengths = np.hypot(
            np.diff(self.parms.plot.xyline[:, 0]), np.diff(self.parms.plot.xyline[:, 1])
        )
        total_length = np.sum(self.parms.plot.lengths)
        nlines = np.round(total_length / self.options.line_interval).astype(int) + 1
        interval_ratio = total_length / ((nlines - 1) * self.options.line_interval)

        # Store line in array: [e0, n0, e1, n1] (e=easting, n=northing)
        line = [self.parms.plot.xyline[0, 0], self.parms.plot.xyline[0, 1], 0, 0]
        distance = 0.0  # Distance from starting point
        self.parms.plot.i_interval = 0
        for i in range(nlines):
            # Compute end point of line
            if i in (0, nlines - 1):
                distance += self.options.line_length * interval_ratio / 2
            else:
                distance += self.options.line_length * interval_ratio

            line[2], line[3], distance = self.point_on_line(distance)
            self.parms.plot.lines.append(line.copy())

            # Compute starting point of next line
            if i == nlines - 1:  # No need to do this when there is no next line
                break
            distance += (self.options.line_interval - self.options.line_length) * interval_ratio
            line[0], line[1], distance = self.point_on_line(distance)

    def point_on_line(self, distance: float) -> Tuple[float, float, float]:
        """Compute the point on the line that is a specified distance away from the start.

        The line is defined by the coordinates of self.parms.plot.xy_line. It is
        assumed that this function is only called with increasing distance. If
        this is not the case, some weird results can be produced. If the distance
        is smaller, the index of the interval (self.parms.plot.i_interval) needs
        to be reset to 0.

        :param distance: The distance to the next point.
        :return: The easting and northing position of the new point on the line and the updated
                 distance.
        """
        while distance > self.parms.plot.lengths[self.parms.plot.i_interval]:
            if self.parms.plot.i_interval + 1 == len(self.parms.plot.lengths):
                break
            distance -= self.parms.plot.lengths[self.parms.plot.i_interval]
            self.parms.plot.i_interval += 1
        d_scaled = distance / self.parms.plot.lengths[self.parms.plot.i_interval]
        easting = (
            self.parms.plot.xyline[self.parms.plot.i_interval, 0] * (1 - d_scaled)
            + self.parms.plot.xyline[self.parms.plot.i_interval + 1, 0] * d_scaled
        )
        northing = (
            self.parms.plot.xyline[self.parms.plot.i_interval, 1] * (1 - d_scaled)
            + self.parms.plot.xyline[self.parms.plot.i_interval + 1, 1] * d_scaled
        )
        return easting, northing, distance

    def apply_offset(self, offset: Union[float, List[float]]) -> None:
        """Apply offset to the (x,y) data of the vertices of this way.

        :param offset: Single offset or list of offsets. In case of list of offsets, there are
                       two options.
                       - A list of 2 floats defining the offsets at both ends. Using linear
                         interpolation, the offsets at the other nodes are determined.
                       - A list of N floats. In this case, node i will have an offset of
                         'offset[i]'.
        """
        if isinstance(offset, List):
            if len(offset) == 2:  # noqa: PLR2004
                xy_data = [[vertex.xcoordinate, vertex.ycoordinate] for vertex in self.vertices]
                distance = np.array(
                    [
                        np.hypot(
                            xy_data[i][0] - xy_data[i - 1][0], xy_data[i][1] - xy_data[i - 1][1]
                        )
                        for i in range(1, len(xy_data))
                    ]
                )
                cumlative_dist = np.concatenate(([0], np.cumsum(distance)))
                new_offset = offset[0] + cumlative_dist / cumlative_dist[-1] * (
                    offset[1] - offset[0]
                )
            else:
                new_offset = offset
        else:
            new_offset = [1 for _ in range(len(self.parms.offset))]
        for i in range(len(self.parms.offset)):
            self.parms.offset[i] += new_offset[i]

    def plot_markers(self, axes: Axes) -> None:
        """Plot the markers.

        :param axes: The axes that are used for plotting.
        """
        # If we have no futher information about the lanes, we can't plot any markers.
        if self.options.turnlanes is None:
            return

        # Get directions. If the number of directions is different than the number of lanes,
        # then return.
        directions = self.options.turnlanes.split("|")
        if len(directions) != self.options.nlanes:
            warnings.warn(
                "Does not know how to plot markers: number of directions is different "
                "from number of lanes",
                stacklevel=2,
            )
            return

        xy_data = self.get_xy()
        self.get_n_markers(xy_data)  # This will set self.option.n_markers if not already set.
        for ilane, direction in enumerate(directions):
            self.plot_markers_lane(axes, ilane, direction, xy_data)

    def get_n_markers(self, xy_data: Optional[np.ndarray] = None) -> int:
        """Return the number of markers that are to be plotted.

        This function will set the option n_markers. If this option is already set,
        the function simply returns this value.

        :param xy_data: (x,y)-coordinates of the road. If not provided, it will be computed.
        :return: Number of markers.
        """
        if self.options.n_markers is not None:
            return self.options.n_markers

        if xy_data is None:
            xy_data = self.get_xy()
        lengths = np.hypot(np.diff(xy_data[:, 0]), np.diff(xy_data[:, 1]))
        total_length = np.sum(lengths)
        n_markers = np.floor(total_length / self.options.marker_interval).astype(int)
        if n_markers == 0:
            n_markers = 1
        self.options.n_markers = n_markers
        return n_markers

    def plot_markers_lane(
        self, axes: Axes, ilane: int, direction: str, xy_data: Optional[np.ndarray] = None
    ) -> None:
        """Plot the markers for a single lane.

        :param axes: The axes that are used for plotting.
        :param ilane: The index of the lane.
        :param direction: The direction of the lane marker, e.g., 'left', 'right', 'leftright'.
        :param xy_data: (x,y)-coordinates of the road. If not provided, it will be computed.
        :return:
        """
        if direction == "none" or self.options.n_markers == 0 or not direction:
            return

        if xy_data is None:
            xy_data = self.get_xy()

        easting, northing, angle = self.compute_position_markers(ilane, xy_data)
        options = TurnArrowOptions(
            edge_color=self.options.marker_border_color, face_color=self.options.marker_fill_color
        )
        for i in range(self.get_n_markers()):
            # Create static object
            if direction.startswith("rev_"):
                angle[i] += np.pi
                turn_arrow = TurnArrow(axes, direction=direction[4:], options=options)
            else:
                turn_arrow = TurnArrow(axes, direction=direction, options=options)
            turn_arrow.change_pos(easting[i], northing[i], angle[i])
            self.parms.plot.arrows.append(turn_arrow)

    def compute_position_markers(
        self, ilane: int, xy_data: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Compute the positions of the markers of a single lane.

        :param ilane: The index of the lane.
        :param xy_data: (x,y)-coordinates of the road. If not provided, it will be computed.
        :return: Numpy arrays of the easting, northing, and angle of the markers.
        """
        if xy_data is None:
            xy_data = self.get_xy()

        xyline = apply_offset(
            xy_data, self.options.lanewidth * ((self.options.nlanes - 1) / 2 - ilane)
        )
        lengths = np.hypot(np.diff(xyline[:, 0]), np.diff(xyline[:, 1]))
        total_length = np.sum(lengths)
        marker_interval = total_length / self.options.n_markers
        distance = 0  # Distance from starting point
        i_interval = 0
        easting = np.zeros(self.get_n_markers())
        northing = np.zeros(self.get_n_markers())
        angle = np.zeros(self.get_n_markers())
        for i in range(self.get_n_markers()):
            if i == 0:
                # First and last line have half of the normal length.
                distance += marker_interval / 2
            else:
                distance += marker_interval
            while i_interval < len(lengths) and distance > lengths[i_interval]:
                distance -= lengths[i_interval]
                i_interval += 1
            d_scaled = distance / lengths[i_interval]
            easting[i] = (
                xyline[i_interval, 0] * (1 - d_scaled) + xyline[i_interval + 1, 0] * d_scaled
            )
            northing[i] = (
                xyline[i_interval, 1] * (1 - d_scaled) + xyline[i_interval + 1, 1] * d_scaled
            )
            angle[i] = np.arctan2(
                xyline[i_interval + 1, 0] - xyline[i_interval, 0],
                xyline[i_interval + 1, 1] - xyline[i_interval, 1],
            )
        return easting, northing, angle

    def _compute_hwidth(self) -> None:
        """Compute half of the road width.

        Parameter is set at self.parms.hwidth, so nothing is returned.
        """
        # Compute half width of the road (i.e., distance from centerline to boundary of the road)
        self.parms.hwidth = self.options.lanewidth * self.options.nlanes / 2

    def __str__(self) -> str:
        """For debugging purposes, it can be nice to see which vertices are used for this road.

        :return: Short description of the way.
        """
        return f"Way[vertices={self.ivs}]"


def apply_offset(xy_data: np.ndarray, offset: Union[float, List[float]]) -> np.ndarray:
    """Apply an offset to a line defined by the xy-coordinates.

    :param xy_data: N-by-2 array with (x,y)-coordinates.
    :param offset: Single offset or list of offsets. In case of list of offsets, there are
                   two options.
                   - A list of 2 floats defining the offsets at both ends.
                     Using linear interpolation, the offsets at the other nodes are determined.
                   - A list of N floats. In this case, node i will have an offset of 'offset[i]'.
    :return: N-by-2 array with new (x,y)-coordinates.
    """
    # Determine the offsets, such that it is a list with N floats.
    if isinstance(offset, list):
        if len(offset) == 2:  # noqa: PLR2004
            distances = np.array(
                [
                    np.hypot(xy_data[i, 0] - xy_data[i - 1, 0], xy_data[i, 1] - xy_data[i - 1, 1])
                    for i in range(1, xy_data.shape[0])
                ]
            )
            cumulative_dist = np.concatenate(([0], np.cumsum(distances)))
            off = offset[0] + cumulative_dist / cumulative_dist[-1] * (offset[1] - offset[0])
        else:
            off = offset
    else:
        off = np.ones(xy_data.shape[0]) * offset

    direction = np.zeros_like(xy_data)
    xy_new = np.zeros_like(xy_data)
    for i in range(xy_data.shape[0]):
        direction[i, :] = xy_data[max(i, 1), :] - xy_data[max(i - 1, 0), :]
        direction[i, :] /= np.sqrt(np.dot(direction[i, :], direction[i, :]))

    # Compute the angle (alpha) between two different sections. We need the tan(alpha/2),
    # which is computed using the formula tan(alpha/2) = sqrt(tan_halpha_squared), with
    # tan_halpha_squared = (1-cos(alpha)) / (1+cos(alpha)).
    cosines = np.concatenate((np.sum(direction[:-1, :] * direction[1:, :], axis=1), [1]))
    tan_halpha_squared = (1 - cosines) / (1 + cosines)  # It is assumed that cosines is not -1 !
    tan_halpha_squared[tan_halpha_squared < 0] = 0
    sign = np.concatenate(
        (np.sign(direction[:-1, 1] * direction[1:, 0] - direction[:-1, 0] * direction[1:, 1]), [1])
    )
    extra = np.sqrt(tan_halpha_squared) * sign

    # Apply offset
    xy_new[:, 0] = xy_data[:, 0] + (direction[:, 0] * extra - direction[:, 1]) * off
    xy_new[:, 1] = xy_data[:, 1] + (direction[:, 1] * extra + direction[:, 0]) * off
    return xy_new
