from app.services.chunk_projection import project_to_2d


def test_project_to_2d_empty_returns_empty():
    assert project_to_2d([]) == []


def test_project_to_2d_single_vector_returns_origin():
    assert project_to_2d([[1.0, 2.0, 3.0]]) == [(0.0, 0.0)]


def test_project_to_2d_returns_one_point_per_vector():
    vectors = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 1.0, 1.0]]

    coords = project_to_2d(vectors)

    assert len(coords) == len(vectors)
    for x, y in coords:
        assert isinstance(x, float)
        assert isinstance(y, float)


def test_project_to_2d_identical_vectors_collapse_to_same_point():
    vectors = [[1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [1.0, 2.0, 3.0]]

    coords = project_to_2d(vectors)

    assert coords[0] == coords[1] == coords[2]


def test_project_to_2d_distinct_vectors_separate():
    vectors = [[0.0, 0.0], [10.0, 0.0], [0.0, 10.0]]

    coords = project_to_2d(vectors)

    assert len(set(coords)) == 3
