"""Trailer object.

Author(s): Erwin de Gelder
"""

from abc import ABC

import numpy as np
from matplotlib.axes import Axes

from .vehicle import Vehicle, VehicleOptions


class TrailerOptions(VehicleOptions):
    """The default values of the options of a trailer.

    The following list shows the options (default values within parentheses):
        length (4.5): The length of the trailer.
        width (1.8): The width of the trailer.
        line_width (1): The line width for plotting the trailer.
        x_position_init (0): The initial horizontal position of the trailer.
        y_position_init (0): The initial vertical position of the trailer.
        angle_init (0): The initial angle of the trailer.
        color ((0, 0.4375, 0.75)): Color of the trailer.
        edgecolor ((0, 0, 0)): Edgecolor of the trailer.
        layer (2): The layer in which the vehicle will be plotted.
        front_pivot (1): The relative point (1=front, 0=rear) where the trailer
            connects with the front vehicle.
        rear_pivot (0): The relative point (1-front, 0=rear) of the rear axle.
    """
    front_pivot: float = 1
    rear_pivot: float = 0


class Trailer(Vehicle, ABC):
    """The default class for a trailer."""

    def __init__(self, axes: Axes, options: TrailerOptions = None) -> None:
        """Initialize a trailer."""
        if options is None:
            options = TrailerOptions()
        Vehicle.__init__(self, axes, options)

    def set_front_pivot(self, xpos: float, ypos: float, angle: float) -> None:
        """Change the position such that the front pivot is at the set position.

        :param xpos: x-coordinate of the front pivot.
        :param ypos: y-coordinate of the front pivot.
        :param angle: angle of the trailer.
        """
        distance_from_center = (self.options.front_pivot - 0.5) * self.options.length
        xpos_center = xpos - np.sin(angle) * distance_from_center
        ypos_center = ypos - np.cos(angle) * distance_from_center
        self.change_pos(xpos_center, ypos_center, angle)

    def get_rearpivot_x(self) -> float:
        """Return the x-coordinate of the rear pivot of the trailer.

        :return: The x-coordinate of the rear pivot of the trailer.
        """
        return self.position.x_center + \
            self.options.length*np.sin(self.position.angle)*(self.options.rear_pivot-0.5)

    def get_rearpivot_y(self) -> float:
        """Return the y-coordinate of the rear pivot of the trailer.

        :return: The y-coordinate of the rear pivot of the trailer.
        """
        return self.position.y_center + \
            self.options.length*np.cos(self.position.angle)*(self.options.rear_pivot-0.5)

    def update_pos(self, xpos: float, ypos: float) -> None:
        """Update position based on updated position of front object.

        :param xpos: The new x-coordinate of where the front pivot point should be.
        :param ypos: The new y-coordinate of where the front pivot point should be.
        """
        # Compute the required distance from the new point (xpos, ypos) to the rear pivot, which is
        # the same as the distance between the front and rear pivot point.
        required_distance = (self.options.front_pivot-self.options.rear_pivot) * self.options.length

        # Compute the distance that the rear pivot point should travel in the direction of the
        # trailer such that it ends up at the required distance. This is computed using quadratic
        # solving using the abc-formula. The smaller solution is the right one - this works if the
        # step is not too big.
        xrearpivot, yrearpivot = self.get_rearpivot_x(), self.get_rearpivot_y()
        quadratic_b = 2*((xrearpivot-xpos)*np.sin(self.position.angle) +
                         (yrearpivot-ypos)*np.cos(self.position.angle))
        quadratic_c = (xrearpivot - xpos)**2 + (yrearpivot - ypos)**2 - required_distance**2
        move_distance = (-quadratic_b - np.sqrt(quadratic_b**2-4*quadratic_c)) / 2

        # Update the position of the rear pivot point.
        xrearpivot += move_distance*np.sin(self.position.angle)
        yrearpivot += move_distance*np.cos(self.position.angle)

        # Compute the new angle and change the position of the trailer accordingly.
        new_angle = np.arctan2(xpos - xrearpivot, ypos - yrearpivot)
        self.set_front_pivot(xpos, ypos, new_angle)
