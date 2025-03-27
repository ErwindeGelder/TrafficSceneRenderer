"""Scripts for testing all functionalities from vertex.py.

Author(s): Erwin de Gelder
"""

import numpy as np

from traffic_scene_renderer import Vertex, VertexOptions, generate_vertices


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


def test_generate_vertices() -> None:
    vertices1 = generate_vertices(np.array([[0, 0], [1, 1], [2, 2]]))
    vertices2 = generate_vertices([(0, 0), (1, 1), (2, 2)], idx_start=5)
    for vertex1, vertex2 in zip(vertices1, vertices2):
        assert vertex1.xcoordinate == vertex2.xcoordinate
        assert vertex1.ycoordinate == vertex2.ycoordinate
        assert vertex1.idx + 5 == vertex2.idx
