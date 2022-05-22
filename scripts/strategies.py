"""
Handle the standard variants for dataset generation.
"""

import abc
import copy
import random

import datasets
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
    def generateSplit(self, dimension, data, numTrain, numTest, numValid):
        """
        Create a new split using the class' specific strategy.
        Returns three tuples: train, test, and valid.
        Each tuple has two elements: visual puzzles, label puzzles.
        """

        pass

    def _generateSplit(self, dimension, numTrain, numTest, numValid,
            labels, trainExamples, testExamples, validExamples):
        """
        A common base for generating splits.
        """

        train = {
            'images': [],
            'cellLabels': [],
            'labels': [],
            'notes': [],
        }
        test = copy.deepcopy(train)
        valid = copy.deepcopy(train)

        splits = [
            [train, numTrain, trainExamples],
            [test, numTest, testExamples],
            [valid, numValid, validExamples],
        ]

        for (split, count, examples) in splits:
            for i in range(count):
                puzzleImages, puzzleCellLabels = puzzles.generatePuzzle(dimension, labels, examples)

                split['images'].append(puzzleImages)
                split['cellLabels'].append(puzzleCellLabels)
                split['labels'].append(puzzles.PUZZLE_LABEL_CORRECT)
                split['notes'].append([puzzles.PUZZLE_NOTE_CORRRECT])

        return train, test, valid

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

    def generateSplit(self, dimension, data, numTrain, numTest, numValid):
        datasetName = list(data.keys())[0]
        dataset = data[datasetName]

        # Choose the first |dimension| labels.
        labels = dataset['labels'][0:dimension]

        return self._generateSplit(dimension, numTrain, numTest, numValid, labels,
                dataset['train'], dataset['test'], dataset['valid'])

class TransferStrategy(BaseStrategy):
    """
    A transfer learning strategy where the train and test/valid have different sets of labels.
    Note that test/valid will share the same label set,
    since MNIST only has 10 classes (and we would need 12 otherwise).
    """

    def __init__(self):
        super().__init__('transfer')

    def validate(self, arguments):
        if (len(arguments.datasetNames) != 1):
            raise ValueError(
                    "%s (%s) can only be used with a single dataset, found [%s]." %
                    (type(self).__name__, self.name, ', '.join(arguments.datasetNames)))

        datasetName = arguments.datasetNames[0]

        if (datasets.NUM_LABELS[datasetName] < (arguments.dimension * 2)):
            raise ValueError(
                    "%s (%s) does not have enough labels. Need %d, found %d." %
                    (type(self).__name__, self.name, (arguments.dimension * 2), datasets.NUM_LABELS[datasetName]))

    def generateSplit(self, dimension, data, numTrain, numTest, numValid):
        datasetName = list(data.keys())[0]
        dataset = data[datasetName]

        labels = dataset['labels'].copy()
        random.shuffle(labels)

        trainLabels = labels[0:dimension]
        testLabels = labels[dimension:(dimension * 2)]

        train, _, _ = self._generateSplit(dimension, numTrain, 0, 0, trainLabels, dataset['train'], None, None)
        _, test, valid = self._generateSplit(dimension, 0, numTest, numValid, testLabels, None, dataset['test'], dataset['valid'])

        return train, test, valid
