#!/usr/bin/env bash
set -euo pipefail

echo "Copy from $SOURCE_DIR"

BASE_DIR="$(dirname $(dirname $0))"

function copy() {
    while true; do
        for path in "$SOURCE_DIR"/*; do
            basename=$(basename "$path")
            sync="${BASE_DIR}/sync/${basename}"
            if ! cmp -s ${path} ${sync}; then
                dest="${BASE_DIR}/articles/${basename#*-}"
                echo sync ${path} to ${dest}
                cp ${path} ${sync}
                cat ${sync} | python ${BASE_DIR}/tools/transform_md.py > ${dest}
            fi
        done
        sleep 1
        echo -n '.'
    done
}

npx zenn preview --open &

copy &

cat
