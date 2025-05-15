#!/usr/bin/env bash
set -euo pipefail

cd $(dirname $0)

function collect_image_urls() {
    perl -ne 'print $1 if /\]\((https:\/\/raw\.githubusercontent\.com.+)\)$/' "$1"
}

function download_image() {
    curl "$1" --output "images/$2/$(printf "%04d" $3).png"
}

function handle_image() {
    filepath="$1"
    basename="$2"
    image_urls=$(collect_image_urls "$filepath")
    mkdir -p "images/${basename}"
    i=1
    for url in ${image_urls}; do
        download_image "${url}" "${basename}" "$i"
        i=$((i+1))
    done
}

for filepath in "$@"; do
    basename=${filepath##articles/}
    basename=${basename%.md}
    handle_image "${filepath}" "${basename}"
    git add "${filepath}" "images/${basename}"
    git commit -m "[Publish] ${basename}"
done
git push
