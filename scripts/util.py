import random

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
