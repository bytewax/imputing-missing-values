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

In this example, we're creating an input class based on the `StatelessSource` base class. `StatelessSource` only requires that we define the `next` method that will return the next item for Bytewax to process.

Lastly, we'll need to create a subclass of `DynamicInput` to return our `RandomNumpyData` class.

https://github.com/bytewax/imputing-missing-values/blob/main/dataflow.py#L14-L43


### Creating Windows Using `fold_window`

We'll be using the [fold_window](https://bytewax.io/apidocs/bytewax.dataflow#bytewax.dataflow.Dataflow.fold_window) operator to create 10 second windows of our event. The fold window operator has two parts to it: a `builder` function and a `folder` function. The `builder` function will get invoked for each new key, and the `folder` will get called for every new data point. For more information on how this works, [the api docs](https://bytewax.io/apidocs/bytewax.window) have a great explanation on windows.

Our builder function `new_array` will return a new, empty numpy array for each new key that it encounters. In the previous step, we set the key of each of our values to be the same string-**"data"**.

Our folder function `impute_value` receives new events, along with the accumulated values within a window. If the value is a `np.nan`, we use the Numpy `nanmean` function to calculate the mean of all of the current accumulated values. Lastly, we insert the new value into our numpy array and return it.

https://github.com/bytewax/imputing-missing-values/blob/main/dataflow.py#L47-L68

### Output Code

Next up we will use the capture operator to write our code to an output source, in this case `StdOutput`. This is not going to do anything sophisticated, just output the data and the imputed value to standard output.

https://github.com/bytewax/imputing-missing-values/blob/main/dataflow.py#L70

### Running our dataflow

That’s it! To run the code, use the following invocation:

```bash
> python -m bytewax.run dataflow:flow
```

## Summary

In this example, we learned how to impute missing values from a datastream using Bytewax.

## We want to hear from you!

If you have any trouble with the process or have ideas about how to improve this document, come talk to us in the #troubleshooting Slack channel!

[Share your tutorial progress!](https://twitter.com/intent/tweet?text=I%27m%20mastering%20data%20streaming%20with%20%40bytewax!%20&url=https://bytewax.io/tutorials/&hashtags=Bytewax,Tutorials)
