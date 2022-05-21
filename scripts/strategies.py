"""
Handle the standard variants for dataset generation.
"""

import abc
import copy

import puzzles

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

    @abc.abstractmethod
    def generateSplit(self, dimension, datasets, numTrain, numTest, numValid):
        """
        Create a new split using the class' specific strategy.
        Returns three tuples: train, test, and valid.
        Each tuple has two elements: visual puzzles, label puzzles.
        """

        pass

    def __repr__(self):
        return self.name

class SimpleStrategy(BaseStrategy):
    def __init__(self):
        super().__init__('simple')

    def validate(self, arguments):
        if (len(arguments.datasetNames) != 1):
            raise ValueError(
                    "%s (%s) can only be used with a single dataset, found [%s]." %
                    (type(self).__name__, self.name, ', '.join(arguments.datasetNames)))

    def generateSplit(self, dimension, datasets, numTrain, numTest, numValid):
        datasetName = list(datasets.keys())[0]

        # Choose the first |dimension| labels.
        labels = datasets[datasetName]['labels'][0:dimension]

        train = {
            'images': [],
            'cellLabels': [],
            'labels': [],
            'notes': [],
        }
        test = copy.deepcopy(train)
        valid = copy.deepcopy(train)

        splits = [
            [train, numTrain, datasets[datasetName]['train']],
            [test, numTest, datasets[datasetName]['test']],
            [valid, numValid, datasets[datasetName]['valid']]
        ]

        for (split, count, examples) in splits:
            for i in range(count):
                puzzleImages, puzzleCellLabels = puzzles.generatePuzzle(dimension, labels, examples)

                split['images'].append(puzzleImages)
                split['cellLabels'].append(puzzleCellLabels)
                split['labels'].append(puzzles.PUZZLE_LABEL_CORRECT)
                split['notes'].append([puzzles.PUZZLE_NOTE_CORRRECT])

        return train, test, valid
