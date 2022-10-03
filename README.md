# Visual Sudoku Puzzle Classification

This repository contains the code necessary to create the collective neuro-symbolic benchmark suite described in the paper:
[Visual Sudoku Puzzle Classification: A Suite of Collective Neuro-Symbolic Tasks](https://linqs.org/publications/#id:augustine-nesy22).

## Pre-Generated Data

Pre-generated data is made available with 4x4 and 9x9 puzzles.
11 splits are provided for each configuration.
The first 10 splits (01 - 10) are to be scored, while the final split (11) is free to be used as the experimenter sees fit.
For convenience, the data has been split up by size, task, and datasets.

All the data is available in this directory:
https://linqs-data.soe.ucsc.edu/public/datasets/ViSudo-PC/v01/

Shortcuts to the basic task datasets are provided here:

| Data Source | 4x4 | 9x9 |
|-------------|-----|-----|
| MNIST       | [Basic 4x4 MNIST](https://linqs-data.soe.ucsc.edu/public/datasets/ViSudo-PC/v01/ViSudo-PC_dimension::4_datasets::mnist_strategy::simple.zip) | [Basic 9x9 MNIST](https://linqs-data.soe.ucsc.edu/public/datasets/ViSudo-PC/v01/ViSudo-PC_dimension::9_datasets::mnist_strategy::simple.zip) |
| EMNIST      | [Basic 4x4 EMNIST](https://linqs-data.soe.ucsc.edu/public/datasets/ViSudo-PC/v01/ViSudo-PC_dimension::4_datasets::emnist_strategy::simple.zip) | [Basic 9x9 EMNIST](https://linqs-data.soe.ucsc.edu/public/datasets/ViSudo-PC/v01/ViSudo-PC_dimension::9_datasets::emnist_strategy::simple.zip) |
| FMNIST      | [Basic 4x4 FMNIST](https://linqs-data.soe.ucsc.edu/public/datasets/ViSudo-PC/v01/ViSudo-PC_dimension::4_datasets::fmnist_strategy::simple.zip) | [Basic 9x9 FMNIST](https://linqs-data.soe.ucsc.edu/public/datasets/ViSudo-PC/v01/ViSudo-PC_dimension::9_datasets::fmnist_strategy::simple.zip) |
| KMNIST      | [Basic 4x4 KMNIST](https://linqs-data.soe.ucsc.edu/public/datasets/ViSudo-PC/v01/ViSudo-PC_dimension::4_datasets::kmnist_strategy::simple.zip) | [Basic 9x9 KMNIST](https://linqs-data.soe.ucsc.edu/public/datasets/ViSudo-PC/v01/ViSudo-PC_dimension::9_datasets::kmnist_strategy::simple.zip) |

## Generating Data

The `./scripts/generate-split.py` script can be used to generate a split of puzzles.
All available options can be viewed using `--help`:
```
./scripts/generate-split.py --help
```

## Citations

To reference this work, please cite:
```
@inproceedings{augustine:nesy22,
    title = {Visual Sudoku Puzzle Classification: A Suite of Collective Neuro-Symbolic Tasks},
    author = {Eriq Augustine and Connor Pryor and Charles Dickens and Jay Pujara and William Yang Wang and Lise Getoor},
    booktitle = {International Workshop on Neural-Symbolic Learning and Reasoning (NeSy)},
    year = {2022},
    _publisher = {CEUR},
    address = { Windsor, United Kingdom},
}
```
