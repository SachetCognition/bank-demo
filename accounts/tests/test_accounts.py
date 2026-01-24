import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from dotmap import DotMap

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['DB_URL'] = 'mongodb://localhost:27017/test_bank'
os.environ['SERVICE_PROTOCOL'] = 'http'


class TestAccountsGeneric:
    
    @pytest.fixture
    def mock_collection(self):
        return MagicMock()
    
    @pytest.fixture
    def accounts_generic(self, mock_collection):
        with patch.dict('sys.modules', {'accounts': MagicMock()}):
            from accounts import AccountsGeneric
            instance = AccountsGeneric()
            return instance

    def test_get_account_details_found(self, mock_collection):
        mock_collection.find_one.return_value = {
            'account_number': 'IBAN1234567890123456',
            'name': 'John Doe',
            'balance': 100,
            'currency': 'USD'
        }
        
        with patch('accounts.collection', mock_collection):
            from accounts import AccountsGeneric
            accounts = AccountsGeneric()
            request = DotMap({'account_number': 'IBAN1234567890123456'})
            result = accounts.getAccountDetails(request)
            
            assert result['account_number'] == 'IBAN1234567890123456'
            assert result['name'] == 'John Doe'
            assert result['balance'] == 100
            assert result['currency'] == 'USD'

    def test_get_account_details_not_found(self, mock_collection):
        mock_collection.find_one.return_value = None
        
        with patch('accounts.collection', mock_collection):
            from accounts import AccountsGeneric
            accounts = AccountsGeneric()
            request = DotMap({'account_number': 'NONEXISTENT'})
            result = accounts.getAccountDetails(request)
            
            assert result == {}

    def test_create_account_success(self, mock_collection):
        mock_collection.count_documents.return_value = 0
        mock_collection.insert_one.return_value = MagicMock()
        
        with patch('accounts.collection', mock_collection):
            from accounts import AccountsGeneric
            accounts = AccountsGeneric()
            request = DotMap({
                'email_id': 'test@example.com',
                'account_type': 'Checking',
                'address': '123 Test Street',
                'govt_id_number': '123-45-6789',
                'government_id_type': 'SSN',
                'name': 'John Doe'
            })
            result = accounts.createAccount(request)
            
            assert result is True
            mock_collection.insert_one.assert_called_once()

    def test_create_account_duplicate(self, mock_collection):
        mock_collection.count_documents.return_value = 1
        
        with patch('accounts.collection', mock_collection):
            from accounts import AccountsGeneric
            accounts = AccountsGeneric()
            request = DotMap({
                'email_id': 'test@example.com',
                'account_type': 'Checking',
                'address': '123 Test Street',
                'govt_id_number': '123-45-6789',
                'government_id_type': 'SSN',
                'name': 'John Doe'
            })
            result = accounts.createAccount(request)
            
            assert result is False
            mock_collection.insert_one.assert_not_called()

    def test_create_account_different_type_same_email(self, mock_collection):
        mock_collection.count_documents.return_value = 0
        mock_collection.insert_one.return_value = MagicMock()
        
        with patch('accounts.collection', mock_collection):
            from accounts import AccountsGeneric
            accounts = AccountsGeneric()
            request = DotMap({
                'email_id': 'test@example.com',
                'account_type': 'Savings',
                'address': '123 Test Street',
                'govt_id_number': '123-45-6789',
                'government_id_type': 'SSN',
                'name': 'John Doe'
            })
            result = accounts.createAccount(request)
            
            assert result is True

    def test_get_accounts_success(self, mock_collection):
        mock_accounts = [
            {
                'account_number': 'IBAN1234567890123456',
                'email_id': 'test@example.com',
                'account_type': 'Checking',
                'address': '123 Test Street',
                'govt_id_number': '123-45-6789',
                'government_id_type': 'SSN',
                'name': 'John Doe',
                'balance': 100,
                'currency': 'USD'
            },
            {
                'account_number': 'IBAN6543210987654321',
                'email_id': 'test@example.com',
                'account_type': 'Savings',
                'address': '123 Test Street',
                'govt_id_number': '123-45-6789',
                'government_id_type': 'SSN',
                'name': 'John Doe',
                'balance': 500,
                'currency': 'USD'
            }
        ]
        mock_collection.find.return_value = mock_accounts
        
        with patch('accounts.collection', mock_collection):
            from accounts import AccountsGeneric
            accounts = AccountsGeneric()
            request = DotMap({'email_id': 'test@example.com'})
            result = accounts.getAccounts(request)
            
            assert len(result) == 2
            assert result[0]['account_number'] == 'IBAN1234567890123456'
            assert result[1]['account_number'] == 'IBAN6543210987654321'

    def test_get_accounts_empty(self, mock_collection):
        mock_collection.find.return_value = []
        
        with patch('accounts.collection', mock_collection):
            from accounts import AccountsGeneric
            accounts = AccountsGeneric()
            request = DotMap({'email_id': 'nonexistent@example.com'})
            result = accounts.getAccounts(request)
            
            assert result == []

    def test_create_account_generates_iban(self, mock_collection):
        mock_collection.count_documents.return_value = 0
        inserted_account = None
        
        def capture_insert(account):
            nonlocal inserted_account
            inserted_account = account
            return MagicMock()
        
        mock_collection.insert_one.side_effect = capture_insert
        
        with patch('accounts.collection', mock_collection):
            from accounts import AccountsGeneric
            accounts = AccountsGeneric()
            request = DotMap({
                'email_id': 'test@example.com',
                'account_type': 'Checking',
                'address': '123 Test Street',
                'govt_id_number': '123-45-6789',
                'government_id_type': 'SSN',
                'name': 'John Doe'
            })
            accounts.createAccount(request)
            
            assert inserted_account is not None
            assert inserted_account['account_number'].startswith('IBAN')
            assert len(inserted_account['account_number']) == 20

    def test_create_account_initial_balance(self, mock_collection):
        mock_collection.count_documents.return_value = 0
        inserted_account = None
        
        def capture_insert(account):
            nonlocal inserted_account
            inserted_account = account
            return MagicMock()
        
        mock_collection.insert_one.side_effect = capture_insert
        
        with patch('accounts.collection', mock_collection):
            from accounts import AccountsGeneric
            accounts = AccountsGeneric()
            request = DotMap({
                'email_id': 'test@example.com',
                'account_type': 'Checking',
                'address': '123 Test Street',
                'govt_id_number': '123-45-6789',
                'government_id_type': 'SSN',
                'name': 'John Doe'
            })
            accounts.createAccount(request)
            
            assert inserted_account['balance'] == 100
            assert inserted_account['currency'] == 'USD'


