# Imputing Values for real-time ML

- Skill level
    
    **Beginner**
    
- Time to complete
    
    **Approx. 5 min**
    

Introduction: **Given that the real world is never ideal, our datasets are often far from perfect and contain missing values. In order to build accurate machine learning models, we must address missing values. When data is missing, our understanding of the system is incomplete, potentially due to issues such as sensor failure, network issues, or optional data fields. In real-time applications like self-driving cars, heating systems, and smart devices, incorrect interpretation of missing data can have severe consequences. The process for dealing with missing value is called imputation and we will demonstrate how you can build a custom window to deal with this in Bytewax.**

## ****Prerequisites****

**Python modules**
bytewax
numpy

## Your Takeaway

*Learn how to create a sliding window to impute values using numpy*

## Resources

[Github link](https://github.com/bytewax/imputing-missing-values)

### Input Code

Bytewax is based around the concept of a dataflow. A dataflow is made up of a sequence of operators that interact with data that is “flowing” through it.

For this example we will mock up some data that will yield either a random integer between 0 and 10, or a numpy `nan` value for every 5th value we generate.

``` python
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
```


### Creating Windows Using `fold_window`

We'll be using the [fold_window](https://bytewax.io/apidocs/bytewax.dataflow#bytewax.dataflow.Dataflow.fold_window) operator to create 10 second windows of our event. The fold window operator has two parts to it: a `builder` function and a `folder` function. The `builder` function will get invoked for each new key, and the `folder` will get called for every new data point. For more information on how this works, [the api docs](https://bytewax.io/apidocs/bytewax.window) have a great explanation on windows.

Our builder function `new_array` will return a new, empty numpy array for each new key that it encounters. In the previous step, we set the key of each of our values to be the same string-**"data"**.

Our folder function `impute_value` receives new events, along with the accumulated values within a window. If the value is a `np.nan`, we use the `np.nanmean` function to calculate the mean of all of the current accumulated values. Lastly, we insert the new value into our numpy array and return it.

```python
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
```

### Output Code

Next up we will use the capture operator to write our code to an output source, in this case `StdOutput`. This is not going to do anything sophisticated, just output the data and the imputed value to standard output.

```python
flow.capture(StdOutput())
```

### Wrapping up

Now to put it all together and add in the execution method. In this case, we wan't a single, in process dataflow worker. So we use `run_main` as the execution method and provide it with the dataflow object.

```python
if __name__ == "__main__":
    run_main(flow)
```

That’s it! To run the code, run it like you would any ordinary Python script:

```bash
python dataflow.py
```

## Summary

In this example, we learned how to impute missing values from a datastream using Bytewax.

## We want to hear from you!

If you have any trouble with the process or have ideas about how to improve this document, come talk to us in the #troubleshooting Slack channel!

## Where to next?

- Relevant explainer video
- Relevant case study
- Relevant blog post
- Another awesome tutorial

See our full gallery of tutorials →

[Share your tutorial progress!](https://twitter.com/intent/tweet?text=I%27m%20mastering%20data%20streaming%20with%20%40bytewax!%20&url=https://bytewax.io/tutorials/&hashtags=Bytewax,Tutorials)
