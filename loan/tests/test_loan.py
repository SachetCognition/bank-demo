import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['DB_URL'] = 'mongodb://localhost:27017/test_bank'
os.environ['SERVICE_PROTOCOL'] = 'http'


class TestLoanGeneric:
    
    @pytest.fixture
    def mock_collections(self):
        mock_accounts = MagicMock()
        mock_loans = MagicMock()
        return mock_accounts, mock_loans

    def test_process_loan_request_success(self, mock_collections):
        mock_accounts, mock_loans = mock_collections
        
        account = {
            'account_number': 'IBAN1234567890123456',
            'email_id': 'test@example.com',
            'balance': 100
        }
        
        mock_accounts.find.return_value = [account]
        mock_accounts.count_documents.return_value = 1
        mock_accounts.update_one.return_value = MagicMock()
        mock_loans.insert_one.return_value = MagicMock()
        
        with patch('loan.collection_accounts', mock_accounts), \
             patch('loan.collection_loans', mock_loans):
            from loan import LoanGeneric
            loan = LoanGeneric()
            request_data = {
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
            }
            result = loan.ProcessLoanRequest(request_data)
            
            assert result['approved'] is True
            assert result['message'] == 'Loan Approved'

    def test_process_loan_request_account_not_found(self, mock_collections):
        mock_accounts, mock_loans = mock_collections
        
        mock_accounts.find.return_value = []
        mock_accounts.count_documents.return_value = 0
        
        with patch('loan.collection_accounts', mock_accounts), \
             patch('loan.collection_loans', mock_loans):
            from loan import LoanGeneric
            loan = LoanGeneric()
            request_data = {
                'name': 'John Doe',
                'email': 'test@example.com',
                'account_type': 'Checking',
                'account_number': 'NONEXISTENT',
                'govt_id_type': 'SSN',
                'govt_id_number': '123-45-6789',
                'loan_type': 'Base Camp',
                'loan_amount': '5000',
                'interest_rate': '5.5',
                'time_period': '12 months'
            }
            result = loan.ProcessLoanRequest(request_data)
            
            assert result['approved'] is False
            assert 'Email or Account number not found' in result['message']

    def test_process_loan_request_email_mismatch(self, mock_collections):
        mock_accounts, mock_loans = mock_collections
        
        account = {
            'account_number': 'IBAN1234567890123456',
            'email_id': 'different@example.com',
            'balance': 100
        }
        
        mock_accounts.find.return_value = [account]
        mock_accounts.count_documents.return_value = 0
        
        with patch('loan.collection_accounts', mock_accounts), \
             patch('loan.collection_loans', mock_loans):
            from loan import LoanGeneric
            loan = LoanGeneric()
            request_data = {
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
            }
            result = loan.ProcessLoanRequest(request_data)
            
            assert result['approved'] is False

    def test_process_loan_request_zero_amount(self, mock_collections):
        mock_accounts, mock_loans = mock_collections
        
        account = {
            'account_number': 'IBAN1234567890123456',
            'email_id': 'test@example.com',
            'balance': 100
        }
        
        mock_accounts.find.return_value = [account]
        mock_accounts.count_documents.return_value = 1
        mock_loans.insert_one.return_value = MagicMock()
        
        with patch('loan.collection_accounts', mock_accounts), \
             patch('loan.collection_loans', mock_loans):
            from loan import LoanGeneric
            loan = LoanGeneric()
            request_data = {
                'name': 'John Doe',
                'email': 'test@example.com',
                'account_type': 'Checking',
                'account_number': 'IBAN1234567890123456',
                'govt_id_type': 'SSN',
                'govt_id_number': '123-45-6789',
                'loan_type': 'Base Camp',
                'loan_amount': '0',
                'interest_rate': '5.5',
                'time_period': '12 months'
            }
            result = loan.ProcessLoanRequest(request_data)
            
            assert result['approved'] is False
            assert result['message'] == 'Loan Rejected'

    def test_process_loan_request_negative_amount(self, mock_collections):
        mock_accounts, mock_loans = mock_collections
        
        account = {
            'account_number': 'IBAN1234567890123456',
            'email_id': 'test@example.com',
            'balance': 100
        }
        
        mock_accounts.find.return_value = [account]
        mock_accounts.count_documents.return_value = 1
        mock_loans.insert_one.return_value = MagicMock()
        
        with patch('loan.collection_accounts', mock_accounts), \
             patch('loan.collection_loans', mock_loans):
            from loan import LoanGeneric
            loan = LoanGeneric()
            request_data = {
                'name': 'John Doe',
                'email': 'test@example.com',
                'account_type': 'Checking',
                'account_number': 'IBAN1234567890123456',
                'govt_id_type': 'SSN',
                'govt_id_number': '123-45-6789',
                'loan_type': 'Base Camp',
                'loan_amount': '-100',
                'interest_rate': '5.5',
                'time_period': '12 months'
            }
            result = loan.ProcessLoanRequest(request_data)
            
            assert result['approved'] is False

    def test_get_loan_history_success(self, mock_collections):
        mock_accounts, mock_loans = mock_collections
        
        loans = [
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
                'timestamp': datetime.now()
            },
            {
                'name': 'John Doe',
                'email': 'test@example.com',
                'account_type': 'Checking',
                'account_number': 'IBAN1234567890123456',
                'govt_id_type': 'SSN',
                'govt_id_number': '123-45-6789',
                'loan_type': 'Rover',
                'loan_amount': 10000,
                'interest_rate': 6.0,
                'time_period': '24 months',
                'status': 'Approved',
                'timestamp': datetime.now()
            }
        ]
        
        mock_loans.find.return_value = loans
        
        with patch('loan.collection_accounts', mock_accounts), \
             patch('loan.collection_loans', mock_loans):
            from loan import LoanGeneric
            loan = LoanGeneric()
            request_data = {'email': 'test@example.com'}
            result = loan.getLoanHistory(request_data)
            
            assert len(result) == 2
            assert result[0]['loan_type'] == 'Base Camp'
            assert result[1]['loan_type'] == 'Rover'

    def test_get_loan_history_empty(self, mock_collections):
        mock_accounts, mock_loans = mock_collections
        
        mock_loans.find.return_value = []
        
        with patch('loan.collection_accounts', mock_accounts), \
             patch('loan.collection_loans', mock_loans):
            from loan import LoanGeneric
            loan = LoanGeneric()
            request_data = {'email': 'nonexistent@example.com'}
            result = loan.getLoanHistory(request_data)
            
            assert result == []

    def test_approve_loan_updates_balance(self, mock_collections):
        mock_accounts, mock_loans = mock_collections
        
        account = {
            'account_number': 'IBAN1234567890123456',
            'email_id': 'test@example.com',
            'balance': 100
        }
        
        updated_balance = None
        
        def capture_update(query, update):
            nonlocal updated_balance
            updated_balance = update['$set']['balance']
            return MagicMock()
        
        mock_accounts.find.return_value = [account]
        mock_accounts.count_documents.return_value = 1
        mock_accounts.update_one.side_effect = capture_update
        mock_loans.insert_one.return_value = MagicMock()
        
        with patch('loan.collection_accounts', mock_accounts), \
             patch('loan.collection_loans', mock_loans):
            from loan import LoanGeneric
            loan = LoanGeneric()
            request_data = {
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
            }
            loan.ProcessLoanRequest(request_data)
            
            assert updated_balance == 5100

    def test_loan_types(self, mock_collections):
        mock_accounts, mock_loans = mock_collections
        
        account = {
            'account_number': 'IBAN1234567890123456',
            'email_id': 'test@example.com',
            'balance': 100
        }
        
        mock_accounts.find.return_value = [account]
        mock_accounts.count_documents.return_value = 1
        mock_accounts.update_one.return_value = MagicMock()
        mock_loans.insert_one.return_value = MagicMock()
        
        loan_types = ['Base Camp', 'Rover', 'Potato Farming', 'Ice Home', 'Rocker']
        
        with patch('loan.collection_accounts', mock_accounts), \
             patch('loan.collection_loans', mock_loans):
            from loan import LoanGeneric
            loan = LoanGeneric()
            
            for loan_type in loan_types:
                request_data = {
                    'name': 'John Doe',
                    'email': 'test@example.com',
                    'account_type': 'Checking',
                    'account_number': 'IBAN1234567890123456',
                    'govt_id_type': 'SSN',
                    'govt_id_number': '123-45-6789',
                    'loan_type': loan_type,
                    'loan_amount': '1000',
                    'interest_rate': '5.0',
                    'time_period': '12 months'
                }
                result = loan.ProcessLoanRequest(request_data)
                assert result['approved'] is True


class TestLoanFlaskEndpoints:
    
    @pytest.fixture
    def client(self):
        with patch('loan.collection_accounts', MagicMock()), \
             patch('loan.collection_loans', MagicMock()):
            from loan import app
            app.config['TESTING'] = True
            with app.test_client() as client:
                yield client

    def test_loan_request_endpoint(self, client):
        with patch('loan.loan_generic') as mock_generic:
            mock_generic.ProcessLoanRequest.return_value = {
                'approved': True,
                'message': 'Loan Approved'
            }
            
            response = client.post('/loan/request',
                                   json={
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
                                   },
                                   content_type='application/json')
            
            assert response.status_code == 200

    def test_loan_history_endpoint(self, client):
        with patch('loan.loan_generic') as mock_generic:
            mock_generic.getLoanHistory.return_value = [
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
                                   json={'email': 'test@example.com'},
                                   content_type='application/json')
            
            assert response.status_code == 200
