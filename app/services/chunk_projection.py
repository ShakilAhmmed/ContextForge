import numpy as np


def project_to_2d(vectors: list[list[float]]) -> list[tuple[float, float]]:
    """PCA via SVD (no scikit-learn dependency for just this). With the
    current mock embedding provider (FakeEmbeddings, see app/core/embeddings.py)
    the vectors carry no real semantic structure, so this plot won't show
    meaningful clusters until real embeddings are wired up - it's still a
    faithful projection of whatever vectors are actually stored, not a
    fabricated layout."""
    if len(vectors) < 2:
        return [(0.0, 0.0) for _ in vectors]

    matrix = np.array(vectors, dtype=float)
    centered = matrix - matrix.mean(axis=0)
    _u, _s, vt = np.linalg.svd(centered, full_matrices=False)
    components = vt[: min(2, vt.shape[0])]
    coords = centered @ components.T

    if coords.shape[1] < 2:
        coords = np.pad(coords, ((0, 0), (0, 2 - coords.shape[1])))

    return [(float(x), float(y)) for x, y in coords]
