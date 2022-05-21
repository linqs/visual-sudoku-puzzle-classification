"""
Handle the standard variants for dataset generation.
"""

import abc

# Will be added to as the strategies are defined.
_strategies = []

def getStrategies():
    return _strategies

def getStrategy(name):
    for strategy in _strategies:
        if (strategy.name == name):
            return strategy

    raise ValueError("Unknown strategy '%s'. Known strategies: [%s]." % (name, ", ".join(map(str, _strategies))))

class BaseStrategy(abc.ABC):
    """
    Strategies represent the methods we use to generate data for different variants of the dataset.
    Strategies will generally handle choosing which labels to use for each location.
    Strategies are not thread-safe.
    """

    def __init__(self, name):
        self.name = name

        self.dimension = None
        self.datasets = None

    def __init_subclass__(cls, **kwargs):
        _strategies.append(cls())

    @abc.abstractmethod
    def validate(self, arguments):
        """
        Validate command-line arguments for this strategy.
        The arguments should have all defaults filled in.
        Throw if there are any incorrect configurations.
        """

        pass

    def newSplit(self, dimension, datasets):
        """
        Prepare for a new split.
        """

        self.dimension = dimension
        self.datasets = datasets

    def __repr__(self):
        return self.name

class SimpleStrategy(BaseStrategy):
    def __init__(self):
        super().__init__('simple')

        self.labels = None

    def validate(self, arguments):
        if (len(arguments.datasetNames) != 1):
            raise ValueError(
                    "%s (%s) can only be used with a single dataset, found [%s]." %
                    (type(self).__name__, self.name, ', '.join(arguments.datasetNames)))

    def newSplit(self, dimension, datasets):
        super().newSplit(dimension, datasets)

        datasetName = list(datasets.keys())[0]
        labels = datasets[datasetName]['labels']
        self.labels = labels[0:dimension]
