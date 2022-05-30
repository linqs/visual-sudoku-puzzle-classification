#!/usr/bin/env python3

# Get an image of a datatse.
# Note that this script may not work for you because of the font choice.
# You need a font that has both Latin and Japanese characters.

import argparse
import os

import matplotlib.pyplot
import numpy

import datasets

DEFAULT_MAX_CLASSES = 10
DEFAULT_NUM_EXAMPLES = 5

# Replace with a local font that has Japanese characters.
FONT_FAMILY = 'Source Han Sans TW'

DEFAULT_FONT_PROPERTIES = {
    'fontfamily': FONT_FAMILY,
    'fontsize': 36,
}

FONT_PROPERTIES = {
    'mnist': DEFAULT_FONT_PROPERTIES,
    'emnist': DEFAULT_FONT_PROPERTIES,
    'fmnist': {
        'fontfamily': FONT_FAMILY,
        'fontsize': 24,
        'rotation': 45,
        'horizontalalignment': 'center',
    },
    'kmnist': DEFAULT_FONT_PROPERTIES,
}

def generateDatasetImage(datasetName, outDir, maxClasses, numExamples, show):
    outPath = os.path.join(outDir, "%s-examples.png" % (datasetName))
    numClasses = min(maxClasses, datasets.NUM_LABELS[datasetName])

    labels, examples, _, _ = datasets.fetchData(9, datasetName, 0.0, 100, 0, 0)
    image = []

    # Use ticks for show the class labels.
    tickInitialOffset = datasets.MNIST_DIMENSION // 2
    xTickPositions = [tickInitialOffset + i * datasets.MNIST_DIMENSION for i in range(numClasses)]
    xTickLabels = [datasets.LABEL_MAP[labels[i]] for i in range(numClasses)]

    for i in range(numClasses):
        label = labels[i]

        column = []
        for _ in range(numExamples):
            example = examples.takeExample(label).reshape((datasets.MNIST_DIMENSION, datasets.MNIST_DIMENSION))
            column.append(example)

        column = numpy.stack(column)
        column = column.reshape((datasets.MNIST_DIMENSION * numExamples, datasets.MNIST_DIMENSION))

        image.append(column)

    image = numpy.stack(image, axis = 1)
    image = image.reshape((datasets.MNIST_DIMENSION * numExamples, datasets.MNIST_DIMENSION * numClasses))

    figure, axis = matplotlib.pyplot.subplots()

    axis.imshow(image, cmap = 'gray_r')

    # matplotlib.pyplot.axis('off')
    axis.get_yaxis().set_visible(False)

    axis.set_xticks(xTickPositions, xTickLabels, **FONT_PROPERTIES[datasetName])
    axis.tick_params(top = True, labeltop = True, bottom = False, labelbottom = False, length = 0)

    axis.spines['right'].set_visible(False)
    axis.spines['left'].set_visible(False)
    axis.spines['bottom'].set_visible(False)

    figure.set_figwidth(10)
    figure.set_figheight(7)

    figure.tight_layout()
    figure.savefig(outPath)

    if (show):
        matplotlib.pyplot.show()

def main(arguments):
    os.makedirs(arguments.outDir, exist_ok = True)

    for datasetName in datasets.DATASETS:
        generateDatasetImage(datasetName, arguments.outDir, arguments.maxClasses, arguments.numExamples, arguments.show)

def _load_args():
    parser = argparse.ArgumentParser(description = 'Generate an image for each dataset.')

    parser.add_argument('outDir',
        action = 'store', type = str,
        help = 'The directory to put the generated images in.')

    parser.add_argument('--max-classes', dest = 'maxClasses',
        action = 'store', type = int, default = DEFAULT_MAX_CLASSES,
        help = 'The maximum number of classes to show per dataset.')

    parser.add_argument('--num-examples', dest = 'numExamples',
        action = 'store', type = int, default = DEFAULT_NUM_EXAMPLES,
        help = 'The number of examples to show per class.')

    parser.add_argument('--no-show', dest = 'show',
        action = 'store_false', default = True,
        help = "Don't pop a window up showing the puzzle.")

    arguments = parser.parse_args()
    return arguments

if (__name__ == '__main__'):
    main(_load_args())
