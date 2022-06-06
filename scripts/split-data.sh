#!/bin/bash

# Create copies of the data partitioned by dimension, datasets, and strategies.
# This is meant for creating reasonable sized chunks of data for people to work with.

readonly THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"
readonly DATA_DIR="${THIS_DIR}/../data"
readonly BASE_OUT_DIR="/tmp/ViSudo-PC"

function main() {
	set -e
	trap exit SIGINT

    for dimensionDir in "${DATA_DIR}/"* ; do
        local dimension=$(basename "${dimensionDir}")

        for datasetsDir in "${dimensionDir}/"* ; do
            local datasets=$(basename "${datasetsDir}")

            for strategyDir in "${datasetsDir}/"* ; do
                local strategy=$(basename "${strategyDir}")

                local id="ViSudo-PC_${dimension}_${datasets}_${strategy}"
                echo "Setting up ${id}."

                local idDir="${BASE_OUT_DIR}/${id}"
                local outDir="${idDir}/${dimension}/${datasets}/${strategy}"
                mkdir -p "${outDir}"

                cp -r "${strategyDir}" "${outDir}/"

                local zipPath="${idDir}.zip"
                zip -r "${zipPath}" "${idDir}"

                rm -Rf "${idDir}"
            done
        done
    done
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && main "$@"
