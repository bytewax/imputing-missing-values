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
            return ("data", {"time": align_to + timedelta(seconds=i), "value": np.nan})
        else:
            return (
                "data",
                {
                    "time": align_to + timedelta(seconds=i),
                    "value": random.randrange(0, 10),
                },
            )


class RandomNumpyInput(DynamicInput):
    def build(self, _worker_index, _worker_count):
        return RandomNumpyData()


flow = Dataflow()
flow.input("input", RandomNumpyInput())
# ('data', {'time': datetime.datetime(...), 'value': nan})


def new_array():
    return np.empty(0, dtype=object)


def impute_value(acc, event):
    new_value = event["value"]
    if np.isnan(new_value):
        new_value = np.nanmean(acc)

    acc = np.insert(acc, 0, new_value)
    return acc


window_config = SlidingWindow(
    length=timedelta(seconds=10), align_to=align_to, offset=timedelta(seconds=5)
)
clock_config = EventClockConfig(
    lambda e: e["time"], wait_for_system_duration=timedelta(seconds=0)
)
flow.fold_window(
    "10_second_windows", clock_config, window_config, new_array, impute_value
)

flow.output("out", StdOutput())
