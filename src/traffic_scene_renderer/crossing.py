"""Constructing crossings.

Author(s): Erwin de Gelder
"""

import warnings
from typing import List, NamedTuple, Optional, Tuple, Union

import numpy as np
from matplotlib import patches
from matplotlib.axes import Axes

from .options import Options
from .vertex import Vertex
from .way import Way, XYData


class CornerInfo(NamedTuple):
    """Tuple for storing information on a single corner."""

    radius: float
    circle_x: float
    circle_y: float
    lambda_left: float
    lambda_right: float
    i_way2: int


class StartDirection(NamedTuple):
    """Tuple for storing information of a single arm of the crossing."""

    x_init: float
    y_init: float
    x_dir: float
    y_dir: float


class IntersectionWays(NamedTuple):
    """Tuple for storing information of two adjacent arms of a crossing."""

    x: float
    y: float
    lambda_left: float
    lambda_right: float
    way1: StartDirection
    way2: StartDirection


class CrossingOptions(Options):
    """Object containing the objects for a crossing."""

    color: Optional[Tuple[float, float, float]] = None
    edge_color: Tuple[float, float, float] = (0, 0, 0)
    n_corner_pieces: int = 20
    radius: float = -1
    zebra_color: Tuple[float, float, float] = (1, 1, 1)
    zebra_width: float = 0.8
    zebra_square_markings: bool = False
    zebra_square_markings_color: Tuple[float, float, float] = (235 / 255, 203 / 255, 108 / 255)
    zorder: int = 0
    roundabout: bool = False
    roundabout_outer_radius: float = 6
    roundabout_inner_radius: float = 2
    roundabout_inner_color: Tuple[float, float, float] = (0.8, 1, 0.8)
    default_radius: float = 2.0
    default_radius_footway: float = 0.01


class CrossingCircles(Options):
    """Parameters of a crossing concerning the circles between two ways."""

    x_data: np.ndarray = np.array([])
    y_data: np.ndarray = np.array([])
    radii: np.ndarray = np.array([])


class CrossingWayParameters(Options):
    """Parameters of a crossing concerning the ways that are connected to it."""

    at_start: np.ndarray = np.array([], dtype=bool)
    lambda_left: np.ndarray = np.array([])
    lambda_right: np.ndarray = np.array([])
    angles: np.ndarray = np.array([])


class CrossingParameters(Options):
    """Object that contains various parameters of a crossing."""

    zebra: bool = False
    processed: bool = False
    part_of_big_crossing: bool = False

    def __init__(
        self, **kwargs: Union[bool, CrossingCircles, XYData, CrossingWayParameters]
    ) -> None:
        """Initialize object that contains various parameters of a crossing.

        :param kwargs: Any parameters that are to be set can be passed via kwargs.
        """
        self.circles = CrossingCircles()
        self.plot = XYData()
        self.way = CrossingWayParameters()
        Options.__init__(self, **kwargs)


