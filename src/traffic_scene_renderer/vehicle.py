"""Abstract class for drawing vehicles.

Author(s): Erwin de Gelder
"""

from abc import abstractmethod
from typing import Optional, Tuple

import numpy as np
from matplotlib.axes import Axes

from .options import Options
from .path_follower import PathFollower
from .static_objects import StaticObject


class MoveVehicleNoPathFollowerDefinedError(Exception):
    """Error to be raised in case a vehicle is moved without a defined PathFollower."""

    def __init__(self) -> None:
        """Description of error."""
        super().__init__("Cannot move the vehicle if no PathFollower is defined.")


class VehicleOptions(Options):
    """The default values of the options of a vehicle.

    The following list shows the options (default values within parentheses):
        length (4.5): The length of the vehicle.
        width (1.8): The width of the vehicle.
        line_width (1): The line width for plotting the vehicle.
        x_position_init (0): The initial horizontal position of the vehicle.
        y_position_init (0): The initial vertical position of the vehicle.
        angle_init (0): The initial angle of the vehicle.
        color ((0, 0.4375, 0.75)): Color of the vehicle.
        edgecolor ((0, 0, 0)): Edgecolor of the vehicle.
        layer (2): The layer in which the vehicle will be plotted.
    """

    length: float = 4.5
    width: float = 1.8
    line_width: float = 1
    x_position_init: float = 0
    y_position_init: float = 0
    angle_init: float = 0
    color: Tuple[float, float, float] = (0, 0.4375, 0.75)
    edgecolor: Tuple[float, float, float] = (0, 0, 0)
    layer: int = 2


class Vehicle(StaticObject):
    """Plot a vehicle on the scene.

    Attributes:
        options (CarOptions): All options. For a detailed description, see above.
        is_braking (bool): Whether the car is braking or not.
        axes (Axes): The axes that is used for plotting.
        path_follower (PathFollower): Optional object, used when vehicle needs to follow a path.
    """

    def __init__(
        self,
        axes: Axes,
        options: Optional[VehicleOptions] = None,
        path_follower: Optional[PathFollower] = None,
    ) -> None:
        """Instantiating a vehicle object.

        :param axes: The axes on which the vehicle is supposed to be drawn.
        :param options: Various options for the vehicle, see VehicleOptions.
        :param path_follower: Path that the vehicle needs to follow (if any).
        """
        self.options = VehicleOptions() if options is None else options
        self.is_braking = False
        self.axes = axes
        StaticObject.__init__(self, axes)

        # Plot the vehicle.
        self.plot_vehicle()

        # Update initial position if path follower is given
        self.path_follower = path_follower
        if self.path_follower is not None:
            if self.path_follower.length is None:
                self.path_follower.length = self.options.length
            self.options.x_position_init, self.options.y_position_init, self.options.angle_init = (
                self.path_follower.get_center_coordinates()
            )

        # Set initial position
        self.change_pos(
            self.options.x_position_init, self.options.y_position_init, self.options.angle_init
        )

    @abstractmethod
    def plot_vehicle(self) -> None:
        """Plot the vehicle on the axes."""

    def get_front_x(self) -> float:
        """Return the x-coordinate of the front of the vehicle.

        :return: The x-coordinate of the front of the vehicle.
        """
        return self.position.x_center + self.options.length * np.sin(self.position.angle) / 2

    def get_rear_x(self) -> float:
        """Return the x-coordinate of the rear of the vehicle.

        :return: The x-coordinate of the front of the vehicle.
        """
        return self.position.x_center - self.options.length * np.sin(self.position.angle) / 2

    def get_front_y(self) -> float:
        """Return the y-coordinate of the front of the vehicle.

        :return: The y-coordinate of the front of the vehicle.
        """
        return self.position.y_center + self.options.length * np.cos(self.position.angle) / 2

    def get_rear_y(self) -> float:
        """Return the y-coordinate of the front of the vehicle.

        :return: The y-coordinate of the front of the vehicle.
        """
        return self.position.y_center - self.options.length * np.cos(self.position.angle) / 2

    def set_front_xy(self, x_front: float, y_front: float, angle: float = 0) -> None:
        """Set position of vehicle such that its front is at (x, y) with provided angle.

        :param x_front: The x-coordinate of where the front should be.
        :param y_front: The y-coordinate of where the frnot should be.
        :param angle: The angle of the vehicle.
        """
        x_center = x_front - self.options.length * np.sin(angle) / 2
        y_center = y_front - self.options.length * np.cos(angle) / 2
        self.change_pos(x_center, y_center, angle)

    def move_vehicle(self, stepsize: float) -> None:
        """Move the vehicle a tiny bit and return new coordinates.

        This is only possible if self.path_follower is defined.
        """
        if self.path_follower is None:
            raise MoveVehicleNoPathFollowerDefinedError
        self.change_pos(*self.path_follower.move_vehicle(stepsize))

    def start_braking(self, length: float = 2) -> None:
        """Add the skid mark that shows that a vehicle is braking.

        :param length: Length of the skid mark (default=2).
        """
        if not self.is_braking:
            x_center = self.position.x_center
            y_center = self.position.y_center
            angle = self.position.angle
            self.change_pos(0, 0, 0)
            xmin = 0.3 * self.options.width
            xmax = 0.45 * self.options.width
            ymin = 0
            ymax = -0.5 * self.options.length - length
            self.fills += (
                self.axes.fill(
                    [xmin, xmin, xmax, xmax],
                    [ymin, ymax, ymax, ymin],
                    "k",
                    zorder=self.options.layer - 1,
                )[0],
                self.axes.fill(
                    [-xmin, -xmin, -xmax, -xmax],
                    [ymin, ymax, ymax, ymin],
                    "k",
                    zorder=self.options.layer - 1,
                )[0],
            )
            self.is_braking = True
            self.change_pos(x_center, y_center, angle)

    def stop_braking(self) -> None:
        """Remove the skid mark (if any) that shows that a vehicle is braking."""
        if self.is_braking:
            removes = self.fills[-2:]
            self.fills = self.fills[:-2]
            for remove in removes:
                remove.remove()
                del remove
            self.is_braking = False
