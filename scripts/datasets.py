'''
Handle loading datasets.
'''

import random

import numpy

import util

DATASET_MNIST = 'mnist'
DATASET_EMNIST = 'emnist'  # Only letters.
DATASET_KMNIST = 'kmnist'
DATASET_FMNIST = 'fmnist'

DATASETS = [DATASET_MNIST, DATASET_EMNIST, DATASET_KMNIST, DATASET_FMNIST]

# Some metadata that we can get without loading the actual data.
NUM_LABELS = {
    DATASET_MNIST: 10,
    DATASET_EMNIST: 47,
    DATASET_KMNIST: 10,
    DATASET_FMNIST: 10,
}

# MNIST images are 28 x 28 = 784.
MNIST_DIMENSION = 28

SIGNIFICANT_DIGITS = 4

TF_DATASET_NAME = {
    DATASET_MNIST: 'mnist',
    DATASET_EMNIST: 'emnist/balanced',
    DATASET_KMNIST: 'kmnist',
    DATASET_FMNIST: 'fashion_mnist',
}

# Special case validations for classes.
LABEL_VALIDATION = {
    DATASET_EMNIST: lambda label: (label > 10)
}

# Special case transformations on each image.
IMAGE_TRANSFORMS = {
    DATASET_EMNIST: lambda image: numpy.transpose(image),
}

# Map labels to an string representation for what they represent.
LABEL_MAP = {
    'mnist_0': '0',
    'mnist_1': '1',
    'mnist_2': '2',
    'mnist_3': '3',
    'mnist_4': '4',
    'mnist_5': '5',
    'mnist_6': '6',
    'mnist_7': '7',
    'mnist_8': '8',
    'mnist_9': '9',

    # Incomplete
    'emnist_0': '00',
    'emnist_1': '01',
    'emnist_2': '02',
    'emnist_3': '03',
    'emnist_4': '04',
    'emnist_5': '05',
    'emnist_6': '06',
    'emnist_7': '07',
    'emnist_8': '08',
    'emnist_9': '09',
    'emnist_10': '10',
    'emnist_11': 'B',
    'emnist_12': 'C',
    'emnist_13': 'D',
    'emnist_14': 'E',
    'emnist_15': 'F',
    'emnist_16': 'G',
    'emnist_17': 'H',
    'emnist_18': 'I',
    'emnist_19': 'J',
    'emnist_20': 'K',
    'emnist_21': '21',
    'emnist_22': '22',
    'emnist_23': '23',
    'emnist_24': '24',
    'emnist_25': '25',
    'emnist_26': '26',
    'emnist_27': '27',
    'emnist_28': '28',
    'emnist_29': '29',
    'emnist_30': '30',
    'emnist_31': '31',
    'emnist_32': '32',
    'emnist_33': '33',
    'emnist_34': '34',
    'emnist_35': '35',
    'emnist_36': '36',
    'emnist_37': '37',
    'emnist_38': '38',
    'emnist_39': '39',
    'emnist_40': '40',
    'emnist_41': '41',
    'emnist_42': '42',
    'emnist_43': '43',
    'emnist_44': '44',
    'emnist_45': '45',
    'emnist_46': '46',

    'fmnist_0': 'T-Shirt/Top',
    'fmnist_1': 'Trouser',
    'fmnist_2': 'Pullover',
    'fmnist_3': 'Dress',
    'fmnist_4': 'Coat',
    'fmnist_5': 'Sandals',
    'fmnist_6': 'Shirt',
    'fmnist_7': 'Sneaker',
    'fmnist_8': 'Bag',
    'fmnist_9': 'Ankle Boots',

    'kmnist_0': 'お',
    'kmnist_1': 'き',
    'kmnist_2': 'す',
    'kmnist_3': 'つ',
    'kmnist_4': 'な',
    'kmnist_5': 'は',
    'kmnist_6': 'ま',
    'kmnist_7': 'や',
    'kmnist_8': 'れ',
    'kmnist_9': 'を',
}

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
        assert (self._nextIndexes[label] < len(self._examples[label])), 'Label: %s, Next Index: %d, Size: %d' % (label, self._nextIndexes[label], len(self._examples[label]))

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
        numTrain, numTest, numValid):
    allExamples, allowedLabels = loadMNIST(datasetName)

    requiredExamplesPerLabel = dimension * (numTrain + numTest + numValid)
    for label in allExamples:
        if (len(allExamples[label]) < requiredExamplesPerLabel):
            raise RuntimeError("Label (%s) from %s does not have enough examples. Want %d, have %d." % (str(label), datasetName, requiredExamplesPerLabel, len(allExamples[label])))

    trainExamples = {}
    testExamples = {}
    validExamples = {}

    usedExamples = 0

    for (examples, puzzleCount) in [(trainExamples, numTrain), (testExamples, numTest), (validExamples, numValid)]:
        exampleCount = puzzleCount * dimension
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
    Labels are turned into strings and prepended with the dataset name to avoid conflict with other datasets.

    Returns:
        {label: [image, ...], ...}
    '''

    # Delay importing tensorflow to avoid waits on already existing datasets.
    import tensorflow_datasets as tfds

    data = tfds.as_numpy(tfds.load(TF_DATASET_NAME[name], batch_size = -1, as_supervised = True))
    (trainImages, trainLabels) = data['train']
    (testImages, testLabels) = data['test']

    labels = []
    for label in sorted(set(trainLabels) | set(testLabels)):
        if (name not in LABEL_VALIDATION or LABEL_VALIDATION[name](label)):
            labels.append(name + '_' + str(label))

    # Remove the depth dimension.
    trainImages = trainImages.reshape((len(trainImages), MNIST_DIMENSION, MNIST_DIMENSION))
    testImages = testImages.reshape((len(testImages), MNIST_DIMENSION, MNIST_DIMENSION))

    trainImages = _normalizeMNISTImages(trainImages, name)
    testImages = _normalizeMNISTImages(testImages, name)

    # {label: [image, ...], ...}
    examples = {label: [] for label in labels}
    for i in range(len(trainImages)):
        label = name + '_' + str(trainLabels[i])
        if (label in labels):
            examples[label].append(trainImages[i])

    for i in range(len(testImages)):
        label = name + '_' + str(testLabels[i])
        if (label in labels):
            examples[label].append(testImages[i])

    if (shuffle):
        for label in labels:
            random.shuffle(examples[label])
            random.shuffle(examples[label])

    return examples, labels

def _normalizeMNISTImages(images, datasetName):
    (numImages, width, height) = images.shape

    if (datasetName in IMAGE_TRANSFORMS):
        for i in range(len(images)):
            images[i] = IMAGE_TRANSFORMS[datasetName](images[i])

    # Flatten out the images into a 1d array.
    images = images.reshape(numImages, width * height)

    # Normalize the greyscale intensity to [0,1].
    images = images / 255.0

    # Round so that the output is significantly smaller.
    images = images.round(SIGNIFICANT_DIGITS)

    return images
