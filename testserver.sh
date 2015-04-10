#!/bin/bash

P="$(cd "$(dirname "$0")"; pwd)/"
cd ${P}/src
export PYTHONPATH=`pwd`

python3 testserver.py $@

