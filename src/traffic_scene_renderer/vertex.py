"""Constructing a vertex that is used to construct ways.

Author(s): Erwin de Gelder
"""

from typing import List, Optional, Tuple

import numpy as np

from .options import Options
from .utilities import wgs_to_utm


class VertexOptions(Options):
    """The default options for a vertex."""

    latlon: bool = False
    zonenumber: Optional[int] = None


class Vertex:
    """A vertex that can be used to construct ways.

    The following list shows the options with within parentheses the default values:
        latlon (False): Whether the provided data is in latlon format. If so, data will be
                        transformed.
        zonenumber (None): In case latlon data is provided, it will be transformed using the
                           zonenumber. If no zonenumber is provided, it will be computed based on
                           the latlon data.
    """

    def __init__(
        self, idx: int, xdata: float, ydata: float, options: Optional[VertexOptions] = None
    ) -> None:
        """Create vertex object.

        :param idx: Index of the vertex. Make sure it is unique.
        :param xdata: x-coordinate.
        :param ydata: y-coordinate.
        :param options: options, such as latlon and zonenumber.
        """
        # Define default options.
        self.options = VertexOptions() if options is None else options

        self.idx = idx
        self.xcoordinate = float(xdata)
        self.ycoordinate = float(ydata)
        if self.options.latlon:
            self.xcoordinate, self.ycoordinate = self.compute_wgs(
                force_zone_number=self.options.zonenumber
            )

    def compute_wgs(self, force_zone_number: Optional[int] = None) -> Tuple[float, float]:
        """Compute the wgs coordinates.

        :param force_zone_number: Zone number to be used. When set to none, zone is determined by
                                  latlon coordinate.
        """
        utm = wgs_to_utm(
            np.array([[self.xcoordinate, self.ycoordinate]]), force_zone_number=force_zone_number
        )
        self.options.zonenumber = utm[1]
        return utm[0][0, 0], utm[0][0, 1]

    def get_xy(self) -> List:
        """Get the (x, y)-coordinate of this vertex.

        :return: The (x, y) coordinate as a list of two numbers.
        """
        return [self.xcoordinate, self.ycoordinate]

    def __str__(self) -> str:
        """Return a string with the ID, x-coordinate, and y-coordinate of the vertex."""
        return f"Vertex[ID={self.idx:d}, x={self.xcoordinate:.2f}, y={self.ycoordinate:.2f}]"
