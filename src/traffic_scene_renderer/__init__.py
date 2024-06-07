"""Python library for creating schematic overviews of traffic scenes.

Author(s): Erwin de Gelder
"""

from .car import Car, CarOptions, CarType, InvalidCarTypeError
from .crossing import Crossing, CrossingOptions
from .options import FrozenOptionsError, Options, UnknownOptionError
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
from .vehicle import MoveVehicleNoPathFollowerDefinedError
from .vertex import Vertex, VertexOptions
from .way import IndexInsertVertexError, Way, WayOptions
