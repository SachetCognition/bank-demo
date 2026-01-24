import pytest
import sys
import os
from unittest.mock import MagicMock, patch
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['DB_URL'] = 'mongodb://localhost:27017/test_bank'
os.environ['SERVICE_PROTOCOL'] = 'http'
os.environ['ACCOUNT_HOST'] = 'localhost'
os.environ['TRANSACTION_HOST'] = 'localhost'
os.environ['LOAN_HOST'] = 'localhost'


class TestDashboardRoutes:
    
    @pytest.fixture
    def client(self):
        with patch('dashboard.MongoClient') as mock_mongo:
            mock_mongo.return_value = MagicMock()
            from dashboard import app
            app.config['TESTING'] = True
            with app.test_client() as client:
                yield client

    def test_homepage(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert b'Dashboard is running' in response.data


class TestAccountEndpoints:
    
    @pytest.fixture
    def client(self):
        with patch('dashboard.MongoClient') as mock_mongo:
            mock_mongo.return_value = MagicMock()
            from dashboard import app
            app.config['TESTING'] = True
            with app.test_client() as client:
                yield client

    def test_create_account_http_protocol(self, client):
        with patch('dashboard.flask_client_requests.post') as mock_post:
            mock_post.return_value.json.return_value = True
            
            response = client.post('/account/create',
                                   data={
                                       'email_id': 'test@example.com',
                                       'account_type': 'Checking',
                                       'address': '123 Test Street',
                                       'govt_id_number': '123-45-6789',
                                       'government_id_type': 'SSN',
                                       'name': 'John Doe'
                                   })
            
            assert response.status_code == 200

    def test_get_all_accounts_http_protocol(self, client):
        with patch('dashboard.flask_client_requests.post') as mock_post:
            mock_post.return_value.json.return_value = [
                {
                    'account_number': 'IBAN1234567890123456',
                    'email_id': 'test@example.com',
                    'account_type': 'Checking',
                    'name': 'John Doe',
                    'balance': 100,
                    'currency': 'USD'
                }
            ]
            
            response = client.post('/account/allaccounts',
                                   data={'email_id': 'test@example.com'})
            
            assert response.status_code == 200

    def test_get_account_details_http_protocol(self, client):
        with patch('dashboard.flask_client_requests.post') as mock_post:
            mock_post.return_value.json.return_value = {
                'account_number': 'IBAN1234567890123456',
                'name': 'John Doe',
                'balance': 100,
                'currency': 'USD'
            }
            
            response = client.post('/account/detail',
                                   data={'account_number': 'IBAN1234567890123456'})
            
            assert response.status_code == 200

    def test_create_account_get_returns_template(self, client):
        response = client.get('/account/create')
        assert response.status_code == 200


class TestTransactionEndpoints:
    
    @pytest.fixture
    def client(self):
        with patch('dashboard.MongoClient') as mock_mongo:
            mock_mongo.return_value = MagicMock()
            from dashboard import app
            app.config['TESTING'] = True
            with app.test_client() as client:
                yield client

    def test_transaction_http_protocol(self, client):
        with patch('dashboard.flask_client_requests.post') as mock_post:
            mock_post.return_value.json.return_value = {
                'approved': True,
                'message': 'Transaction is Successful.'
            }
            
            response = client.post('/transaction/',
                                   data={
                                       'sender_account_number': 'IBAN1111111111111111',
                                       'receiver_account_number': 'IBAN2222222222222222',
                                       'amount': '100',
                                       'sender_account_type': 'Checking',
                                       'receiver_account_type': 'Checking',
                                       'reason': 'Test transfer'
                                   })
            
            assert response.status_code == 200

    def test_zelle_transaction_http_protocol(self, client):
        with patch('dashboard.flask_client_requests.post') as mock_post:
            mock_post.return_value.json.return_value = {
                'approved': True,
                'message': 'Transaction is Successful.'
            }
            
            response = client.post('/transaction/zelle/',
                                   data={
                                       'sender_email': 'sender@example.com',
                                       'receiver_email': 'receiver@example.com',
                                       'amount': '50',
                                       'reason': 'Zelle test'
                                   })
            
            assert response.status_code == 200

    def test_transaction_history_http_protocol(self, client):
        with patch('dashboard.flask_client_requests.post') as mock_post:
            mock_post.return_value.json.return_value = [
                {
                    'account_number': 'IBAN2222222222222222',
                    'amount': 100,
                    'reason': 'Test',
                    'time_stamp': '2024-01-01',
                    'type': 'credit',
                    'transaction_id': 'abc123'
                }
            ]
            
            response = client.post('/transaction/history',
                                   data={'account_number': 'IBAN1111111111111111'})
            
            assert response.status_code == 200

    def test_transaction_by_id_http_protocol(self, client):
        with patch('dashboard.flask_client_requests.post') as mock_post:
            mock_post.return_value.json.return_value = {
                'account_number': 'IBAN2222222222222222',
                'amount': 100,
                'reason': 'Test',
                'time_stamp': '2024-01-01',
                'type': 'credit',
                'transaction_id': 'abc123'
            }
            
            response = client.post('/transaction/transaction-with-id',
                                   data={'transaction_id': 'abc123'})
            
            assert response.status_code == 200


class TestLoanEndpoints:
    
    @pytest.fixture
    def client(self):
        with patch('dashboard.MongoClient') as mock_mongo:
            mock_mongo.return_value = MagicMock()
            from dashboard import app
            app.config['TESTING'] = True
            with app.test_client() as client:
                yield client

    def test_loan_request_http_protocol(self, client):
        with patch('dashboard.flask_client_requests.post') as mock_post:
            mock_post.return_value.json.return_value = {
                'approved': True,
                'message': 'Loan Approved'
            }
            
            response = client.post('/loan/',
                                   data={
                                       'name': 'John Doe',
                                       'email': 'test@example.com',
                                       'account_type': 'Checking',
                                       'account_number': 'IBAN1234567890123456',
                                       'govt_id_type': 'SSN',
                                       'govt_id_number': '123-45-6789',
                                       'loan_type': 'Base Camp',
                                       'loan_amount': '5000',
                                       'interest_rate': '5.5',
                                       'time_period': '12 months'
                                   })
            
            assert response.status_code == 200

    def test_loan_history_http_protocol(self, client):
        with patch('dashboard.flask_client_requests.post') as mock_post:
            mock_post.return_value.json.return_value = [
                {
                    'name': 'John Doe',
                    'email': 'test@example.com',
                    'account_type': 'Checking',
                    'account_number': 'IBAN1234567890123456',
                    'govt_id_type': 'SSN',
                    'govt_id_number': '123-45-6789',
                    'loan_type': 'Base Camp',
                    'loan_amount': 5000,
                    'interest_rate': 5.5,
                    'time_period': '12 months',
                    'status': 'Approved',
                    'timestamp': '2024-01-01 12:00:00'
                }
            ]
            
            response = client.post('/loan/history',
                                   data={'email': 'test@example.com'})
            
            assert response.status_code == 200


class TestProtocolSwitching:
    
    def test_http_protocol_is_default(self):
        os.environ['SERVICE_PROTOCOL'] = 'http'
        
        import importlib
        import dashboard
        importlib.reload(dashboard)
        
        assert dashboard.protocol == 'http'

    def test_grpc_protocol_can_be_set(self):
        original_protocol = os.environ.get('SERVICE_PROTOCOL')
        os.environ['SERVICE_PROTOCOL'] = 'grpc'
        
        import importlib
        import dashboard
        importlib.reload(dashboard)
        
        assert dashboard.protocol == 'grpc'
        
        if original_protocol:
            os.environ['SERVICE_PROTOCOL'] = original_protocol
        else:
            os.environ['SERVICE_PROTOCOL'] = 'http'


class TestServiceHostConfiguration:
    
    def test_account_host_configuration(self):
        os.environ['ACCOUNT_HOST'] = 'accounts-service'
        
        import importlib
        import dashboard
        importlib.reload(dashboard)
        
        os.environ['ACCOUNT_HOST'] = 'localhost'

    def test_transaction_host_configuration(self):
        os.environ['TRANSACTION_HOST'] = 'transactions-service'
        
        import importlib
        import dashboard
        importlib.reload(dashboard)
        
        os.environ['TRANSACTION_HOST'] = 'localhost'

    def test_loan_host_configuration(self):
        os.environ['LOAN_HOST'] = 'loan-service'
        
        import importlib
        import dashboard
        importlib.reload(dashboard)
        
        os.environ['LOAN_HOST'] = 'localhost'


class TestErrorHandling:
    
    @pytest.fixture
    def client(self):
        with patch('dashboard.MongoClient') as mock_mongo:
            mock_mongo.return_value = MagicMock()
            from dashboard import app
            app.config['TESTING'] = True
            with app.test_client() as client:
                yield client

    def test_get_all_accounts_returns_none_on_get(self, client):
        response = client.get('/account/allaccounts')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['response'] is None

    def test_get_account_details_returns_none_on_get(self, client):
        response = client.get('/account/detail')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['response'] is None

    def test_transaction_history_returns_none_on_get(self, client):
        response = client.get('/transaction/history')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['response'] is None

    def test_transaction_by_id_returns_none_on_get(self, client):
        response = client.get('/transaction/transaction-with-id')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['response'] is None
