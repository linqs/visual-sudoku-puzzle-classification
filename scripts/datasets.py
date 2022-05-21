'''
Handle loading datasets.
'''

import random

import numpy

DATASET_MNIST = 'mnist'
DATASET_EMNIST = 'emnist'
DATASET_KMNIST = 'knist'
DATASET_FMNIST = 'fashion_mnist'

DATASETS = [DATASET_MNIST, DATASET_EMNIST, DATASET_KMNIST, DATASET_FMNIST]

# MNIST images are 28 x 28 = 784.
MNIST_DIMENSION = 28

SIGNIFICANT_DIGITS = 4

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

    return examples

def _normalizeMNISTImages(images):
    (numImages, width, height) = images.shape

    # Flatten out the images into a 1d array.
    images = images.reshape(numImages, width * height)

    # Normalize the greyscale intensity to [0,1].
    images = images / 255.0

    # Round so that the output is significantly smaller.
    images = images.round(SIGNIFICANT_DIGITS)

    return images
