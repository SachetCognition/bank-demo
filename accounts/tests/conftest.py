import pytest
import mongomock
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['DB_URL'] = 'mongodb://localhost:27017/test_bank'
os.environ['SERVICE_PROTOCOL'] = 'http'


@pytest.fixture
def mock_mongo_client(monkeypatch):
    client = mongomock.MongoClient()
    db = client['bank']
    
    monkeypatch.setattr('accounts.client', client)
    monkeypatch.setattr('accounts.db', db)
    monkeypatch.setattr('accounts.collection', db['accounts'])
    
    yield db
    
    client.close()


@pytest.fixture
def sample_account_data():
    return {
        'email_id': 'test@example.com',
        'account_type': 'Checking',
        'address': '123 Test Street',
        'govt_id_number': '123-45-6789',
        'government_id_type': 'SSN',
        'name': 'John Doe'
    }


@pytest.fixture
def sample_account_in_db(mock_mongo_client, sample_account_data):
    account = {
        **sample_account_data,
        'account_number': 'IBAN1234567890123456',
        'balance': 100,
        'currency': 'USD'
    }
    mock_mongo_client['accounts'].insert_one(account)
    return account
