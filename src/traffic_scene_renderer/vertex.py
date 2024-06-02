"""Constructing a vertex that is used to construct ways.

Author(s): Erwin de Gelder
"""

from typing import List, Tuple
import numpy as np
from .utilities import wgs_to_utm, set_options


class Vertex:
    """A vertex that can be used to construct ways.

    The following list shows the options with within parentheses the default values:
        latlon (False): Whether the provided data is in latlon format. If so, data will be
                        transformed.
        zonenumber (None): In case latlon data is provided, it will be transformed using the
                           zonenumber. If no zonenumber is provided, it will be computed based on
                           the latlon data.

    Attributes:
    """

    def __init__(self, idx: int, xdata: float, ydata: float, options: dict = None):
        # Define default options.
        self.options = dict(latlon=False, zonenumber=None)

        # Set options.
        self.options = set_options(self.options, options)

        self.idx = idx
        self.xcoordinate = float(xdata)
        self.ycoordinate = float(ydata)
        if self.options["latlon"]:
            self.xcoordinate, self.ycoordinate = self.compute_wgs(
                force_zone_number=self.options["zonenumber"]
            )

    def compute_wgs(self, force_zone_number=None) -> Tuple[float, float]:
        """Compute the wgs coordinates.

        :param force_zone_number: Zone number to be used. When set to none, zone is determined by
                                  latlon coordinate.
        """
        utm = wgs_to_utm(
            np.array([[self.xcoordinate, self.ycoordinate]]), force_zone_number=force_zone_number
        )
        self.options["zonenumber"] = utm[1]
        return utm[0][0, 0], utm[0][0, 1]

    def get_xy(self) -> List:
        """Get the (x, y)-coordinate of this vertex.

        :return: The (x, y) coordinate as a list of two numbers.
        """
        return [self.xcoordinate, self.ycoordinate]

    def __str__(self):
        return "Vertex[ID={:d}, x={:.2f}, y={:.2f}]".format(
            self.idx, self.xcoordinate, self.ycoordinate
        )
