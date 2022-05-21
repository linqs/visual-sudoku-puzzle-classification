#!/usr/bin/env python3

# Generate a split of puzzles.

import argparse
import os
import random
import shutil
import sys

import numpy

import datasets
import strategies
import util

DEFAULT_DATASET = datasets.DATASET_MNIST
DEFAULT_STRATEGY = strategies.getStrategies()[0]

DEFAULT_PUZZLE_DIM = 4
DEFAULT_NUM_TRAIN = 100
DEFAULT_NUM_TEST = 100
DEFAULT_NUM_VALID = 100
DEFAULT_OUT_DIR = 'data'
DEFAULT_OVERLAP_PERCENT = 0.0
DEFAULT_SPLIT = '00'
DEFAULT_TRAIN_PERCENT = 0.5

SUBPATH_FORMAT = os.path.join('dimension::{:01d}', 'datasets::{:s}', 'strategy::{:s}', 'numTrain::{:05d}', 'numTest::{:05d}', 'numValid::{:05d}', 'overlap::{:04.2f}', 'split::{:s}')
OPTIONS_FILENAME = 'options.json'

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
    allExamples, allowedLabels = datasets.loadMNIST(datasetName)

    trainExamples = {}
    testExamples = {}
    validExamples = {}

    usedExamples = 0

    for (examples, count) in [(trainExamples, numTrain), (testExamples, numTest), (validExamples, numValid)]:
        for label in allExamples:
            examples[label] = allExamples[label][usedExamples:(usedExamples + count)]
        usedExamples += count

    for examples in [trainExamples, testExamples, validExamples]:
        addOverlap(examples, overlapPercent)

    return allowedLabels, util.ExampleChooser(trainExamples), util.ExampleChooser(testExamples), util.ExampleChooser(validExamples)

def generateSplit(outDir, seed,
        dimension, datasetNames, 
        numTest, numTrain, numValid,
        overlapPercent, strategy):
    random.seed(seed)
    numpy.random.seed(seed)

    datasets = {}

    for datasetName in datasetNames:
        labels, trainExamples, testExamples, validExamples = fetchData(dimension, datasetName, overlapPercent, numTest, numTrain, numValid)
        datasets[datasetName] = {
            'labels': labels,
            'train': trainExamples,
            'test': testExamples,
            'valid': validExamples,
        }

    strategy.newSplit(dimension, datasets)

    print('TEST')
    print(datasets)
    print(strategy)
    print(strategy.labels)

def main(arguments):
    subpath = SUBPATH_FORMAT.format(
            arguments.dimension,
            ','.join(arguments.datasetNames),
            str(arguments.strategy),
            arguments.numTrain,
            arguments.numTest,
            arguments.numValid,
            arguments.overlapPercent,
            arguments.split)

    outDir = os.path.join(arguments.outDir, subpath)

    optionsPath = os.path.join(outDir, OPTIONS_FILENAME)
    if (os.path.isfile(optionsPath)):
        if (not arguments.force):
            print("Found existing split opions file, skipping generation. " + optionsPath)
            return

        print("Found existing options file, but forcing over it. " + optionsPath)
        shutil.rmtree(DATA_DIR.format(subpath))
    print("Generating data defined in: " + optionsPath)

    generateSplit(
            outDir, arguments.seed,
            arguments.dimension, arguments.datasetNames, 
            arguments.numTest, arguments.numTrain, arguments.numValid,
            arguments.overlapPercent, arguments.strategy)

def _load_args():
    parser = argparse.ArgumentParser(description = 'Generate custom visual sudoku puzzles.')

    parser.add_argument('--dataset', dest = 'datasetNames',
        action = 'append', default = None,
        help = 'The dataset to use for puzzle cells (can be specified multiple times). Defaults to "%s"' % (DEFAULT_DATASET))

    parser.add_argument('--dimension', dest = 'dimension',
        action = 'store', type = int, default = DEFAULT_PUZZLE_DIM,
        choices = [4, 9],
        help = 'Size of the square puzzle.')

    parser.add_argument('--force', dest = 'force',
        action = 'store_true', default = False,
        help = 'Ignore existing data directories and write over them.')

    parser.add_argument('--num-test', dest = 'numTest',
        action = 'store', type = int, default = DEFAULT_NUM_TEST,
        help = 'See --num-train, but for test.')

    parser.add_argument('--num-train', dest = 'numTrain',
        action = 'store', type = int, default = DEFAULT_NUM_TRAIN,
        help = 'The number of correct training puzzles to generate (the same number of negative puzzles will also be generated).')

    parser.add_argument('--num-valid', dest = 'numValid',
        action = 'store', type = int, default = DEFAULT_NUM_VALID,
        help = 'See --num-train, but for validation.')

    parser.add_argument('--overlap-percent', dest = 'overlapPercent',
        action = 'store', type = float, default = DEFAULT_OVERLAP_PERCENT,
        help = 'The percentage to add to the base dataset that comes from overlaps (e.g. a 1.0 overlap will double the size of the dataset.')

    parser.add_argument('--seed', dest = 'seed',
        action = 'store', type = int, default = None,
        help = 'Random seed.')

    parser.add_argument('--split', dest = 'split',
        action = 'store', type = str, default = DEFAULT_SPLIT,
        help = 'An identifier for this split.')

    parser.add_argument('--strategy', dest = 'strategy',
        action = 'store', type = str, default = str(DEFAULT_STRATEGY),
        choices = list(map(str, strategies.getStrategies())),
        help = 'The strategy to use when creating puzzles.')

    parser.add_argument('--out-dir', dest = 'outDir',
        action = 'store', type = str, default = DEFAULT_OUT_DIR,
        help = 'Where to create split directories.')

    arguments = parser.parse_args()

    if (arguments.datasetNames is None):
        arguments.datasetNames = [DEFAULT_DATASET]

    if (len(set(arguments.datasetNames)) != len(arguments.datasetNames)):
        print("Duplicate datasetNames specified: %s." % (arguments.datasetNames), file = sys.stderr)
        sys.exit(2)

    for datasetName in arguments.datasetNames:
        if (datasetName not in datasets.DATASETS):
            print("Unknown dataset specified: %s." % (datasetName), file = sys.stderr)
            sys.exit(2)

    arguments.datasetNames = list(sorted(set(arguments.datasetNames)))

    if (arguments.numTrain < 1 or arguments.numTest < 1 or arguments.numValid < 1):
        print("Number of puzzles must be >= 1, got: %d.")
        sys.exit(2)

    if (arguments.overlapPercent < 0.0):
        print("Overlap percent must be non-negative, got: %f." % (arguments.overlapPercent), file = sys.stderr)
        sys.exit(2)

    if (arguments.seed is None):
        arguments.seed = random.randrange(2 ** 32)

    arguments.strategy = strategies.getStrategy(arguments.strategy)
    arguments.strategy.validate(arguments)

    return arguments

if (__name__ == '__main__'):
    main(_load_args())
