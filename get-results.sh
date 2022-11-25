#!/usr/bin/env bash

HOST="127.0.0.1"
PORT="3000"

test -d results || mkdir results

if [[ $# -gt 0 ]]
then
    for name in "$@"
    do
        echo Getting ${name} results...
        curl -s "${HOST}:${PORT}/autoabr/result/${name}/" > results/${name}.json
        echo Getting ${name} auto-ladder...
        curl -s "${HOST}:${PORT}/autovmaf/ladder/${name}/" > results/${name}_ladder.json
    done
else 
    for name in $(cat $(dirname $0)/jobnames.txt); do
        echo Getting ${name} results...
        curl -s "${HOST}:${PORT}/autoabr/result/${name}/" > results/${name}.json
        echo Getting ${name} auto-ladder...
        curl -s "${HOST}:${PORT}/autovmaf/ladder/${name}/" > results/${name}_ladder.json
    done
fi