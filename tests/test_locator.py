# tests/test_locator.py
import matplotlib
matplotlib.use("Agg")

from matplotlib import ticker
import pytest

from py2dcos.plotting.backends.locator import define_locator


@pytest.mark.parametrize(
    "choice, levels, expected_cls, attr",
    [
        ("linear", 4, ticker.LinearLocator, "numticks"),
        ("maxN",  10, ticker.MaxNLocator, "_nbins"),
        ("log",    8, ticker.LogLocator,  "numticks"),
    ],
)
def test_define_locator_returns_correct_type_and_levels(choice, levels, expected_cls, attr):
    # define_locator should return the right Locator class and tick count
    loc = define_locator(choice, levels=levels)
    assert isinstance(loc, expected_cls)
    # ensure the number of levels matches the passed parameter
    assert getattr(loc, attr) == levels
