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

    def validate(self, arguments):
        """
        Validate command-line arguments for this strategy.
        The arguments should have all defaults filled in.
        Throw if there are any incorrect configurations.
        """

        pass

    @abc.abstractmethod
    def generateSplit(self, dimension, data, corruptChance, numTrain, numTest, numValid):
        """
        Create a new split using the class' specific strategy.
        Returns three tuples: train, test, and valid.
        Each tuple has two elements: visual puzzles, label puzzles.
        """

        pass

    def _generateSplit(self, dimension, corruptChance, numTrain, numTest, numValid,
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
                # Generate a correct puzzle.

                puzzleImages, puzzleCellLabels = puzzles.generatePuzzle(dimension, labels, examples)

                split['images'].append(puzzleImages)
                split['cellLabels'].append(puzzleCellLabels)
                split['labels'].append(puzzles.PUZZLE_LABEL_CORRECT)
                split['notes'].append([puzzles.PUZZLE_NOTE_CORRRECT])

                # Corrupt a puzzle.

                corruptImages, corruptCellLabels, corruptNote = puzzles.corruptPuzzle(dimension, labels, examples, puzzleImages, puzzleCellLabels, corruptChance)

                split['images'].append(corruptImages)
                split['cellLabels'].append(corruptCellLabels)
                split['labels'].append(puzzles.PUZZLE_LABEL_INCORRECT)
                split['notes'].append([corruptNote])

        return train, test, valid

    def _mergeDatasets(self, data):
        labels = []
        trainExamples = {}
        testExamples = {}
        validExamples = {}

        for datasetName in data:
            labels.extend(data[datasetName]['labels'])
            trainExamples.update(data[datasetName]['train']._examples)
            testExamples.update(data[datasetName]['test']._examples)
            validExamples.update(data[datasetName]['valid']._examples)

        labels = list(sorted(set(labels)))
        trainExamples = datasets.ExampleChooser(trainExamples)
        testExamples = datasets.ExampleChooser(testExamples)
        validExamples = datasets.ExampleChooser(validExamples)

        return labels, trainExamples, testExamples, validExamples

    def __repr__(self):
        return self.name

class SimpleStrategy(BaseStrategy):
    """
    Use a single dataset, and just take the first |dimension| classes.
    """

    def __init__(self):
        super().__init__('simple')

    def validate(self, arguments):
        if (len(arguments.datasetNames) != 1):
            raise ValueError(
                    "%s (%s) can only be used with a single dataset, found [%s]." %
                    (type(self).__name__, self.name, ', '.join(arguments.datasetNames)))

    def generateSplit(self, dimension, data, corruptChance, numTrain, numTest, numValid):
        datasetName = list(data.keys())[0]
        dataset = data[datasetName]

        # Choose the first |dimension| labels.
        labels = dataset['labels'][0:dimension]

        return self._generateSplit(dimension, corruptChance, numTrain, numTest, numValid, labels,
                dataset['train'], dataset['test'], dataset['valid'])

class RandomSplitStrategy(BaseStrategy):
    """
    Choose |dimension| random classes from all datasets for the entire split.
    """

    def __init__(self):
        super().__init__('r_split')

    def generateSplit(self, dimension, data, corruptChance, numTrain, numTest, numValid):
        labels, trainExamples, testExamples, validExamples = self._mergeDatasets(data)

        labels = random.sample(labels, k = dimension)

        return self._generateSplit(dimension, corruptChance, numTrain, numTest, numValid, labels,
                trainExamples, testExamples, validExamples)

class RandomPuzzleStrategy(BaseStrategy):
    """
    Choose |dimension| random classes from all datasets for each puzzle.
    """

    def __init__(self):
        super().__init__('r_puzzle')

    def generateSplit(self, dimension, data, corruptChance, numTrain, numTest, numValid):
        baseLabels, trainExamples, testExamples, validExamples = self._mergeDatasets(data)

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

        # Reuse the same pool of labels from train for test/valid.
        seenLabels = set()

        for i in range(len(splits)):
            (split, count, examples) = splits[i]

            if (i != 0):
                seenLabels = list(sorted(seenLabels))

            for _ in range(count):
                if (i == 0):
                    labels = random.sample(baseLabels, k = dimension)
                    seenLabels.update(set(labels))
                else:
                    labels = random.sample(seenLabels, k = dimension)

                # Generate a correct puzzle.

                puzzleImages, puzzleCellLabels = puzzles.generatePuzzle(dimension, labels, examples)

                split['images'].append(puzzleImages)
                split['cellLabels'].append(puzzleCellLabels)
                split['labels'].append(puzzles.PUZZLE_LABEL_CORRECT)
                split['notes'].append([puzzles.PUZZLE_NOTE_CORRRECT])

                # Corrupt a puzzle.

                corruptImages, corruptCellLabels, corruptNote = puzzles.corruptPuzzle(dimension, labels, examples, puzzleImages, puzzleCellLabels, corruptChance)

                split['images'].append(corruptImages)
                split['cellLabels'].append(corruptCellLabels)
                split['labels'].append(puzzles.PUZZLE_LABEL_INCORRECT)
                split['notes'].append([corruptNote])

        return train, test, valid

class RandomCellStrategy(BaseStrategy):
    """
    Use all available classes (more than |dimension|) for every cell.
    """

    def __init__(self):
        super().__init__('r_cell')

    def generateSplit(self, dimension, data, corruptChance, numTrain, numTest, numValid):
        baseLabels, trainExamples, testExamples, validExamples = self._mergeDatasets(data)

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

        # Reuse the same pool of labels from train for test/valid.
        seenLabels = set()

        for i in range(len(splits)):
            (split, count, examples) = splits[i]

            if (i == 0):
                labels = baseLabels
            else:
                labels = list(sorted(seenLabels))

            for _ in range(count):
                # Generate a correct puzzle.

                puzzleImages, puzzleCellLabels = puzzles.generatePuzzle(dimension, labels, examples)

                split['images'].append(puzzleImages)
                split['cellLabels'].append(puzzleCellLabels)
                split['labels'].append(puzzles.PUZZLE_LABEL_CORRECT)
                split['notes'].append([puzzles.PUZZLE_NOTE_CORRRECT])

                # Corrupt a puzzle.

                corruptImages, corruptCellLabels, corruptNote = puzzles.corruptPuzzle(dimension, labels, examples, puzzleImages, puzzleCellLabels, corruptChance)

                split['images'].append(corruptImages)
                split['cellLabels'].append(corruptCellLabels)
                split['labels'].append(puzzles.PUZZLE_LABEL_INCORRECT)
                split['notes'].append([corruptNote])

                if (i == 0):
                    # Keep track of all the labels we have seen.
                    seenLabels.update(set([label for row in puzzleCellLabels for label in row]))
                    seenLabels.update(set([label for row in corruptCellLabels for label in row]))

        return train, test, valid

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

    def generateSplit(self, dimension, data, corruptChance, numTrain, numTest, numValid):
        datasetName = list(data.keys())[0]
        dataset = data[datasetName]

        labels = dataset['labels'].copy()
        random.shuffle(labels)

        trainLabels = labels[0:dimension]
        testLabels = labels[dimension:(dimension * 2)]

        train, _, _ = self._generateSplit(dimension, corruptChance, numTrain, 0, 0, trainLabels, dataset['train'], None, None)
        _, test, valid = self._generateSplit(dimension, corruptChance, 0, numTest, numValid, testLabels, None, dataset['test'], dataset['valid'])

        return train, test, valid
