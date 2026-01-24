import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['DB_URL'] = 'mongodb://localhost:27017/test_bank'
os.environ['SERVICE_PROTOCOL'] = 'http'
