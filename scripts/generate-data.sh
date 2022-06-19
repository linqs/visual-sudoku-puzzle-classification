#!/bin/bash

# Create all the splits.
# Warning: this will create more than a TB of data, it is recommended that you adjust the constants to only generate what you need.

readonly THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"
readonly SETUP_SCRIPT="${THIS_DIR}/generate-split.py"

readonly NUM_SPLITS='11'

readonly DIMENSIONS='4 9'
readonly NUM_TRAIN_PUZZLES='001 002 005 010 020 030 040 050 100'
readonly NUM_TEST_VALID_PUZZLE='100'
readonly OVERLAP_PERCENTS='0.00 0.50 1.00 2.00'

readonly STRATEGIES='simple r_split r_puzzle r_cell transfer'

readonly SINGLE_DATASETS='mnist emnist fmnist kmnist'
readonly LARGE_DATASETS='emnist'
readonly ALL_DATASETS='mnist emnist fmnist kmnist mnist,emnist mnist,fmnist mnist,kmnist emnist,fmnist emnist,kmnist fmnist,kmnist emnist,fmnist,kmnist mnist,fmnist,kmnist mnist,emnist,fmnist mnist,emnist,fmnist,kmnist'

# {"${dim}::${strategy}": datasets, ...}
declare -A ALLOWED_DATASETS

ALLOWED_DATASETS['4::simple']="${SINGLE_DATASETS}"
ALLOWED_DATASETS['4::r_split']="${ALL_DATASETS}"
ALLOWED_DATASETS['4::r_puzzle']="${ALL_DATASETS}"
ALLOWED_DATASETS['4::r_cell']="${ALL_DATASETS}"
ALLOWED_DATASETS['4::transfer']="${SINGLE_DATASETS}"

ALLOWED_DATASETS['9::simple']="${SINGLE_DATASETS}"
ALLOWED_DATASETS['9::r_split']="${ALL_DATASETS}"
ALLOWED_DATASETS['9::r_puzzle']="${ALL_DATASETS}"
ALLOWED_DATASETS['9::r_cell']="${ALL_DATASETS}"
ALLOWED_DATASETS['9::transfer']="${LARGE_DATASETS}"

function main() {
	set -e
	trap exit SIGINT

    for split in $(seq -w 01 ${NUM_SPLITS}) ; do
        for dimension in ${DIMENSIONS} ; do
            for numTrainPuzzles in ${NUM_TRAIN_PUZZLES} ; do
                for numTestValidPuzzles in ${NUM_TEST_VALID_PUZZLE} ; do
                    for overlapPercent in ${OVERLAP_PERCENTS} ; do
                        for strategy in ${STRATEGIES} ; do
                            for datasets in ${ALLOWED_DATASETS["${dimension}::${strategy}"]} ; do
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

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && main "$@"
