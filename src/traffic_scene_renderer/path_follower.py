"""Class that can be used to make an object follow a certain path.

Author(s): Erwin de Gelder
"""

from typing import Optional, Tuple

import numpy as np


class PathFollowerLengthNotSetError(Exception):
    """Error to be raised in case the length is not set."""

    def __init__(self) -> None:
        """Description of error."""
        super().__init__("Length of PathFollower not set.")


class PathFollower:
    """Class for making an object follow a path."""

    def __init__(
        self,
        xcoordinates: np.ndarray,
        ycoordinates: np.ndarray,
        length: Optional[float] = None,
        init_rear: Optional[Tuple[int, float]] = None,
    ) -> None:
        """Create a PathFollower object that can be used to make an object follow a path.

        The location of the rear of the vehicle will be represented using (i_segment, lambda),
        where i_segment represents the segment the rear is on. Note that there are N-1 segments,
        where N represents the number of elements in the x,y coordinates. The proportion of the
        segment that is already covered is denoted by lambda.

        :param xcoordinates: The x-coordinates of the path.
        :param ycoordinates: The y-coordinates of the path.
        :param length: The length of the vehicle. It may be set later.
        :param init_rear: Initial location of the rear vehicle represented using
                          (i_segment, lambda). By default, this is (0, 0).
        """
        self.xcoordinates = xcoordinates
        self.ycoordinates = ycoordinates
        self.length = length
        if init_rear is None:
            self.i_segment = 0
            self.lambda_segment = 0.0
        else:
            self.i_segment, self.lambda_segment = init_rear
        self._segment_lengths = np.hypot(np.diff(self.xcoordinates), np.diff(self.ycoordinates))

    def get_rear_xy(self) -> Tuple[float, float]:
        """Return the (x,y) coordinates of the rear of the vehicle.

        :return: [x-coordinate, y-coordinate]
        """
        return (
            self.xcoordinates[self.i_segment] * (1 - self.lambda_segment)
            + self.xcoordinates[self.i_segment + 1] * self.lambda_segment,
            self.ycoordinates[self.i_segment] * (1 - self.lambda_segment)
            + self.ycoordinates[self.i_segment + 1] * self.lambda_segment,
        )

    def get_location_front(self) -> Tuple[int, float]:
        """Find the location of the front of the vehicle, given its position of the rear.

        :return: [Segment of front, Fraction of segment covered by front]
        """
        # Check that length is set.
        if self.length is None:
            raise PathFollowerLengthNotSetError

        # First determine the segment that the front is located in.
        xrear, yrear = self.get_rear_xy()
        i = self.i_segment + 1
        while np.hypot(self.xcoordinates[i] - xrear, self.ycoordinates[i] - yrear) < self.length:
            i += 1

        # We can now find lambda using quadratic solving. To see how this works, just write down the
        # equations yourself.
        # Also, except in some weird cases (e.g., if the path is screwed up), we can simply take the
        # largest solution.
        quadratic_a = (self.xcoordinates[i] - self.xcoordinates[i - 1]) ** 2 + (
            self.ycoordinates[i] - self.ycoordinates[i - 1]
        ) ** 2
        quadratic_b = 2 * (
            (self.xcoordinates[i - 1] - xrear) * (self.xcoordinates[i] - self.xcoordinates[i - 1])
            + (self.ycoordinates[i - 1] - yrear) * (self.ycoordinates[i] - self.ycoordinates[i - 1])
        )
        quadratic_c = (
            (self.xcoordinates[i - 1] - xrear) ** 2
            + (self.ycoordinates[i - 1] - yrear) ** 2
            - self.length**2
        )
        lambda_segment = (
            -quadratic_b + np.sqrt(quadratic_b**2 - 4 * quadratic_a * quadratic_c)
        ) / (2 * quadratic_a)
        return i, lambda_segment

    def get_front_xy(self) -> Tuple[float, float]:
        """Return the (x,y) coordinates of the front of the vehicle.

        :return: [x-coordinate, y-coordinate]
        """
        i_segment, lambda_segment = self.get_location_front()
        return (
            self.xcoordinates[i_segment - 1] * (1 - lambda_segment)
            + self.xcoordinates[i_segment] * lambda_segment,
            self.ycoordinates[i_segment - 1] * (1 - lambda_segment)
            + self.ycoordinates[i_segment] * lambda_segment,
        )

    def get_center_coordinates(self) -> Tuple[float, float, float]:
        """Get the center coordinates, including the heading.

        :return: [x-coordinate, y-coordinate, angle]
        """
        xrear, yrear = self.get_rear_xy()
        xfront, yfront = self.get_front_xy()
        angle = np.arctan2(xfront - xrear, yfront - yrear)
        return (xfront + xrear) / 2, (yfront + yrear) / 2, angle

    def move_vehicle(self, stepsize: float) -> Tuple[float, float, float]:
        """Move the vehicle a tiny bit and return new coordinates.

        :return: [x-coordinate, y-coordinate, angle]
        """
        # Check if we can use the same segment.
        available_space = (1 - self.lambda_segment) * self._segment_lengths[self.i_segment]
        if available_space > stepsize:
            self.lambda_segment += stepsize / self._segment_lengths[self.i_segment]
        else:
            stepsize -= available_space

            # Find the right segment
            self.i_segment += 1
            while stepsize > self._segment_lengths[self.i_segment]:
                stepsize -= self._segment_lengths[self.i_segment]
                self.i_segment += 1

            # Compute the new lambda
            self.lambda_segment = stepsize / self._segment_lengths[self.i_segment]

        # Return the updated position
        return self.get_center_coordinates()
