# -*- coding: utf-8 -*-
"""Euclidean distance and pairwise euclidean distance."""

__author__ = ["chrisholder"]
__all__ = [
    "euclidean_distance",
    "pairwise_euclidean_distance",
    "numba_euclidean_distance_factory",
]

from typing import Callable

import numpy as np
from numba import njit, prange

from sktime.dists_kernels._utils import to_numba_timeseries
from sktime.dists_kernels.numba.distances.pairwise_distances import pairwise_distance


def euclidean_distance(x: np.ndarray, y: np.ndarray) -> float:
    r"""Compute the Euclidean distance between two timeseries.

    Euclidean distance is supported for 1D, 2D and 3D arrays.

    The euclidean distance between two timeseries is defined as:

    .. math::
        ed(x, y) = \sqrt{\sum_{i=1}^{n} (x_i - y_i)^2}

    Parameters
    ----------
    x: np.ndarray (1D, 2D or 3D)
        First timeseries.
    y: np.ndarray (1D, 2D or 3D)
        Second timeseries.

    Returns
    -------
    distance: float
        Euclidean distance between the two timeseries.
    """
    _x = to_numba_timeseries(x)
    _y = to_numba_timeseries(y)
    return _numba_euclidean_distance(_x, _y)


def pairwise_euclidean_distance(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    r"""Compute the Euclidean pairwise distance between two timeseries.

    Pairwise euclidean distance is supported for 1D, 2D and 3D arrays.

    Parameters
    ----------
    x: np.ndarray (1D, 2D or 3D)
        First timeseries.
    y: np.ndarray (1D, 2D or 3D)
        Second timeseries.

    Returns
    -------
    np.ndarray (2D of size mxn where m is len(x) and m is len(y)
        Pairwise euclidean distance matrix of size nxm where n is len(x) and m is
        len(y).
    """
    return pairwise_distance(
        x, y, numba_distance_factory=numba_euclidean_distance_factory
    )


def numba_euclidean_distance_factory(
    x: np.ndarray, y: np.ndarray, symmetric: bool, **kwargs: dict
) -> Callable[[np.ndarray, np.ndarray], float]:
    """Create a numba compiled Euclidean distance callable based on parameters.

    While in this example parameters aren't used and the already defined numba method
    is returned, in more complex examples to compile them the parameters are needed.
    As such, for consistency parameters are kept here.

    Parameters
    ----------
    x: np.ndarray (1D, 2D or 3D)
        First timeseries.
    y: np.ndarray (1D, 2D or 3D)
        Second timeseries.
    symmetric: bool
        Boolean that is true when x == y and false when x != y. Used in some instances
        to speed up pairwise computation.
    kwargs: dict
        Extra kwargs. For euclidean there are none however, this is kept for
        consistency.

    Returns
    -------
    Callable[[np.ndarray, np.ndarray], float]
        Numba compiled Euclidean distance callable.
    """
    return _numba_euclidean_distance


@njit(cache=True, parallel=True)
def _numba_euclidean_distance(x: np.ndarray, y: np.ndarray) -> float:
    """Numba compiled Euclidean distance.

    Parameters
    ----------
    x: np.ndarray (1D, 2D or 3D)
        First timeseries.
    y: np.ndarray (1D, 2D or 3D)
        Second timeseries.

    Returns
    -------
    distance: float
        Euclidean distance between the two timeseries.
    """
    distance = 0.0
    for i in prange(x.shape[0]):
        curr = x[i] - y[i]
        distance += np.sum(np.sqrt(curr * curr))

    return distance
