"""Car object.

Author(s): Erwin de Gelder
"""

from enum import Enum
from typing import List, Optional, Tuple

import numpy as np
from matplotlib.axes import Axes

from .path_follower import PathFollower
from .polygon import Polygon
from .vehicle import Vehicle, VehicleOptions


class CarType(Enum):
    """Different car types for drawing a transparent car."""

    VEHICLE = 1
    STATION_WAGON = 2
    PICKUP_TRUCK = 3
    SEDAN = 4


class InvalidCarTypeError(Exception):
    """Error to be raised in case a car type is specified that is not implemented."""

    def __init__(self, car_type: int) -> None:
        """Description of error."""
        super().__init__(
            f"Car type '{car_type}' is invalid. Choose one of the CarType enumeration."
        )


class CarOptions(VehicleOptions):
    """The default values of the options of a car.

    The following list shows the options with within parentheses the default values:
        length (4.5): The length of the car.
        width (1.8): The width of the car.
        icar (CarType.VEHICLE): The index of the type of the car.
        line_width (1): The line width for plotting the car.
        x_position_init (0): The initial horizontal position of the car.
        y_position_init (0): The initial vertical position of the car.
        angle_init (0): The initial angle of the car.
        fill (True): Whether to use a non-transparent car (True) or a transparent car (False).
        color ([0, 0.4375, 0.75]): Color of the car.
        windowcolor ([1, 1, 1]): In case of a non-transparent car, the color of the windows can be
                                 set.
        front_light_color ([1, 1, 1]): Colors of the front light beam.
        edgecolor ([0, 0, 0]): In case of a non-transparent car, the color of the lines is set
                               using this option.
        layer (2): The layer in which the car will be plotted.
    """

    length: float = 4.5
    width: float = 1.8
    fill: bool = True
    icar: CarType = CarType.VEHICLE
    window_color: Tuple[float, float, float] = (1, 1, 1)
    front_light_color: Tuple[float, float, float] = (1, 1, 1)


