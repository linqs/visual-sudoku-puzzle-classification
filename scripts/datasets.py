'''
Handle loading datasets.
'''

import random

import util

DATASET_MNIST = 'mnist'
DATASET_EMNIST = 'emnist'
DATASET_KMNIST = 'kmnist'
DATASET_FMNIST = 'fashion_mnist'

DATASETS = [DATASET_MNIST, DATASET_EMNIST, DATASET_KMNIST, DATASET_FMNIST]

# MNIST images are 28 x 28 = 784.
MNIST_DIMENSION = 28

SIGNIFICANT_DIGITS = 4

class ExampleChooser(object):
    '''
    An object for controlling exactly how many instances of each label are used to create puzzles.
    '''

    # examples: {label: [image, ...], ...}
    def __init__(self, examples):
        self._examples = examples
        self._nextIndexes = {label: 0 for label in examples}

    # Takes (consumes) the next example for a label.
    def takeExample(self, label):
        assert(self._nextIndexes[label] < len(self._examples[label]))

        image = self._examples[label][self._nextIndexes[label]]
        self._nextIndexes[label] += 1
        return image

    # Get a example randomly from anywhere in the sequence.
    def getExample(self, label):
        return random.choice(self._examples[label])

def addOverlap(examples, overlapPercent):
    if (overlapPercent <= 0.0):
        return

    for label in examples:
        overlapCount = int(len(examples[label]) * overlapPercent)
        overlap = random.choices(examples[label], k = overlapCount)
        examples[label].extend(overlap)
        random.shuffle(examples[label])

def fetchData(dimension, datasetName, overlapPercent,
        numTest, numTrain, numValid):
    allExamples, allowedLabels = loadMNIST(datasetName)

    trainExamples = {}
    testExamples = {}
    validExamples = {}

    usedExamples = 0

    for (examples, puzzleCount) in [(trainExamples, numTrain), (testExamples, numTest), (validExamples, numValid)]:
        exampleCount = puzzleCount * (dimension ** 2)
        for label in allExamples:
            examples[label] = allExamples[label][usedExamples:(usedExamples + exampleCount)]
        usedExamples += exampleCount

    for examples in [trainExamples, testExamples, validExamples]:
        addOverlap(examples, overlapPercent)

    return allowedLabels, ExampleChooser(trainExamples), ExampleChooser(testExamples), ExampleChooser(validExamples)

def loadMNIST(name = DATASET_MNIST, shuffle = True):
    '''
    Load an MNIST-style dataset (with MNIST_DIMENSION square images).
    Train and test are combined into the same structures.

    Returns:
        {label: [image, ...], ...}
    '''

    # Delay importing tensorflow to avoid waits on already existing datasets.
    import tensorflow_datasets as tfds

    data = tfds.as_numpy(tfds.load(name, batch_size = -1, as_supervised = True))
    (trainImages, trainLabels) = data['train']
    (testImages, testLabels) = data['test']

    labels = list(sorted(set(testLabels)))

    # Remove the depth dimension.
    trainImages = trainImages.reshape((len(trainImages), MNIST_DIMENSION, MNIST_DIMENSION))
    testImages = testImages.reshape((len(testImages), MNIST_DIMENSION, MNIST_DIMENSION))

    trainImages = _normalizeMNISTImages(trainImages)
    testImages = _normalizeMNISTImages(testImages)

    # {label: [image, ...], ...}
    examples = {label: [] for label in labels}
    for i in range(len(trainImages)):
        examples[int(trainLabels[i])].append(trainImages[i])

    for i in range(len(testImages)):
        examples[int(testLabels[i])].append(testImages[i])

    if (shuffle):
        for label in labels:
            random.shuffle(examples[label])
            random.shuffle(examples[label])

    return examples, labels

def _normalizeMNISTImages(images):
    (numImages, width, height) = images.shape

    # Flatten out the images into a 1d array.
    images = images.reshape(numImages, width * height)

    # Normalize the greyscale intensity to [0,1].
    images = images / 255.0

    # Round so that the output is significantly smaller.
    images = images.round(SIGNIFICANT_DIGITS)

    return images
