#!/usr/bin/env python3

# Generate a split of puzzles.

import argparse
import datetime
import json
import os
import random
import shutil
import sys

import datasets
import strategies
import puzzles
import util

DEFAULT_DATASET = datasets.DATASET_MNIST
DEFAULT_STRATEGY = strategies.getStrategies()[0]

DEFAULT_CORRUPT_CHANCE = 0.5
DEFAULT_PUZZLE_DIM = 4
DEFAULT_NUM_TRAIN = 100
DEFAULT_NUM_TEST = 100
DEFAULT_NUM_VALID = 100
DEFAULT_OUT_DIR = 'data'
DEFAULT_OVERLAP_PERCENT = 0.0
DEFAULT_SPLIT = '00'
DEFAULT_TRAIN_PERCENT = 0.5

SUBPATH_FORMAT = os.path.join('dimension::{:01d}', 'datasets::{:s}', 'strategy::{:s}',
        'numTrain::{:05d}', 'numTest::{:05d}', 'numValid::{:05d}',
        'corruptChance::{:04.2f}', 'overlap::{:04.2f}', 'split::{:s}')
OPTIONS_FILENAME = 'options.json'

CELL_LABELS_FILENAME = 'cell_labels.txt'
PUZZLE_PIXELS_FILENAME = 'puzzle_pixels.txt'
PUZZLE_LABELS_FILENAME = 'puzzle_labels.txt'
PUZZLE_NOTES_FILENAME = 'puzzle_notes.txt'

def writeData(outDir, puzzles, prefix):
    basePath = os.path.join(outDir, prefix)

    images = []
    cellLabels = []

    # Flatten the puzzles for writing.
    for i in range(len(puzzles['labels'])):
        images.append([pixel for row in puzzles['images'][i] for cell in row for pixel in cell])
        cellLabels.append([cell for row in puzzles['cellLabels'][i] for cell in row])

    util.writeRows(basePath + '_' + PUZZLE_PIXELS_FILENAME, images)
    util.writeRows(basePath + '_' + CELL_LABELS_FILENAME, cellLabels)
    util.writeRows(basePath + '_' + PUZZLE_LABELS_FILENAME, puzzles['labels'])
    util.writeRows(basePath + '_' + PUZZLE_NOTES_FILENAME, puzzles['notes'])

def generateSplit(outDir, seed,
        dimension, datasetNames, 
        numTrain, numTest, numValid,
        corruptChance, overlapPercent, strategy):
    random.seed(seed)

    data = {}
    for datasetName in datasetNames:
        labels, trainExamples, testExamples, validExamples = datasets.fetchData(dimension, datasetName, overlapPercent, numTrain, numTest, numValid)
        data[datasetName] = {
            'labels': labels,
            'train': trainExamples,
            'test': testExamples,
            'valid': validExamples,
        }

    train, test, valid = strategy.generateSplit(dimension, data, corruptChance, numTrain, numTest, numValid)

    writeData(outDir, train, 'train')
    writeData(outDir, test, 'test')
    writeData(outDir, valid, 'valid')

def main(arguments):
    subpath = SUBPATH_FORMAT.format(
            arguments.dimension,
            ','.join(arguments.datasetNames),
            str(arguments.strategy),
            arguments.numTrain,
            arguments.numTest,
            arguments.numValid,
            arguments.corruptChance,
            arguments.overlapPercent,
            arguments.split)

    outDir = os.path.join(arguments.outDir, subpath)

    optionsPath = os.path.join(outDir, OPTIONS_FILENAME)
    if (os.path.isfile(optionsPath)):
        if (not arguments.force):
            print("Found existing split opions file, skipping generation. " + optionsPath)
            return

        print("Found existing options file, but forcing over it. " + optionsPath)
        shutil.rmtree(outDir)

    print("Generating data defined in: " + optionsPath)
    os.makedirs(outDir, exist_ok = True)

    generateSplit(
            outDir, arguments.seed,
            arguments.dimension, arguments.datasetNames, 
            arguments.numTrain, arguments.numTest, arguments.numValid,
            arguments.corruptChance, arguments.overlapPercent, arguments.strategy)

    options = {
        'dimension': arguments.dimension,
        'datasets': arguments.datasetNames,
        'strategy': str(arguments.strategy),
        'numTrain': arguments.numTrain,
        'numTest': arguments.numTest,
        'numValid': arguments.numValid,
        'corruptChance': arguments.corruptChance,
        'overlap': arguments.overlapPercent,
        'splitId': arguments.split,
        'seed': arguments.seed,
        'timestamp': str(datetime.datetime.now()),
        'generator': os.path.basename(os.path.realpath(__file__)),
    }

    with open(optionsPath, 'w') as file:
        json.dump(options, file, indent = 4)

def _load_args():
    parser = argparse.ArgumentParser(description = 'Generate custom visual sudoku puzzles.')

    parser.add_argument('--corrupt-chance', dest = 'corruptChance',
        action = 'store', type = float, default = DEFAULT_CORRUPT_CHANCE,
        help = 'The chance to continue to make another corruption after one has been made.')

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

    if (arguments.corruptChance < 0.0 or arguments.corruptChance >= 1.0):
        print("Corrupt chance must be in [0, 1), got: %f." % (arguments.corruptChance), file = sys.stderr)
        sys.exit(2)

    if (arguments.seed is None):
        arguments.seed = random.randrange(2 ** 32)

    arguments.strategy = strategies.getStrategy(arguments.strategy)
    arguments.strategy.validate(arguments)

    return arguments

if (__name__ == '__main__'):
    main(_load_args())
