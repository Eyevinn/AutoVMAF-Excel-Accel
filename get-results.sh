#!/usr/bin/env bash

HOST="127.0.0.1"
PORT="3000"

processJob () {
    echo "Fetching '${1}' results..."
    curl -s "${HOST}:${PORT}/autoabr/result/${1}/" > "results/${1}.json"
    echo "Fetching '${1}' auto-ladder..."
    curl -s "${HOST}:${PORT}/autovmaf/ladder/${1}/" > "results/${1}_ladder.json"
}

test -d results || mkdir results

if [[ $# -gt 0 ]]; then
    for name in "$@"; do
        processJob "$name"
    done
else
    # loop through lines, add a trailing line break because read otherwise ignores the last line
    (cat "$(dirname "$0")/jobnames.txt"; echo -e) | while IFS= read -r line
    do
        # remove comments and trim leading/trailing whitespaces
        # need to echo and not use quotes, for this to work, so disabled those shellchecks
        # shellcheck disable=SC2116,SC2086
        name=$(echo ${line%%#*})
        
        if [[ -n "$name" ]]; then
            processJob "$name"
        fi
    done
fi