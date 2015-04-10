#!/bin/bash

P="$(cd "$(dirname "$0")"; pwd)/"
export PYTHONPATH="${P}/src"

python3 ${P}/src/tester.py $@

