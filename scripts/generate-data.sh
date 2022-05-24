#!/bin/bash

# Create all the splits.

readonly THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"
readonly SETUP_SCRIPT="${THIS_DIR}/generate-split.py"

readonly NUM_SPLITS='11'

# readonly DIMENSIONS='4 9'
readonly DIMENSIONS='4'
readonly NUM_TRAIN_PUZZLES='001 002 005 010 020 030 040 050 100'
readonly NUM_TEST_VALID_PUZZLE='100'
readonly OVERLAP_PERCENTS='0.00 0.50 1.00 2.00'

readonly STRATEGIES='simple r_split r_puzzle r_cell transfer'

readonly SINGLE_DATASETS='mnist emnist fmnist kmnist'
readonly ALL_DATASETS='mnist emnist fmnist kmnist mnist,emnist mnist,fmnist mnist,kmnist emnist,fmnist emnist,kmnist fmnist,kmnist emnist,fmnist,kmnist mnist,fmnist,kmnist mnist,emnist,fmnist mnist,emnist,fmnist,kmnist'

declare -A ALLOWED_DATASETS
ALLOWED_DATASETS['simple']="${SINGLE_DATASETS}"
ALLOWED_DATASETS['r_split']="${ALL_DATASETS}"
ALLOWED_DATASETS['r_puzzle']="${ALL_DATASETS}"
ALLOWED_DATASETS['r_cell']="${ALL_DATASETS}"
ALLOWED_DATASETS['transfer']="${SINGLE_DATASETS}"

function main() {
	set -e
	trap exit SIGINT

    for split in $(seq -w 01 ${NUM_SPLITS}) ; do
        for dimension in ${DIMENSIONS} ; do
            for numTrainPuzzles in ${NUM_TRAIN_PUZZLES} ; do
                for numTestValidPuzzles in ${NUM_TEST_VALID_PUZZLE} ; do
                    for overlapPercent in ${OVERLAP_PERCENTS} ; do
                        for strategy in ${STRATEGIES} ; do
                            for datasets in ${ALLOWED_DATASETS[${strategy}]} ; do
                                "${SETUP_SCRIPT}" \
                                    --dataset "${datasets}" \
                                    --dimension "${dimension}" \
                                    --num-train "${numTrainPuzzles}" \
                                    --num-test "${numTestValidPuzzles}" \
                                    --num-valid "${numTestValidPuzzles}" \
                                    --overlap-percent "${overlapPercent}" \
                                    --split "${split}" \
                                    --strategy "${strategy}"
                            done
                        done
                    done
                done
            done
        done
    done
}

main "$@"
