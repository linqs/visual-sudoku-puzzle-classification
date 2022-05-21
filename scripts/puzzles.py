"""
Handle puzzle creation and utils.
"""

import math
import random

PUZZLE_LABEL_CORRECT = [1, 0]
PUZZLE_LABEL_INCORRECT = [0, 1]

PUZZLE_NOTE_CORRRECT = 'solved'

def generatePuzzle(dimension, labels, exampleChooser):
    """
    Generate a valid puzzle and return the visual (pixel) and label representation for it.
    """

    puzzleImages = None
    puzzleCellLabels = None

    while (puzzleImages is None):
        puzzleImages, puzzleCellLabels = _generatePuzzle(dimension, labels, exampleChooser)

    return puzzleImages, puzzleCellLabels

def _generatePuzzle(dimension, labels, exampleChooser):
    """
    Generate a puzzle, but return (None, None) on failure.
    Failure can be encountered because this does not backtrack.
    Instead, just call again until you get a valid puzzle.
    """

    puzzleImages = [[None] * dimension for i in range(dimension)]
    puzzleCellLabels = [[None] * dimension for i in range(dimension)]

    # Keep track of the possible options for each location.
    # [row][col][label].
    # Remove options as we add to the puzzle.
    options = [[list(labels) for j in range(dimension)] for i in range(dimension)]

    blockSize = int(math.sqrt(dimension))

    for row in range(dimension):
        for col in range(dimension):
            if (len(options[row][col]) == 0):
                # Failed to create a puzzle, try again.
                return None, None

            label = random.choice(options[row][col])
            options[row][col].clear()

            puzzleCellLabels[row][col] = label

            blockRow = row // blockSize
            blockCol = col // blockSize

            # Remove the chosen label from row/col/grid options.
            for i in range(dimension):
                if label in options[i][col]:
                    options[i][col].remove(label)

                if label in options[row][i]:
                    options[row][i].remove(label)

                for j in range(dimension):
                    if (i // blockSize == blockRow and j // blockSize == blockCol):
                        if label in options[i][j]:
                            options[i][j].remove(label)

    # Once we have a complete puzzle, choose the examples.
    for row in range(dimension):
        for col in range(dimension):
            puzzleImages[row][col] = exampleChooser.takeExample(puzzleCellLabels[row][col])

    return puzzleImages, puzzleCellLabels

def checkPuzzle(puzzleCellLabels):
    """
    Return true if the labels create a correct puzzle.
    Note that we are checking for duplicates, not deficiencies.
    """

    dimension = len(puzzleCellLabels)

    # {row/col: {value, ...}, ...}
    seenInRow = {}
    seenInCol = {}

    # {blockRowId: {blockColId: {value, ...}, ...}, ...}
    seenInBlock = {}

    size = dimension
    blockSize = int(math.sqrt(dimension))

    # Pre-load the seen data structures.
    for i in range(size):
        seenInRow[i] = set()
        seenInCol[i] = set()

    for blockRowID in range(blockSize):
        seenInBlock[blockRowID] = {}

        for blockColID in range(blockSize):
            seenInBlock[blockRowID][blockColID] = set()

    # Load the seen data structures.
    for row in range(size):
        for col in range(size):
            digit = puzzleCellLabels[row][col]

            seenInRow[row].add(digit)
            seenInCol[col].add(digit)
            seenInBlock[row // blockSize][col // blockSize].add(digit)

    # Check for valid rows/cols.
    for i in range(size):
        if (len(seenInRow[i]) != size):
            return False

        if (len(seenInCol[i]) != size):
            return False

    # Check for valid grids.
    for blockRowID in range(blockSize):
        for blockColID in range(blockSize):
            if (len(seenInBlock[blockRowID][blockColID]) != size):
                return False

    return True