class Crossing:
    """Constructing a crossing with multiple ways.

    This object is used for drawing a crossing between two or more ways.

    Attributes:
        idx (int): The index of the crossing.
        options (CrossingOptions): Options that change the way the crossing is rendered.
        vertex (Vertex): The vertex that is shared among the different ways.
        ways (List[Way]): The ways that are connected to the crossing.
        parms (CrossingParms): Parameters of the crossing that are used for rendering.
    """

    def __init__(
        self, index: int, vertex: Vertex, ways: List[Way], options: Optional[CrossingOptions] = None
    ) -> None:
        """Initialize a crossing.

        :param index: Nonnegative index of the crossing.
        :param vertex: The vertex at which the crossing is located.
        :param ways: The ways that are connected to the crossing.
        :param options: Any options of the crossing, see CrossingOptions.
        """
        self.options = CrossingOptions() if options is None else options
        self.idx = index
        self.vertex = vertex
        self.ways = ways

        self.parms = CrossingParameters(
            zebra=np.sum([way.options.highway == "footway" for way in self.ways]) == 2,  # noqa: PLR2004
            way=CrossingWayParameters(
                at_start=np.zeros(len(self.ways), dtype=bool),
                angles=np.array([np.arctan2(*self.direction(way)) for way in self.ways]),
                lambda_left=np.zeros(len(self.ways)),
                lambda_right=np.zeros(len(self.ways)),
            ),
            circles=CrossingCircles(
                radii=np.ones(len(self.ways)) * -1,
                x_data=np.zeros(len(self.ways)),
                y_data=np.zeros(len(self.ways)),
            ),
            plot=XYData(
                x_data=np.zeros((self.options.n_corner_pieces + 2, len(self.ways))),
                y_data=np.zeros((self.options.n_corner_pieces + 2, len(self.ways))),
            ),
        )
        self._determine_color()

        # Reorder the ways, such that they are in clockwise order
        iways = np.argsort(self.parms.way.angles)  # type: np.ndarray
        self.ways = [self.ways[i] for i in iways]
        self.parms.way.angles = np.sort(self.parms.way.angles)

        # Determine if either the start or end of a way is connected to this crossing.
        for i_way, way in enumerate(self.ways):
            if way.ivs[0] == self.vertex.idx:  # Only check if at start, otherwise assume at end.
                self.parms.way.at_start[i_way] = True
                way.parms.crossing.i_start = self.idx
            else:
                way.parms.crossing.i_end = self.idx

        # Set reference to crossing correct for the ways
        # We could not do this earlier, because ways are potentially reordered
        for i_way, way in enumerate(self.ways):
            if self.parms.way.at_start[i_way]:
                way.parms.crossing.i_start = self.idx
            else:
                way.parms.crossing.i_end = self.idx

    def compute_corner_info(self, i_way1: int) -> CornerInfo:
        """Compute information of the corner.

        The returned CornerInfo contains the radius of the corner, (x,y)-coordinates
        of the circle, and the part of the way that is used by the corner (lambda_left
        and  lambda_right) as a ratio of the segment of the way that is connected to
        the crossing.

        :param i_way1: Index of first way.
        :return: A CornerInfo structure with the information.
        """
        i_way2 = i_way1 + 1 if i_way1 < len(self.ways) - 1 else 0  # Index of second way.
        angle = np.mod(self.parms.way.angles[i_way2] - self.parms.way.angles[i_way1], 2 * np.pi)
        if angle >= np.pi:
            # In this case, the radius equals the half width of the roads (assumed to be similar).
            # The center of the circle is simply the coordinate of the vertex.
            # The end of the way is used, so lambda=0.
            return CornerInfo(
                radius=self.ways[i_way1].parms.hwidth,
                circle_x=self.vertex.xcoordinate,
                circle_y=self.vertex.ycoordinate,
                lambda_left=0,
                lambda_right=0,
                i_way2=i_way2,
            )
        # Angle is less than 180 degrees
        # For the center of the corner cicle, we need to determine stuff of lines that go
        # through center.
        radius = (
            self.options.radius
            if self.parms.circles.radii[i_way1] < 0
            else self.parms.circles.radii[i_way1]
        )
        intersection = self.compute_intersection(
            i_way1,
            i_way2,
            self.ways[i_way1].parms.hwidth + radius,
            self.ways[i_way2].parms.hwidth + radius,
        )

        # Check if lambda is not larger than 1. If so, we need to decrease radius
        max_right = 0.45 if len(self.ways[i_way1].vertices) == 2 else 0.9  # noqa: PLR2004
        max_left = 0.45 if len(self.ways[i_way2].vertices) == 2 else 0.9  # noqa: PLR2004
        if intersection.lambda_right > max_right or intersection.lambda_left > max_left:
            # Compute intersection of road boundaries
            roadside = self.compute_intersection(
                i_way1, i_way2, self.ways[i_way1].parms.hwidth, self.ways[i_way2].parms.hwidth
            )
            dist = min(
                np.hypot(
                    roadside.way1.x_init + max_right * roadside.way1.x_dir - roadside.x,
                    roadside.way1.y_init + max_right * roadside.way1.y_dir - roadside.y,
                ),
                np.hypot(
                    roadside.way2.x_init + max_left * roadside.way2.x_dir - roadside.x,
                    roadside.way2.y_init + max_left * roadside.way2.y_dir - roadside.y,
                ),
            )
            radius = dist * np.tan(angle / 2)

            # Compute again the center of the circle
            intersection = self.compute_intersection(
                i_way1,
                i_way2,
                self.ways[i_way1].parms.hwidth + radius,
                self.ways[i_way2].parms.hwidth + radius,
            )
        return CornerInfo(
            radius=radius,
            circle_x=intersection.x,
            circle_y=intersection.y,
            i_way2=i_way2,
            lambda_left=intersection.lambda_left,
            lambda_right=intersection.lambda_right,
        )

    def process(self) -> None:
        """Process the crossing, i.e., create the boundaries."""
        self.options.radius = self.compute_radius()
        if self.options.roundabout:
            self.process_roundabout()
            return

        # Loop through all corners to compute the boundary location of the circle
        nways = len(self.ways)
        for i in range(nways):  # Index of first way
            corner_info = self.compute_corner_info(i)
            self.parms.circles.radii[i] = corner_info.radius
            self.parms.circles.x_data[i] = corner_info.circle_x
            self.parms.circles.y_data[i] = corner_info.circle_y
            self.parms.way.lambda_left[corner_info.i_way2] = corner_info.lambda_left
            self.parms.way.lambda_right[i] = corner_info.lambda_right

        # Loop again through all corners to compute the coordinates of the boundary of the road.
        for i in range(nways):  # Index of first way
            # Determine (x,y) coordinates of the corners
            i_way2 = i + 1 if i < nways - 1 else 0  # Index of second way
            angle = np.mod(self.parms.way.angles[i_way2] - self.parms.way.angles[i], 2 * np.pi)
            if angle >= np.pi:
                theta0 = self.parms.way.angles[i] + np.pi / 2
            else:  # Angle is less than 180 degrees
                theta0 = self.parms.way.angles[i] - np.pi / 2
            theta1 = theta0 - np.pi + angle
            theta = np.linspace(theta0, theta1, self.options.n_corner_pieces)
            self.parms.plot.x_data[1:-1, i] = (
                self.parms.circles.x_data[i] + np.sin(theta) * self.parms.circles.radii[i]
            )
            self.parms.plot.y_data[1:-1, i] = (
                self.parms.circles.y_data[i] + np.cos(theta) * self.parms.circles.radii[i]
            )

            # Determine the (x,y) coordinates of the end of the crossing.
            way1 = self.start_and_direction(i, self.ways[i].parms.hwidth, left=False)
            way2 = self.start_and_direction(i_way2, self.ways[i_way2].parms.hwidth, left=True)
            self.parms.plot.x_data[0, i] = way1.x_init + way1.x_dir * max(
                self.parms.way.lambda_left[i], self.parms.way.lambda_right[i]
            )
            self.parms.plot.y_data[0, i] = way1.y_init + way1.y_dir * max(
                self.parms.way.lambda_left[i], self.parms.way.lambda_right[i]
            )
            self.parms.plot.x_data[-1, i] = way2.x_init + way2.x_dir * max(
                self.parms.way.lambda_left[i_way2], self.parms.way.lambda_right[i_way2]
            )
            self.parms.plot.y_data[-1, i] = way2.y_init + way2.y_dir * max(
                self.parms.way.lambda_left[i_way2], self.parms.way.lambda_right[i_way2]
            )

        # Set the lambdas for the individual ways.
        for i, way in enumerate(self.ways):
            if self.parms.way.at_start[i]:
                way.parms.crossing.start_lambda_left = self.parms.way.lambda_left[i]
                way.parms.crossing.start_lambda_right = self.parms.way.lambda_right[i]
            else:
                way.parms.crossing.end_lambda_left = self.parms.way.lambda_left[i]
                way.parms.crossing.end_lambda_right = self.parms.way.lambda_right[i]

        # Set flag that this crossing is processed.
        self.parms.processed = True

    def compute_corner_info_roundabout(self, i_way: int, *, left: bool) -> CornerInfo:
        """Compute the location of the corner.

        :param i_way: The index of the way.
        :param left: Whether the corner is on the left or the right.
        :return: Information about the corner.
        """
        radius = self.options.radius
        way = self.start_and_direction(
            i_way, offset=self.ways[i_way].parms.hwidth + radius, left=left
        )
        square = way.x_dir**2 + way.y_dir**2
        linear = 2 * (
            (way.x_init - self.vertex.xcoordinate) * way.x_dir
            + (way.y_init - self.vertex.ycoordinate) * way.y_dir
        )
        constant = (
            (way.x_init - self.vertex.xcoordinate) ** 2
            + (way.y_init - self.vertex.ycoordinate) ** 2
            - (self.options.roundabout_outer_radius + radius) ** 2
        )
        lam = (-linear + np.sqrt(linear**2 - 4 * square * constant)) / (2 * square)
        return CornerInfo(
            radius=radius,
            lambda_right=lam,
            lambda_left=lam,
            i_way2=0,
            circle_x=way.x_init + way.x_dir * lam,
            circle_y=way.y_init + way.y_dir * lam,
        )

    def process_roundabout(self) -> None:
        """Process the roundabout, i.e., create the boundaries."""
        # For each corner, we will have three circles.
        self.parms.circles.radii = np.ones(len(self.ways) * 3) * -1
        self.parms.circles.y_data = np.zeros_like(self.parms.circles.radii)
        self.parms.circles.x_data = np.zeros_like(self.parms.circles.radii)

        # The plot data also includes the inner circle (last row).
        self.parms.plot.x_data = np.zeros((self.options.n_corner_pieces * 3 + 2, len(self.ways)))
        self.parms.plot.y_data = np.zeros_like(self.parms.plot.x_data)

        # Loop through all ways and compute the centers of the circles.
        nways = len(self.ways)
        for i in range(nways):
            for j, left in enumerate([False, True]):
                corner = self.compute_corner_info_roundabout(i, left=left)
                self.parms.circles.radii[i * 3 - j] = corner.radius
                self.parms.circles.x_data[i * 3 - j] = corner.circle_x
                self.parms.circles.y_data[i * 3 - j] = corner.circle_y
                if j == 0:  # This has to be done only once...
                    self.parms.way.lambda_right[i] = corner.lambda_right
                    self.parms.way.lambda_left[i] = corner.lambda_left  # Is the same.
            self.parms.circles.radii[i * 3 + 1] = self.options.roundabout_outer_radius
            self.parms.circles.x_data[i * 3 + 1] = self.vertex.xcoordinate
            self.parms.circles.y_data[i * 3 + 1] = self.vertex.ycoordinate

        # Define the borders
        for i in range(nways):
            i_way2 = i + 1 if i < nways - 1 else 0  # Index of second way

            # Determine the (x,y) coordinates of the end of the crossing.
            way1 = self.start_and_direction(i, self.ways[i].parms.hwidth, left=False)
            way2 = self.start_and_direction(i_way2, self.ways[i_way2].parms.hwidth, left=True)
            self.parms.plot.x_data[0, i] = way1.x_init + way1.x_dir * max(
                self.parms.way.lambda_left[i], self.parms.way.lambda_right[i]
            )
            self.parms.plot.y_data[0, i] = way1.y_init + way1.y_dir * max(
                self.parms.way.lambda_left[i], self.parms.way.lambda_right[i]
            )
            self.parms.plot.x_data[-1, i] = way2.x_init + way2.x_dir * max(
                self.parms.way.lambda_left[i_way2], self.parms.way.lambda_right[i_way2]
            )
            self.parms.plot.y_data[-1, i] = way2.y_init + way2.y_dir * max(
                self.parms.way.lambda_left[i_way2], self.parms.way.lambda_right[i_way2]
            )

            # Compute corners
            x_data, y_data = self.roundabout_corner(i, i_way2, big_angle=False)
            self.parms.plot.x_data[1:-1, i] = x_data
            self.parms.plot.y_data[1:-1, i] = y_data

        # Set the lambdas for the individual ways.
        for i, way in enumerate(self.ways):
            if self.parms.way.at_start[i]:
                way.parms.crossing.start_lambda_left = self.parms.way.lambda_left[i]
                way.parms.crossing.start_lambda_right = self.parms.way.lambda_right[i]
            else:
                way.parms.crossing.end_lambda_left = self.parms.way.lambda_left[i]
                way.parms.crossing.end_lambda_right = self.parms.way.lambda_right[i]

        # Set flag that this crossing is processed.
        self.parms.processed = True

    def roundabout_corner(
        self, i_way1: int, i_way2: int, *, big_angle: bool, radius: Optional[float] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Create a corner of a roundabout.

        The function is used to create the corners of a roundabout. However,
        the function can also be used to create the trajectory of a vehicle
        driving on the roundabout. If the vehicle is supposed to drive more than
        50% of the roundabout (i.e., > pi), big_angle should be set to True.

        :param i_way1: Index of the way at which the line starts.
        :param i_way2: Index of the way at which the line ends.
        :param big_angle: Whether the angle is larger than pi.
        :param radius: The radius of the circle.
        :return: (x,y) data of the line.
        """
        if radius is None:
            radius = self.options.roundabout_outer_radius
        begin_radius = self.options.radius + self.options.roundabout_outer_radius - radius
        way1 = self.start_and_direction(i_way1, 0, left=True)
        way2 = self.start_and_direction(i_way2, 0, left=True)
        x_data = np.zeros(3 * self.options.n_corner_pieces)
        y_data = np.zeros(3 * self.options.n_corner_pieces)
        theta0 = np.arctan2(-way1.y_dir, way1.x_dir)
        theta1 = np.arctan2(
            self.vertex.xcoordinate - self.parms.circles.x_data[i_way1 * 3],
            self.vertex.ycoordinate - self.parms.circles.y_data[i_way1 * 3],
        )
        theta0 = correct_angle(theta0, theta1, big_angle=big_angle)
        theta = np.linspace(theta0, theta1, self.options.n_corner_pieces)
        x_data[: self.options.n_corner_pieces] = (
            self.parms.circles.x_data[i_way1 * 3] + np.sin(theta) * begin_radius
        )
        y_data[: self.options.n_corner_pieces] = (
            self.parms.circles.y_data[i_way1 * 3] + np.cos(theta) * begin_radius
        )
        theta0 = np.mod(theta1, 2 * np.pi) - np.pi
        theta1 = np.arctan2(
            self.parms.circles.x_data[i_way2 * 3 - 1] - self.vertex.xcoordinate,
            self.parms.circles.y_data[i_way2 * 3 - 1] - self.vertex.ycoordinate,
        )
        theta0 = correct_angle(theta0, theta1, big_angle=big_angle)
        theta = np.linspace(theta0, theta1, self.options.n_corner_pieces)
        x_data[self.options.n_corner_pieces : 2 * self.options.n_corner_pieces] = (
            self.vertex.xcoordinate + np.sin(theta) * radius
        )
        y_data[self.options.n_corner_pieces : 2 * self.options.n_corner_pieces] = (
            self.vertex.ycoordinate + np.cos(theta) * radius
        )
        theta0 = np.mod(theta1, 2 * np.pi) - np.pi
        theta1 = np.arctan2(way2.y_dir, -way2.x_dir)
        theta0 = correct_angle(theta0, theta1, big_angle=big_angle)
        theta = np.linspace(theta0, theta1, self.options.n_corner_pieces)
        x_data[2 * self.options.n_corner_pieces :] = (
            self.parms.circles.x_data[i_way2 * 3 - 1] + np.sin(theta) * begin_radius
        )
        y_data[2 * self.options.n_corner_pieces :] = (
            self.parms.circles.y_data[i_way2 * 3 - 1] + np.cos(theta) * begin_radius
        )
        return x_data, y_data

    def plot(self, axes: Axes) -> None:
        """Plot the crossing on an axes.

        :param axes: The axes that is used for plotting.
        """
        x_plot = np.reshape(self.parms.plot.x_data.T, (np.prod(self.parms.plot.x_data.shape), 1))
        y_plot = np.reshape(self.parms.plot.y_data.T, (np.prod(self.parms.plot.y_data.shape), 1))
        axes.add_patch(
            patches.Polygon(
                np.concatenate((x_plot, y_plot), axis=1),
                color=self.options.color,
                zorder=self.options.zorder,
            )
        )
        if self.options.edge_color is not None:
            axes.plot(
                self.parms.plot.x_data,
                self.parms.plot.y_data,
                color=self.options.edge_color,
                zorder=self.options.zorder,
            )

        if self.options.roundabout:
            theta = np.linspace(0, 2 * np.pi, 4 * self.options.n_corner_pieces)
            x_plot = np.sin(theta) * self.options.roundabout_inner_radius + self.vertex.xcoordinate
            y_plot = np.cos(theta) * self.options.roundabout_inner_radius + self.vertex.ycoordinate
            axes.add_patch(
                patches.Polygon(
                    np.concatenate(([x_plot], [y_plot]), axis=0).T,
                    color=self.options.roundabout_inner_color,
                    zorder=self.options.zorder,
                )
            )
            axes.plot(x_plot, y_plot, color=self.options.edge_color, zorder=self.options.zorder)

        if self.parms.zebra:
            self.plot_zebra(axes)

    def plot_zebra(self, axes: Axes) -> None:
        """Plot the zebra strips.

        :param axes: The axes that is used for plotting.
        """
        # Step 1: Find the endpoints of the zebra crossing
        x_footway, y_footway, x_road, y_road = self.find_endpoints_zebra()
        if len(x_footway) != 2:  # noqa: PLR2004
            warnings.warn(
                "No zebra crossing plotted, because not 2 footways connected to crossing",
                stacklevel=2,
            )
            return
        if len(x_road) != 2:  # noqa: PLR2004
            warnings.warn(
                "No zebra crossing plotted, because not 2 roadways connected to crossing",
                stacklevel=2,
            )
            return

        # Step 2: determine coordinates of a stripe with center (0, 0).
        nstripes, dxf, dyf, xstripe, ystripe = self.compute_coordinates_zebra(
            x_footway, y_footway, x_road, y_road
        )

        # Step 3: Draw the stripes.
        for i in range(nstripes):
            x_center = (0.5 + i) / nstripes * dxf + x_footway[0]
            y_center = (0.5 + i) / nstripes * dyf + y_footway[0]
            axes.fill(x_center + xstripe, y_center + ystripe, color=self.options.zebra_color)

        # Add yellow squares
        if self.options.zebra_square_markings:
            footpath_width = np.hypot(x_road[1] - x_road[0], y_road[1] - y_road[0])
            road_width = np.hypot(dxf, dyf)
            size_square = road_width / nstripes / 2
            x_square = (
                np.array([dyf - dxf, -dyf - dxf, -dyf + dxf, dyf + dxf])
                / road_width
                * size_square
                / 2
            )
            y_square = (
                np.array([-dyf - dxf, -dyf + dxf, dyf + dxf, dyf - dxf])
                / road_width
                * size_square
                / 2
            )
            for i in range(nstripes):
                x_center = (0.5 + i) / nstripes * dxf + x_footway[0]
                y_center = (0.5 + i) / nstripes * dyf + y_footway[0]
                for direction in [1, -1]:
                    xc_square = (
                        x_center
                        + direction / road_width * (footpath_width / 2 + 2 * size_square) * dyf
                    )
                    yc_square = (
                        y_center
                        - direction / road_width * (footpath_width / 2 + 2 * size_square) * dxf
                    )
                    axes.fill(
                        x_square + xc_square,
                        y_square + yc_square,
                        color=self.options.zebra_square_markings_color,
                    )
                    if i:
                        xc_square -= (dyf * direction + dxf) / road_width * size_square
                        yc_square += (dxf * direction - dyf) / road_width * size_square
                        axes.fill(
                            x_square + xc_square,
                            y_square + yc_square,
                            color=self.options.zebra_square_markings_color,
                        )

    def find_endpoints_zebra(self) -> Tuple[List, List, List, List]:
        """Find the endpoints of the zebra crossing.

        :return: A list of the coordinates of the footway and a list of the coordinates of the
                 road.
        """
        x_footway, y_footway = [], []  # Footway
        x_road, y_road = [], []  # Road
        for i, way in enumerate(self.ways):
            max_lambda = max(self.parms.way.lambda_left[i], self.parms.way.lambda_right[i])
            start_dir = self.start_and_direction(i, 0, left=True)
            if way.options.highway == "footway":
                x_footway.append(start_dir.x_init + max_lambda * start_dir.x_dir)
                y_footway.append(start_dir.y_init + max_lambda * start_dir.y_dir)
            else:
                x_road.append(start_dir.x_init + max_lambda * start_dir.x_dir)
                y_road.append(start_dir.y_init + max_lambda * start_dir.y_dir)
        return x_footway, y_footway, x_road, y_road

    def compute_coordinates_zebra(
        self, x_footway: List, y_footway: List, x_road: List, y_road: List
    ) -> Tuple[int, float, float, np.ndarray, np.ndarray]:
        """Determine coordinates of a zebra stripe with center (0, 0).

        :param x_footway: The x-coordinates of the footway.
        :param y_footway: The y-coordinates of the footway.
        :param x_road: The x-coordinates of the road.
        :param y_road: The y-coordinates of the road.
        :return: The number of stripes, the x-direction of the footway, the y-direction of the
                 footway, the x-coordinates of a stripe with center (0, 0), and the y-coordinates
                 of a stripe with center (0, 0).
        """
        dxf, dyf = x_footway[1] - x_footway[0], y_footway[1] - y_footway[0]
        dxr, dyr = x_road[1] - x_road[0], y_road[1] - y_road[0]
        nstripes = np.round(np.hypot(dxf, dyf) / self.options.zebra_width / 2).astype(int) * 2
        width = np.hypot(dxf, dyf) / nstripes / 2
        ratio = width / np.hypot(dxr, dyr)
        xstripe = (
            np.array([dxr - dyr * ratio, dxr + dyr * ratio, -dxr + dyr * ratio, -dxr - dyr * ratio])
            / 2
        )
        ystripe = (
            np.array([dyr + dxr * ratio, dyr - dxr * ratio, -dyr - dxr * ratio, -dyr + dxr * ratio])
            / 2
        )
        return nstripes, dxf, dyf, xstripe, ystripe

    def direction(self, index_or_way: Union[int, Way]) -> Tuple[float, float]:
        """Compute the direction (i.e., (dx, dy)) of the way.

        :param index_or_way: index of way or the way itself.
        :return: (x, y)-direction.
        """
        if isinstance(index_or_way, Way):
            way = index_or_way
            crossing_at_start = way.ivs[0] == self.vertex.idx
        else:
            way = self.ways[index_or_way]
            crossing_at_start = self.parms.way.at_start[index_or_way]
        if crossing_at_start:
            difference_x = way.vertices[1].xcoordinate - way.vertices[0].xcoordinate
            difference_y = way.vertices[1].ycoordinate - way.vertices[0].ycoordinate
        else:
            difference_x = way.vertices[-2].xcoordinate - way.vertices[-1].xcoordinate
            difference_y = way.vertices[-2].ycoordinate - way.vertices[-1].ycoordinate
        return difference_x, difference_y

    def start_and_direction(
        self, index_or_way: Union[int, Way], offset: float, *, left: bool
    ) -> StartDirection:
        """Compute starting position and direction of way i, given an offset.

        :param index_or_way: index of way or the way itself.
        :param offset: the total offset
        :param left: whether offset is on left or right side (seen when pointing away from the
                     crossing center)
        :return: StartDirection structure that contains starting point of way and its direction.
        """
        # Compute the direction first.
        x_dir, y_dir = self.direction(index_or_way)
        absdxy = np.hypot(x_dir, y_dir)

        # Compute offset starting position in case it is on the left side.
        xoffset = -y_dir / absdxy * offset
        yoffset = x_dir / absdxy * offset

        # Set initial position
        if left:
            x_init, y_init = self.vertex.xcoordinate + xoffset, self.vertex.ycoordinate + yoffset
        else:
            x_init, y_init = self.vertex.xcoordinate - xoffset, self.vertex.ycoordinate - yoffset

        return StartDirection(x_init=x_init, y_init=y_init, x_dir=x_dir, y_dir=y_dir)

    def compute_intersection(
        self, i_way1: int, i_way2: int, offset1: float, offset2: float
    ) -> IntersectionWays:
        """Compute the intersection of two ways given a certain offset.

        It returns the (x,y)-coordinate of the intersection, as well as the portions
        of the segments that are used of the two ways, i.e., lambda_left and
        lambda_right.

        :param i_way1: Index of first way.
        :param i_way2: Index of second way.
        :param offset1: The offset that is to be used for the first way.
        :param offset2: The offset that is to be used for the second way.
        :return: An IntersectionWays structure.
        """
        way1 = self.start_and_direction(i_way1, offset1, left=False)
        way2 = self.start_and_direction(i_way2, offset2, left=True)

        # The intersection is located where the lines meet, so compute this using linear algebra.
        matrix = np.array([[way1.x_dir, -way2.x_dir], [way1.y_dir, -way2.y_dir]])
        vector = np.array([way2.x_init - way1.x_init, way2.y_init - way1.y_init])
        solution = np.linalg.solve(matrix, vector)
        x_intersection = way1.x_init + solution[0] * way1.x_dir
        y_intersection = way1.y_init + solution[0] * way1.y_dir
        return IntersectionWays(
            x=x_intersection,
            y=y_intersection,
            way1=way1,
            way2=way2,
            lambda_right=solution[0],
            lambda_left=solution[1],
        )

    def compute_radius(self) -> float:
        """Compute the turning radius.

        :return: turning radius.
        """
        if self.options.radius != -1:
            return self.options.radius
        if self.parms.zebra:
            return 0.01
        if all(way.options.highway == "footway" for way in self.ways):
            return self.options.default_radius_footway
        return self.options.default_radius

    def _determine_color(self) -> None:
        """Determine the color based on the connected roads."""
        if not self.parms.zebra:
            # Just copy the color of the first way that is connected to the crossing.
            self.options.color = self.ways[0].options.color
            self.options.edge_color = self.ways[0].options.side_color
        else:
            # Copy the color of the first road that is not a footpath
            for way in self.ways:
                if way.options.highway != "footway":
                    self.options.color = way.options.color
                    self.options.edge_color = way.options.side_color


def correct_angle(angle1: float, angle2: float, *, big_angle: bool) -> float:
    """Correct the first angle if needed.

    The first angle is corrected with +2pi or -2pi, such that the difference
    between the two angles is less than pi.

    :param angle1: The first angle.
    :param angle2: The second angle.
    :param big_angle: If True, than the two angles should have a bigger
                      difference than pi.
    :return: The updated first angle.
    """
    if angle1 + np.pi < angle2 and not big_angle:
        return angle1 + 2 * np.pi
    if angle1 - np.pi > angle2 and not big_angle:
        return angle1 - 2 * np.pi
    if angle1 < angle2 < angle1 + np.pi and big_angle:
        return angle1 + 2 * np.pi
    if angle1 - np.pi < angle2 < angle1 and big_angle:
        return angle1 - 2 * np.pi
    return angle1
