"""Airport baggage transport vehicle.

Author(s): Erwin de Gelder
"""

import numpy as np
from matplotlib.axes import Axes

from .car import Car, CarOptions
from .path_follower import PathFollower
from .polygon import Polygon
from .trailer import Trailer, TrailerOptions
from .utilities import hsl2rgb, rgb2hsl


class AirportVehicleOptions(CarOptions):
    """The default values of the options of a airport vehicle.

    The following list shows the options (within parentheses default values):
        length (2.9): The length of the truck.
        width (1.36): The width of the truck.
        length_trailer_a (1.0): Length of the first part of the trailer.
        length_trailer_b (2.0): Length of the second part of the trailer.
        width_trailer (1.5): Width of the trailer.
        line_width (1): The line width for plotting the vehicle.
        x_position_init (0): The initial horizontal position of the vehicle.
        y_position_init (0): The initial vertical position of the vehicle.
        color ((1, .8, .05)): Main color of the vehicle.
        color2 (None): Secondary color of the vehicle. If None, a bit darker than color.
        color3 (None): Color of trailer. If None, same as color.
        window_color (.6, .85, .92): Color of the windscreen.
        edgecolor ((0, 0, 0)): Color of the edges
        n_trailers (0): Number of trailers
        luminance_diff (0.3): If color2 is not set, specify luminance difference
            between color2 and color.
        layer (2): The layer in which the ambulance will be plotted.
    """

    length: float = 2.9
    width: float = 1.36
    length_trailer_a: float = 1.0
    length_trailer_b: float = 2.0
    width_trailer: float = 1.5
    color: tuple[float, float, float] = (1.0, 0.8, 0.05)
    color2: tuple[float, float, float] | None = None
    color3: tuple[float, float, float] | None = None
    window_color: tuple[float, float, float] = (0.6, 0.85, 0.92)
    n_trailers: int = 0
    luminance_diff: float = -0.3


class AirportVehicle(Car):
    """Plot an airport vehicle on the scene.

    Create an airport vehicle object using AirportVehicle(axes, options).

    Attributes:
        options (AirportVehicleOptions): All options. For a detailed description, see above.
        axes (Axes): The axes that is used for plotting.
    """

    def __init__(
        self,
        axes: Axes,
        options: AirportVehicleOptions | None = None,
        path_follower: PathFollower | None = None,
    ) -> None:
        """Initialize an airport vehicle.

        :param axes: Axes on which the airport vehicle has to be plotted.
        :param options: Options for configuring the appearance of the airport vehicle.
        :param path_follower: PathFollower object to follow a path.
        """
        if options is None:
            options = AirportVehicleOptions()
        self.options: AirportVehicleOptions
        if options.color3 is None:
            options.color3 = options.color
        self.trailers = []  # type: list[Trailer]
        Car.__init__(self, axes, options, path_follower)

        if self.options.n_trailers:
            options_a = TrailerOptions(
                length=self.options.length_trailer_a,
                width=self.options.width_trailer,
                color=self.options.edgecolor,
                edgecolor=self.options.edgecolor,
                layer=self.options.layer,
            )
            options_b = TrailerOptions(
                length=self.options.length_trailer_b,
                width=self.options.width_trailer,
                color=self.options.color3,
                edgecolor=self.options.edgecolor,
                layer=self.options.layer + 1,
                front_pivot=0.9,
                rear_pivot=0.1,
            )
            for _ in range(self.options.n_trailers):
                self.trailers.append(AirportTrailerA(axes, options_a))
                self.trailers.append(AirportTrailerB(axes, options_b))

            self.change_pos(
                self.options.x_position_init, self.options.y_position_init, self.options.angle_init
            )

    def _determine_color2(self) -> tuple[float, float, float]:
        """If defined, just return color2. If not, return darker version of color."""
        if self.options.color2 is None:
            hue, saturation, luminance = rgb2hsl(*self.options.color)
            luminance = min(1.0, max(0.0, luminance + self.options.luminance_diff))
            return hsl2rgb(hue, saturation, luminance)
        return self.options.color2

    def plot_vehicle(self) -> None:
        """Plot the airport vehicle."""
        # Plot the vehicle
        xdata = np.array([0.5, 0.5, -0.5, -0.5]) * self.options.width
        ydata = np.array([0.5, -0.5, -0.5, 0.5]) * self.options.length
        self.fills += (
            Polygon(
                self.axes,
                xdata,
                ydata,
                facecolor=self.options.color,
                edgecolor=self.options.edgecolor,
                zorder=self.options.layer,
            ),
        )

        # Plot some lines
        for xdata, ydata in (
            (np.array([-0.45, -0.45]), np.array([0.45, 0.1])),
            (np.array([0.45, 0.45]), np.array([0.45, 0.1])),
            (np.array([-0.5, 0.5]), np.array([0.1, 0.1])),
        ):
            self.plots += (
                self.axes.plot(
                    np.array(xdata) * self.options.width,
                    np.array(ydata) * self.options.length,
                    color=self.options.edgecolor,
                    linewidth=self.options.line_width,
                    zorder=self.options.layer,
                )[0],
            )

        # Plot baggage area
        xdata = np.array([0.45, 0.45, -0.45, -0.45]) * self.options.width
        ydata = np.array([0., -0.45, -0.45, 0.]) * self.options.length
        self.fills += (
            Polygon(
                self.axes,
                xdata,
                ydata,
                facecolor=self._determine_color2(),
                edgecolor=self.options.edgecolor,
                zorder=self.options.layer,
            ),
        )

        # Plot window
        xdata = np.array([0.45, 0.45, -0.45, -0.45]) * self.options.width
        ydata = np.array([0.45, 0.37, 0.37, 0.45]) * self.options.length
        self.fills += (
            Polygon(
                self.axes,
                xdata,
                ydata,
                facecolor=self.options.window_color,
                edgecolor=self.options.edgecolor,
                zorder=self.options.layer,
            ),
        )

    def change_pos(self, x_center: float, y_center: float, angle: float = 0) -> None:
        """Change the position of the static object.

        :param x_center: The new x-coordinate of the static object.
        :param y_center: The new y-coordinate of the static object.
        :param angle: The new angle of the static object.
        """
        Car.change_pos(self, x_center, y_center, angle)
        if self.trailers:
            xpos, ypos = self.get_rear_x(), self.get_rear_y()
            for trailer in self.trailers:
                trailer.set_front_pivot(xpos, ypos, angle)
                xpos, ypos = trailer.get_rear_x(), trailer.get_rear_y()

    def move_vehicle(self, stepsize: float) -> None:
        """Move the vehicle a tiny bit and return new coordinates.

        This is only possible if self.path_follower is defined.

        :param stepsize: The distance to move the vehicle.
        """
        if self.path_follower is None:
            msg = "PathFollower is not defined for this vehicle."
            raise ValueError(msg)
        xpos, ypos, angle = self.path_follower.move_vehicle(stepsize)
        Car.change_pos(self, xpos, ypos, angle)
        if self.trailers:
            xpos, ypos = self.get_rear_x(), self.get_rear_y()
            for trailer in self.trailers:
                trailer.update_pos(xpos, ypos)
                xpos, ypos = trailer.get_rear_x(), trailer.get_rear_y()


