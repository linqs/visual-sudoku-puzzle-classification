#!/usr/bin/env python3

# Get an image of a puzzle.

import argparse
import os
import re

import matplotlib.pyplot

import datasets

def readPuzzle(path, index):
    count = 0

    with open(path, 'r') as file:
        for line in file:
            line = line.strip()
            if (line == ''):
                continue

            if (count != index):
                count += 1
                continue

            return list(map(float, line.split("\t")))

def main(arguments):
    dimension = arguments.dimension
    if (dimension is None):
        for (key, value) in re.findall(r'([\w\-\.]+)::([\w\-\.]+)', arguments.path):
            if (key == 'dimension'):
                dimension = int(value)
                break

        if (dimension is None):
            raise RuntimeError('Could not figure out the puzzle dimensions. Please specify --dimension.')

    imageDimension = datasets.MNIST_DIMENSION * dimension

    pixels = readPuzzle(arguments.path, arguments.index)

    puzzle = [[None] * imageDimension for _ in range(imageDimension)]

    # Map the pixels as a list back to a grid.
    # Note that the list version is stored one image at a time.
    for puzzleRow in range(dimension):
        for puzzleCol in range(dimension):
            puzzleIndex = (puzzleRow * dimension) + puzzleCol

            for cellRow in range(datasets.MNIST_DIMENSION):
                for cellCol in range(datasets.MNIST_DIMENSION):
                    cellIndex = (cellRow * datasets.MNIST_DIMENSION) + cellCol

                    pixelIndex = (puzzleIndex * (datasets.MNIST_DIMENSION ** 2)) + cellIndex

                    pixelRow = (puzzleRow * datasets.MNIST_DIMENSION) + cellRow
                    pixelCol = (puzzleCol * datasets.MNIST_DIMENSION) + cellCol

                    puzzle[pixelRow][pixelCol] = pixels[pixelIndex]

    matplotlib.pyplot.imshow(puzzle, cmap = 'gray_r')
    matplotlib.pyplot.axis('off')

    if (arguments.show):
        matplotlib.pyplot.show()

    if (arguments.outPath):
        matplotlib.pyplot.savefig(arguments.outPath)

def _load_args():
    parser = argparse.ArgumentParser(description = 'Generate an image for a puzzle in *_puzzle_pixels.txt file.')

    parser.add_argument('path',
        action = 'store', type = str,
        help = 'The path to the _puzzle_pixels.txt file.')

    parser.add_argument('--dimension', dest = 'dimension',
        action = 'store', type = int, default = None,
        help = 'The dimension of the puzzle. If not specified, it will be lifted from the path.')

    parser.add_argument('--index', dest = 'index',
        action = 'store', type = int, default = 0,
        help = 'The index of the puzzle to visualize.')

    parser.add_argument('--no-show', dest = 'show',
        action = 'store_false', default = True,
        help = "Don't pop a window up showing the puzzle.")

    parser.add_argument('--out-path', dest = 'outPath',
        action = 'store', type = str, default = None,
        help = 'Where to save an image of the puzzle (no image will be saved if not specified).')

    arguments = parser.parse_args()
    return arguments

if (__name__ == '__main__'):
    main(_load_args())
