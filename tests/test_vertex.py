"""Scripts for testing all functionalities from vertex.py.

Author(s): Erwin de Gelder
"""

from traffic_scene_renderer import Vertex, VertexOptions


def test_vertex_creation() -> None:
    vertex = Vertex(0, 0, 0)
    assert str(vertex) == "Vertex[ID=0, x=0.00, y=0.00]"


def test_vertex_creation_with_latlon() -> None:
    vertex_options = VertexOptions(latlon=True)
    # Location of TNO Automotive :)
    vertex = Vertex(0, 51.474457, 5.623897, options=vertex_options)
    assert str(vertex) == "Vertex[ID=0, x=682219.44, y=5705853.69]"


def test_vertex_get_xy() -> None:
    vertex = Vertex(0, 1, 2)
    assert vertex.get_xy() == [1, 2]
