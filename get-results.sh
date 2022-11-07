#!/usr/bin/env bash

HOST="127.0.0.1"
PORT="3000"

for name in $(cat $(dirname $0)/jobnames.txt); do
    echo Getting ${name} results...
    curl -s "${HOST}:${PORT}/autoabr/result/${name}/" > results/${name}.json
    echo Getting ${name} auto-ladder...
    curl -s "${HOST}:${PORT}/autovmaf/ladder/${name}/" > results/${name}_ladder.json
done