import numpy as np
import random

from datetime import datetime, timedelta, timezone

from bytewax.dataflow import Dataflow
from bytewax.connectors.stdio import StdOutput

from bytewax.window import (
    EventClockConfig,
    SlidingWindow,
)

from bytewax.inputs import DynamicInput, StatelessSource

align_to = datetime(2023, 1, 1, tzinfo=timezone.utc)


class RandomNumpyData(StatelessSource):
    def __init__(self):
        self._it = enumerate(range(100))

    def next(self):
        i, item = next(self._it)
        if i % 5 == 0:
            return ("data", np.nan)
        else:
            return ("data", random.randint(0, 10))


class RandomNumpyInput(DynamicInput):
    def build(self, _worker_index, _worker_count):
        return RandomNumpyData()


flow = Dataflow()
flow.input("input", RandomNumpyInput())
# ('data', {'time': datetime.datetime(...), 'value': nan})


class WindowedArray:
    """Windowed Numpy Array.
    Create a numpy array to run windowed statistics on.
    """

    def __init__(self, window_size):
        self.last_n = np.empty(0, dtype=object)
        self.n = window_size

    def _push(self, value):
        self.last_n = np.insert(self.last_n, 0, value)
        try:
            self.last_n = np.delete(self.last_n, self.n)
        except IndexError:
            pass

    def impute_value(self, value):
        self._push(value)
        if np.isnan(value):
            new_value = np.nanmean(self.last_n)
        else:
            new_value = value
        return self, (value, new_value)


flow.stateful_map(
    "windowed_array", lambda: WindowedArray(10), WindowedArray.impute_value
)
# ("metric", (old value, new value))
flow.output("out", StdOutput())
