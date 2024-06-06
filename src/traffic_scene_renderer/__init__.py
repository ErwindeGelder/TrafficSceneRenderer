"""Python library for creating schematic overviews of traffic scenes.

Author(s): Erwin de Gelder
"""

from .bus import Bus, BusOptions
from .car import Car, CarOptions, CarType
from .path_follower import PathFollower
from .static_objects import (
    Building,
    BuildingOptions,
    MaxSpeed,
    MaxSpeedOptions,
    Stripes,
    StripesOptions,
    TurnArrow,
    TurnArrowOptions,
)
from .vertex import Vertex, VertexOptions
from .way import Way, WayOptions
