import numpy as np
import bytewax.operators as op
from bytewax.dataflow import Dataflow
from bytewax.inputs import StatelessSourcePartition, DynamicSource
from bytewax.connectors.stdio import StdOutSink
import random 
from bytewax.testing import run_main
from bytewax._encoder import to_plantuml

class RandomNumpyData(StatelessSourcePartition):
    ''' 
    Data Source that generates a sequence 
    of 100 numbers, where every 5th number is 
    missing (represented by np.nan),
    and the rest are random integers between 0 and 10. 
    '''

    def __init__(self): 
         self._it = enumerate(range(100)) 
    
    def next_batch(self):
        i, item = next(self._it)
        if i % 5 == 0:
            return [("data", np.nan)]
        else:
            return [("data", random.randint(0, 10))]

class RandomNumpyInput(DynamicSource):
    ''' 
    Class encapsulating dynamic data generation 
    based on worker distribution in distributed processing 
    '''
    
    def build(self,step_id, _worker_index, _worker_count):
        return RandomNumpyData()


flow = Dataflow("map_eg")
input_stream = op.input("input", flow, RandomNumpyInput())

class WindowedArray:
    """Windowed Numpy Array.
    Create a numpy array to run windowed statistics on.
    """

    def __init__(self, window_size):
        self.last_n = np.empty(0, dtype=float)
        self.n = window_size

    def _push(self, value):
        if np.isscalar(value) and np.isreal(value):
            self.last_n = np.insert(self.last_n, 0, value)
            try:
                self.last_n = np.delete(self.last_n, self.n)
            except IndexError:
                pass

    def impute_value(self, value):
        self._push(value)
        if np.isnan(value):
            if self.last_n.size == 0 or np.all(np.isnan(self.last_n)):
                new_value = value
            else:
                new_value = np.nanmean(self.last_n)
        else:
            new_value = value
        return self, (value, new_value)
class StatefulImputer:
    '''
    This class is a stateful object that encapsulates a 
    WindowedArray and provides a method that uses this 
    array to impute values. 
    The impute_value method of this object is passed to 
    op.stateful_map, so the state is maintained across 
    calls to this method.
    '''
    def __init__(self, window_size):
        self.windowed_array = WindowedArray(window_size)

    def impute_value(self, key, value):
        return self.windowed_array.impute_value(value)

imputer = StatefulImputer(window_size=10)
imputed_stream = op.stateful_map("impute", input_stream, imputer.impute_value)
# optional - run a test
# op.inspect("inspect", imputed_stream)
# run_main(flow)
op.output("output", imputed_stream, StdOutSink())

# Optional - print the plantuml diagram
# if __name__ == "__main__":

#     print(to_plantuml(flow, recursive=False))