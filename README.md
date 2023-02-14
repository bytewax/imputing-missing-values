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

*Learn how to create a custom sliding window with stateful map to impute values using numpy*

## Resources

[Github link](https://github.com/bytewax/imputing-missing-values)

### Input Code

Bytewax is based around the concepts of a dataflow. A dataflow is made up of a sequence of operators that interact with data that is “flowing” through. For more information, please [check out the documentation.](https://bytewax.io/docs)

To start we create a dataflow object and then we can add an input. The input is based off of a python generator. In our case, we will mock up some "live" data that will yield a numpy nan value for every 5th item in a loop. Otherwise it will yield an integer between 0 and 10.

We will use this generator function to create a stream of random data points.

When the Bytewax process starts it will call our function `random_datapoints` on each worker, 1 in this instance. The type of input is specified in the `bytewax.Dataflow.input` method and we are using the `ManualInputConfig` for our custom input.

### Custom Window Using Stateful Map

Before we dive into the code, it is important to understand the stateful map operator. Stateful map is a one-to-one transformation of values in (key, value) pairs, but allows you to reference a persistent state for each key when doing the transformation. The stateful map operator has two parts to it: a `builder` function and a `mapper` function. The `builder` function will get evoked for each new key and the `mapper` will get called for every new data point. For more information on how this works, [the api docs](https://bytewax.io/apidocs/bytewax.dataflow#bytewax.dataflow.Dataflow.stateful_map) have a great explanation.

```python
flow.stateful_map("windowed_array", lambda: WindowedArray(10), WindowedArray.impute_value)
```

In our case our key will be the same for the entire stream because we only have one stream of data in this example. So, we have some code that will create a `WindowedArray` object in the builder function and then use the update function to impute the mean.

```python
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
```

Let’s unpack the code. When our class `WindowedArray` is initialized, it will create an empty Numpy array with dtype of object.The reason the the object datatype is that this will allow us to add both integers and Nan values. For each new data point that we receive, we will instruct the stateful map operator to use the impute_value method that will check if the value is nan and then calculate the mean from the last `n` objects, `n` being the size of array of values we've "remembered". In other words, how many of the values we care about and want to use in our calculation. this will vary on the application itself. It will also add the value to our window (last_n).

### Output Code

Next up we will use the capture operator to write our code to an output source, in this case `StdOutputConfig`. This is not going to do anything sophisticated, just output the data and the imputed value to standard output.

```python
flow.capture(StdOutputConfig())
```

### Wrapping up

Now to put it all together and add in the execution method. In this case, we wan't a single, in process dataflow worker. So we use `run_main` as the execution method and provide it with the dataflow object.

```python
if __name__ == "__main__":
    run_main(flow)
```

That’s it! To run the code simply run it like an ordinary python file on your machine.

```bash
python dataflow.py
```

## Summary

That’s it, you are awesome and we are going to rephrase our takeaway paragraph

## We want to hear from you!

If you have any trouble with the process or have ideas about how to improve this document, come talk to us in the #troubleshooting Slack channel!

## Where to next?

- Relevant explainer video
- Relevant case study
- Relevant blog post
- Another awesome tutorial

See our full gallery of tutorials →

[Share your tutorial progress!](https://twitter.com/intent/tweet?text=I%27m%20mastering%20data%20streaming%20with%20%40bytewax!%20&url=https://bytewax.io/tutorials/&hashtags=Bytewax,Tutorials)
