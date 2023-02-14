import random
import numpy as np

from bytewax.dataflow import Dataflow
from bytewax.execution import run_main
from bytewax.inputs import ManualInputConfig
from bytewax.outputs import StdOutputConfig


def random_datapoints(worker_index, worker_count, state):
    state = None
    for i in range(100):
        if i % 5 == 0:
            yield state, ('data', np.nan)
        else:
            yield state, ('data', random.randrange(0, 10))

flow = Dataflow()
flow.input("input", ManualInputConfig(random_datapoints))
# ("metric", value)

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


flow.stateful_map("windowed_array", lambda: WindowedArray(10), WindowedArray.impute_value)
# ("metric", (old value, new value))
flow.capture(StdOutputConfig())

if __name__ == "__main__":
    run_main(flow)