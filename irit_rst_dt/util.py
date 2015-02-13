# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)


"""
Miscellaneous utility functions
"""

import itertools
import os

from attelo.harness.util import timestamp

from .local import LOCAL_TMP


def current_tmp():
    """
    Directory for the current run
    """
    return os.path.join(LOCAL_TMP, timestamp())


def latest_tmp():
    """
    Directory for last run (usually a symlink)
    """
    return os.path.join(LOCAL_TMP, "latest")


def concat_i(itr):
    """
    Walk an iterable of iterables as a single one
    """
    return itertools.chain.from_iterable(itr)
