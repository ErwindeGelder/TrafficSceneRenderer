"""Python library for creating schematic overviews of traffic scenes.

Author(s): Erwin de Gelder
"""

from .ambulance import Ambulance, AmbulanceOptions
from .arrow import arrow
from .bus import Bus, BusOptions
from .car import Car, CarOptions, CarType, InvalidCarTypeError
from .connection import Connection, InvalidConnectionError
from .crossing import Crossing, CrossingOptions
from .letters import Letter, LetterOptions, Letters, LettersOptions
from .options import FrozenOptionsError, Options, UnknownOptionError
from .path_follower import PathFollower
from .road_network import CrossingInfo, RoadNetwork, RoadNetworkOptions, StopLineOptions
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
from .traffic_light import NoAmberError, TrafficLight, TrafficLightOptions, TrafficLightStatus
from .truck import Truck, TruckOptions
from .vehicle import MoveVehicleNoPathFollowerDefinedError
from .vertex import Vertex, VertexOptions
from .way import IndexVertexError, Way, WayOptions
