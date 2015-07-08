# Configuration

table_prefix = ''
table_suffix = 'coords'

database_username = 'networktester'
database_password = 'networktestser'
database_hostname = 'localhost'
database_database = 'networktester'

submit_url = "http://localhost:8080/"
submit_key = "foobarasdf"

version = 0.1

try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
    from local_config import *
except ImportError:
    print("Cannot import local settings")