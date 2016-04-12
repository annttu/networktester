Network tester
==============

Network quality tester. Tester uses UDP and TCP probes to ping remote server and reports statistics with coordinates to [statscollector](https://github.com/annttu/statscollector/).

Installation
============

Install some required packages

    apt-get install -y python3 python3-pip python3-virtualenv python-virtualenv
    apt-get install -y --no-install-recommends gpsd ntp git ca-certificates

Setup gpsd.

    vi /etc/default/gpsd
    systemctl restart gpsd

Create user and setup environment

    git clone https://github.com/annttu/networktester.git
    virtualenv env --python=python3 --system-site-packages
    . env/bin/activate
    pip install -r networktester/requirements.txt
    git clone https://github.com/tpoche/gps-python3.git env/lib/python3.*/site-packages/gps-python3
    mv env/lib/python3.*/site-packages/gps-python3/gps env/lib/python3.*/site-packages/gps
    # Remove annoying print statement
    sed -i'' -e 's/print("GPS.*//' env/lib/python3.*/site-packages/gps/gps.py
    cp local_config.py.sample local_config.py
    vi local_config.py


Usage
=====

Enable virtualenv and run.

    cd networktester
    . env/bin/activate
    ./tester.sh --server statscollector.example.com -p 25001 -t udp &
    ./tester.sh --server statscollector.example.com -p 25001 -t tcp &
    ./tester.sh --server statscollector.example.com -p 25001 -t statistics &
    wait

License
=======

The MIT License (MIT)
Copyright (c) 2015 Antti Jaakkola

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.