class TestAccountsFlaskEndpoints:
    
    @pytest.fixture
    def client(self):
        with patch('accounts.collection', MagicMock()):
            from accounts import app
            app.config['TESTING'] = True
            with app.test_client() as client:
                yield client

    def test_get_account_details_endpoint(self, client):
        with patch('accounts.accounts_generic') as mock_generic:
            mock_generic.getAccountDetails.return_value = {
                'account_number': 'IBAN1234567890123456',
                'name': 'John Doe',
                'balance': 100,
                'currency': 'USD'
            }
            
            response = client.post('/account-detail', 
                                   json={'account_number': 'IBAN1234567890123456'},
                                   content_type='application/json')
            
            assert response.status_code == 200

    def test_create_account_endpoint(self, client):
        with patch('accounts.accounts_generic') as mock_generic:
            mock_generic.createAccount.return_value = True
            
            response = client.post('/create-account',
                                   json={
                                       'email_id': 'test@example.com',
                                       'account_type': 'Checking',
                                       'address': '123 Test Street',
                                       'govt_id_number': '123-45-6789',
                                       'government_id_type': 'SSN',
                                       'name': 'John Doe'
                                   },
                                   content_type='application/json')
            
            assert response.status_code == 200

    def test_get_all_accounts_endpoint(self, client):
        with patch('accounts.accounts_generic') as mock_generic:
            mock_generic.getAccounts.return_value = [
                {
                    'account_number': 'IBAN1234567890123456',
                    'email_id': 'test@example.com',
                    'account_type': 'Checking',
                    'name': 'John Doe',
                    'balance': 100,
                    'currency': 'USD'
                }
            ]
            
            response = client.post('/get-all-accounts',
                                   json={'email_id': 'test@example.com'},
                                   content_type='application/json')
            
            assert response.status_code == 200
