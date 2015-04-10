#!/bin/bash

P="$(cd "$(dirname "$1")"; pwd)/$(basename "$1")"
cd ${P}/src
export PYTHONPATH=`pwd`

python tester.py