class AirportTrailerA(Trailer):
    """First part of the airport vehicle trailer."""

    def plot_vehicle(self) -> None:
        """Plot the first part of the airport vehicle."""
        # The tires
        xdata = np.array([0.42, 0.42, 0.5, 0.5]) * self.options.width
        ydata = np.array([-0.7, -0.3, -0.3, -0.7]) * self.options.length
        self.fills += (
            Polygon(
                self.axes,
                xdata,
                ydata,
                facecolor=self.options.color,
                edgecolor=None,
                zorder=self.options.layer,
            ),
            Polygon(
                self.axes,
                -xdata,
                ydata,
                facecolor=self.options.color,
                edgecolor=None,
                zorder=self.options.layer,
            ),
        )

        # Rear axle
        xdata = np.array([-0.42, 0.42]) * self.options.width
        ydata = np.array([-0.5, -0.5]) * self.options.length
        self.plots += (
            self.axes.plot(
                xdata,
                ydata,
                color=self.options.edgecolor,
                linewidth=self.options.line_width,
                zorder=self.options.layer,
            )[0],
        )

        # Connection to front
        xdata = np.array([-0.2, 0.0, 0.2]) * self.options.width
        ydata = np.array([-0.5, 0.5, -0.5]) * self.options.length
        self.plots += (
            self.axes.plot(
                xdata,
                ydata,
                color=self.options.edgecolor,
                linewidth=self.options.line_width,
                zorder=self.options.layer,
            )[0],
        )


class AirportTrailerB(Trailer):
    """Second part of the airport vehicle trailer."""

    def plot_vehicle(self) -> None:
        """Plot the second part of the airport vehicle."""
        # Just a big square
        xdata = np.array([0.5, 0.5, -0.5, -0.5]) * self.options.width
        ydata = np.array([0.5, -0.5, -0.5, 0.5]) * self.options.length
        self.fills += (
            Polygon(
                self.axes,
                xdata,
                ydata,
                facecolor=self.options.color,
                edgecolor=self.options.edgecolor,
                zorder=self.options.layer,
            ),
        )