class Car(Vehicle):
    """Plot a car on the scene.

    Attributes:
        options (CarOptions): All options. For a detailed description, see above.
        is_braking (bool): Whether the car is braking or not.
        axes (Axes): The axes that is used for plotting.
    """

    def __init__(
        self,
        axes: Axes,
        options: Optional[CarOptions] = None,
        path_follower: Optional[PathFollower] = None,
    ) -> None:
        """Create a car object.

        :param axes: The axes on which the car is supposed to be drawn.
        :param options: Various options for the car, see CarOptions.
        :param path_follower: Path that the car needs to follow (if any).
        """
        if options is None:
            options = CarOptions()
        Vehicle.__init__(self, axes, options, path_follower)
        self.options: CarOptions

    def plot_vehicle(self) -> None:
        """Do the actual plotting of the vehicle on the specified axes."""
        if self.options.fill:
            self.draw_filled_car()
        else:
            self.draw_transparent_car()

    def car(self) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """Get (x,y) data of the lines for drawing the (transparent) car.

        :return: The (x,y) data of the lines for drawing the car.
        """
        if self.options.icar == CarType.VEHICLE:
            xdata = [
                [2.0, 2, 5, 6, 6, 5, 2, 2, 6, 13, 13, 13, 16, 61, 63, 63],
                [61.0, 67, 76, 80, 80],
                [67.0, 14, 6, 14, 67, 64, 67, 95, 101, 107, 105, 99, 101, 107, 109, 111, 111],
            ]
            ydata = [
                [26.0, 14, 14, 15, 20, 21, 21, 13, 7, 11, 26, 11, 9, 9, 13, 26],
                [9.0, 4, 12, 20, 26],
                [4.0, 2, 7, 2, 4, 1, 4, 3, 5, 12, 13, 9, 5, 12, 16, 23, 26],
            ]
            xoffset = 56.5
            xscale = 109.0
            yoffset = 26.0
            yscale = 50.0
        elif self.options.icar == CarType.STATION_WAGON:
            xdata = [
                [49.0, 49, 51, 109, 112, 113, 113],
                [109.0, 114, 120, 125, 128, 128],
                [114.0, 81, 81, 81, 52, 51, 52, 55, 139, 146, 142, 138, 138],
                [146.0, 148, 148],
            ]
            ydata = [
                [68.0, 60, 53, 53, 60, 63, 68],
                [53.0, 49, 49, 54, 62, 68],
                [49.0, 50, 53, 50, 50, 53, 50, 47, 47, 54, 54, 50, 47],
                [54.0, 61, 68],
            ]
            xoffset = 98.5
            xscale = 99
            yoffset = 68
            yscale = 42
        elif self.options.icar == CarType.PICKUP_TRUCK:
            xdata = [
                [29.0, 29, 78, 78],
                [29.0, 78, 78, 29, 29],
                [29.0, 78, 78, 29, 29],
                [11.0, 11, 14, 19, 19, 19, 22, 135, 129, 135, 164, 177, 183, 183],
                [84.0, 84, 93, 93],
                [129.0, 129, 126, 146, 149, 149],
                [25.0, 25, 79],
            ]
            ydata = [
                [49.5, 49, 49, 49.5],
                [39.0, 39, 40, 40, 39],
                [28.0, 28, 29, 29, 28],
                [49.5, 22, 19, 19, 49.5, 16, 13, 14, 8, 14, 15, 20, 45, 49.5],
                [49.5, 19, 23, 49.5],
                [49.5, 37, 22, 18, 38, 49.5],
                [49.5, 20, 20],
            ]
            xoffset = 97
            xscale = 172
            yoffset = 49.5
            yscale = 73
        elif self.options.icar == CarType.SEDAN:
            xdata = [
                [1.0, 1, 5, 27, 100, 95, 100, 135, 149, 154, 154, 154, 121],
                [38.0, 51, 81, 95],
                [38.0, 38, 42, 30, 22, 18, 15, 15],
                [88.0, 88, 87, 111, 116, 116],
            ]
            ydata = [
                [39.0, 23, 12, 6, 6, 1, 6, 6, 12, 26, 38, 27, 14],
                [10.0, 14, 14, 10],
                [38.0, 31, 17, 17, 20, 24, 32, 38],
                [38.0, 25, 17, 10, 33, 38],
            ]
            xoffset = 77.5
            xscale = 153
            yoffset = 38
            yscale = 70  # Mirrors will be 'outside' car
        else:
            raise InvalidCarTypeError(self.options.icar)

        xdata_scaled = []
        ydata_scaled = []
        for xdata_sub, ydata_sub in zip(xdata, ydata):
            xdata_scaled.append((np.array(xdata_sub) - xoffset) / xscale * self.options.length)
            ydata_scaled.append((np.array(ydata_sub) - yoffset) / yscale * self.options.width)

        return xdata_scaled, ydata_scaled

    def draw_transparent_car(self) -> None:
        """Draw a transparent car."""
        xdata, ydata = self.car()
        for xdata_sub, ydata_sub in zip(xdata, ydata):
            self.plots += (
                self.axes.plot(
                    ydata_sub,
                    xdata_sub,
                    "r-",
                    zorder=self.options.layer,
                    linewidth=self.options.line_width,
                )[0],
            )
            self.plots += (
                self.axes.plot(
                    ydata_sub * -1,
                    xdata_sub,
                    "r-",
                    zorder=self.options.layer,
                    linewidth=self.options.line_width,
                )[0],
            )

    def draw_filled_car(self) -> None:
        """Draw a car that is not transparent."""
        yoffset = 278.5
        yscale = 555
        xoffset = 135.5
        xscale = 224

        # Fill blue, mirror.
        xdata = np.array([135, 70, 45, 36, 30, 23, 28, 35, 57, 81, 135])
        ydata = np.array([1, 2, 9, 19, 35, 92, 513, 524, 541, 548, 556])
        xdata_new = (np.concatenate((xdata, 2 * xoffset - np.flipud(xdata))) - xoffset) / xscale
        ydata_new = (np.concatenate((ydata, np.flipud(ydata))) - yoffset) / yscale
        self.fills += (
            Polygon(
                self.axes,
                xdata_new * self.options.width,
                ydata_new * self.options.length,
                facecolor=self.options.color,
                edgecolor=self.options.edgecolor,
                zorder=self.options.layer,
            ),
        )

        # Fill blue, twice.
        xdata = (np.array([32, 7, 1, 4, 30]) - xoffset) / xscale
        ydata = (np.array([361, 360, 361, 365, 371]) - yoffset) / yscale
        self.fills += (
            Polygon(
                self.axes,
                xdata * self.options.width,
                ydata * self.options.length,
                facecolor=self.options.color,
                edgecolor=self.options.edgecolor,
                linewidth=self.options.line_width,
                zorder=self.options.layer,
            ),
            Polygon(
                self.axes,
                -xdata * self.options.width,
                ydata * self.options.length,
                facecolor=self.options.color,
                edgecolor=self.options.edgecolor,
                linewidth=self.options.line_width,
                zorder=self.options.layer,
            ),
        )

        # Black line, mirror.
        for xdata, ydata in zip(
            [np.array([43, 44, 51, 61]), np.array([82, 79, 96]), np.array([44, 40, 82])],
            [np.array([77, 49, 23, 15]), np.array([524, 527, 538]), np.array([493, 396, 524])],
        ):
            xdatas = (np.concatenate((xdata, 2 * xoffset - np.flipud(xdata))) - xoffset) / xscale
            ydatas = (np.concatenate((ydata, np.flipud(ydata))) - yoffset) / yscale
            self.plots += (
                self.axes.plot(
                    xdatas * self.options.width,
                    ydatas * self.options.length,
                    color=self.options.edgecolor,
                    linewidth=self.options.line_width,
                    zorder=self.options.layer,
                )[0],
            )

        # Fill white, mirror.
        for xdata, ydata in zip(
            [
                np.array([135, 89, 61, 46, 45, 62, 79, 105]),
                np.array([135, 81, 47, 40, 66, 90, 111]),
            ],
            [
                np.array([67, 69, 75, 83, 90, 153, 147, 146]),
                np.array([412, 409, 398, 391, 326, 332, 334]),
            ],
        ):
            xdatas = (np.concatenate((xdata, 2 * xoffset - np.flipud(xdata))) - xoffset) / xscale
            ydatas = (np.concatenate((ydata, np.flipud(ydata))) - yoffset) / yscale
            self.fills += (
                Polygon(
                    self.axes,
                    xdatas * self.options.width,
                    ydatas * self.options.length,
                    facecolor=self.options.window_color,
                    edgecolor=self.options.edgecolor,
                    linewidth=self.options.line_width,
                    fixed_color=True,
                    zorder=self.options.layer,
                ),
            )

        # Fill windows, twice.
        for xdata, ydata in zip(
            [
                np.array([32, 32, 51, 45]),
                np.array([53, 37, 33, 33, 38, 56, 60, 58]),
                np.array([63, 32, 32, 38, 60]),
                np.array([30, 31, 46, 58, 70, 91, 72]),
            ],
            [
                np.array([152, 178, 178, 165]),
                np.array([184, 184, 188, 253, 256, 250, 241, 208]),
                np.array([260, 276, 367, 366, 315]),
                np.array([494, 514, 529, 536, 538, 538, 527]),
            ],
        ):
            xdatas = (np.array(xdata) - xoffset) / xscale
            ydatas = (np.array(ydata) - yoffset) / yscale
            self.fills += (
                Polygon(
                    self.axes,
                    xdatas * self.options.width,
                    ydatas * self.options.length,
                    facecolor=self.options.window_color,
                    edgecolor=self.options.edgecolor,
                    linewidth=self.options.line_width,
                    fixed_color=True,
                    zorder=self.options.layer,
                ),
                Polygon(
                    self.axes,
                    -xdatas * self.options.width,
                    ydatas * self.options.length,
                    facecolor=self.options.window_color,
                    edgecolor=self.options.edgecolor,
                    linewidth=self.options.line_width,
                    fixed_color=True,
                    zorder=self.options.layer,
                ),
            )

        # Fill front beam, twice.
        xdata = (np.array([30, 31, 46, 58, 70, 91, 72]) - xoffset) / xscale
        ydata = (np.array([494, 514, 529, 536, 538, 538, 527]) - yoffset) / yscale
        self.fills += (
            Polygon(
                self.axes,
                xdata * self.options.width,
                ydata * self.options.length,
                facecolor=self.options.front_light_color,
                edgecolor=self.options.edgecolor,
                linewidth=self.options.line_width,
                fixed_color=True,
                zorder=self.options.layer,
            ),
            Polygon(
                self.axes,
                -xdata * self.options.width,
                ydata * self.options.length,
                facecolor=self.options.front_light_color,
                edgecolor=self.options.edgecolor,
                linewidth=self.options.line_width,
                fixed_color=True,
                zorder=self.options.layer,
            ),
        )
