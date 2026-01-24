import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from dotmap import DotMap
from bson.objectid import ObjectId

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['DB_URL'] = 'mongodb://localhost:27017/test_bank'
os.environ['SERVICE_PROTOCOL'] = 'http'


class TestTransactionGeneric:
    
    @pytest.fixture
    def mock_collections(self):
        mock_accounts = MagicMock()
        mock_transactions = MagicMock()
        return mock_accounts, mock_transactions

    def test_send_money_success(self, mock_collections):
        mock_accounts, mock_transactions = mock_collections
        
        sender = {
            'account_number': 'IBAN1111111111111111',
            'balance': 500,
            'email_id': 'sender@example.com'
        }
        receiver = {
            'account_number': 'IBAN2222222222222222',
            'balance': 100,
            'email_id': 'receiver@example.com'
        }
        
        mock_accounts.find.return_value = [sender, receiver]
        mock_accounts.update_one.return_value = MagicMock()
        mock_transactions.insert_one.return_value = MagicMock()
        
        with patch('transaction.collection_accounts', mock_accounts), \
             patch('transaction.collection_transactions', mock_transactions):
            from transaction import TransactionGeneric
            trans = TransactionGeneric()
            request = DotMap({
                'sender_account_number': 'IBAN1111111111111111',
                'receiver_account_number': 'IBAN2222222222222222',
                'amount': '100',
                'reason': 'Test transfer'
            })
            result = trans.SendMoney(request)
            
            assert result['approved'] is True
            assert result['message'] == 'Transaction is Successful.'

    def test_send_money_insufficient_balance(self, mock_collections):
        mock_accounts, mock_transactions = mock_collections
        
        sender = {
            'account_number': 'IBAN1111111111111111',
            'balance': 50,
            'email_id': 'sender@example.com'
        }
        receiver = {
            'account_number': 'IBAN2222222222222222',
            'balance': 100,
            'email_id': 'receiver@example.com'
        }
        
        mock_accounts.find.return_value = [sender, receiver]
        
        with patch('transaction.collection_accounts', mock_accounts), \
             patch('transaction.collection_transactions', mock_transactions):
            from transaction import TransactionGeneric
            trans = TransactionGeneric()
            request = DotMap({
                'sender_account_number': 'IBAN1111111111111111',
                'receiver_account_number': 'IBAN2222222222222222',
                'amount': '100',
                'reason': 'Test transfer'
            })
            result = trans.SendMoney(request)
            
            assert result['approved'] is False
            assert result['message'] == 'Insufficient Balance'

    def test_send_money_sender_not_found(self, mock_collections):
        mock_accounts, mock_transactions = mock_collections
        
        receiver = {
            'account_number': 'IBAN2222222222222222',
            'balance': 100,
            'email_id': 'receiver@example.com'
        }
        
        mock_accounts.find.return_value = [receiver]
        
        with patch('transaction.collection_accounts', mock_accounts), \
             patch('transaction.collection_transactions', mock_transactions):
            from transaction import TransactionGeneric
            trans = TransactionGeneric()
            request = DotMap({
                'sender_account_number': 'NONEXISTENT',
                'receiver_account_number': 'IBAN2222222222222222',
                'amount': '100',
                'reason': 'Test transfer'
            })
            result = trans.SendMoney(request)
            
            assert result['approved'] is False
            assert 'Sender Account Not Found' in result['message']

    def test_send_money_receiver_not_found(self, mock_collections):
        mock_accounts, mock_transactions = mock_collections
        
        sender = {
            'account_number': 'IBAN1111111111111111',
            'balance': 500,
            'email_id': 'sender@example.com'
        }
        
        mock_accounts.find.return_value = [sender]
        
        with patch('transaction.collection_accounts', mock_accounts), \
             patch('transaction.collection_transactions', mock_transactions):
            from transaction import TransactionGeneric
            trans = TransactionGeneric()
            request = DotMap({
                'sender_account_number': 'IBAN1111111111111111',
                'receiver_account_number': 'NONEXISTENT',
                'amount': '100',
                'reason': 'Test transfer'
            })
            result = trans.SendMoney(request)
            
            assert result['approved'] is False
            assert 'Receiver Account Not Found' in result['message']

    def test_zelle_transfer_success(self, mock_collections):
        mock_accounts, mock_transactions = mock_collections
        
        sender = {
            'account_number': 'IBAN1111111111111111',
            'balance': 500,
            'email_id': 'sender@example.com',
            'account_type': 'Checking'
        }
        receiver = {
            'account_number': 'IBAN2222222222222222',
            'balance': 100,
            'email_id': 'receiver@example.com',
            'account_type': 'Checking'
        }
        
        mock_accounts.count_documents.return_value = 1
        mock_accounts.find.side_effect = [[sender], [receiver]]
        mock_accounts.update_one.return_value = MagicMock()
        mock_transactions.insert_one.return_value = MagicMock()
        
        with patch('transaction.collection_accounts', mock_accounts), \
             patch('transaction.collection_transactions', mock_transactions):
            from transaction import TransactionGeneric
            trans = TransactionGeneric()
            request = DotMap({
                'sender_email': 'sender@example.com',
                'receiver_email': 'receiver@example.com',
                'amount': '50',
                'reason': 'Zelle transfer'
            })
            result = trans.Zelle(request)
            
            assert result['approved'] is True
            assert result['message'] == 'Transaction is Successful.'

    def test_zelle_transfer_prioritizes_checking(self, mock_collections):
        mock_accounts, mock_transactions = mock_collections
        
        checking_account = {
            'account_number': 'IBAN1111111111111111',
            'balance': 500,
            'email_id': 'sender@example.com',
            'account_type': 'Checking'
        }
        
        def count_docs_side_effect(query):
            if query.get('account_type') == 'Checking':
                return 1
            return 0
        
        mock_accounts.count_documents.side_effect = count_docs_side_effect
        mock_accounts.find.return_value = [checking_account]
        
        with patch('transaction.collection_accounts', mock_accounts), \
             patch('transaction.collection_transactions', mock_transactions):
            from transaction import TransactionGeneric
            trans = TransactionGeneric()
            account = trans._TransactionGeneric__getAccountwithEmail('sender@example.com')
            
            assert account is not None
            assert account['account_type'] == 'Checking'

    def test_get_transaction_by_id_found(self, mock_collections):
        mock_accounts, mock_transactions = mock_collections
        
        transaction_id = ObjectId()
        mock_transactions.count_documents.return_value = 1
        mock_transactions.find_one.return_value = {
            '_id': transaction_id,
            'sender': 'IBAN1111111111111111',
            'receiver': 'IBAN2222222222222222',
            'amount': 100,
            'reason': 'Test',
            'time_stamp': '2024-01-01 12:00:00'
        }
        
        with patch('transaction.collection_accounts', mock_accounts), \
             patch('transaction.collection_transactions', mock_transactions):
            from transaction import TransactionGeneric
            trans = TransactionGeneric()
            request = DotMap({'transaction_id': str(transaction_id)})
            result = trans.GetTransactionByID(request)
            
            assert result['account_number'] == 'IBAN2222222222222222'
            assert result['amount'] == 100
            assert result['type'] == 'credit'

    def test_get_transaction_by_id_not_found(self, mock_collections):
        mock_accounts, mock_transactions = mock_collections
        
        mock_transactions.count_documents.return_value = 0
        
        with patch('transaction.collection_accounts', mock_accounts), \
             patch('transaction.collection_transactions', mock_transactions):
            from transaction import TransactionGeneric
            trans = TransactionGeneric()
            request = DotMap({'transaction_id': str(ObjectId())})
            result = trans.GetTransactionByID(request)
            
            assert result == {}

    def test_get_transactions_history(self, mock_collections):
        mock_accounts, mock_transactions = mock_collections
        
        credit_transactions = [
            {
                '_id': ObjectId(),
                'sender': 'IBAN1111111111111111',
                'receiver': 'IBAN2222222222222222',
                'amount': 100,
                'reason': 'Payment 1',
                'time_stamp': '2024-01-01 12:00:00'
            }
        ]
        debit_transactions = [
            {
                '_id': ObjectId(),
                'sender': 'IBAN3333333333333333',
                'receiver': 'IBAN1111111111111111',
                'amount': 50,
                'reason': 'Payment 2',
                'time_stamp': '2024-01-02 12:00:00'
            }
        ]
        
        mock_transactions.find.side_effect = [credit_transactions, debit_transactions]
        
        with patch('transaction.collection_accounts', mock_accounts), \
             patch('transaction.collection_transactions', mock_transactions):
            from transaction import TransactionGeneric
            trans = TransactionGeneric()
            request = DotMap({'account_number': 'IBAN1111111111111111'})
            result = trans.GetTransactionsHistory(request)
            
            assert len(result) == 2

    def test_get_transactions_history_empty(self, mock_collections):
        mock_accounts, mock_transactions = mock_collections
        
        mock_transactions.find.side_effect = [[], []]
        
        with patch('transaction.collection_accounts', mock_accounts), \
             patch('transaction.collection_transactions', mock_transactions):
            from transaction import TransactionGeneric
            trans = TransactionGeneric()
            request = DotMap({'account_number': 'IBAN1111111111111111'})
            result = trans.GetTransactionsHistory(request)
            
            assert result == []


class TestTransactionFlaskEndpoints:
    
    @pytest.fixture
    def client(self):
        with patch('transaction.collection_accounts', MagicMock()), \
             patch('transaction.collection_transactions', MagicMock()):
            from transaction import app
            app.config['TESTING'] = True
            with app.test_client() as client:
                yield client

    def test_transfer_endpoint(self, client):
        with patch('transaction.transaction_generic') as mock_generic:
            mock_generic.SendMoney.return_value = {
                'approved': True,
                'message': 'Transaction is Successful.'
            }
            
            response = client.post('/transfer',
                                   json={
                                       'sender_account_number': 'IBAN1111111111111111',
                                       'receiver_account_number': 'IBAN2222222222222222',
                                       'amount': '100',
                                       'reason': 'Test'
                                   },
                                   content_type='application/json')
            
            assert response.status_code == 200

    def test_zelle_endpoint(self, client):
        with patch('transaction.transaction_generic') as mock_generic:
            mock_generic.Zelle.return_value = {
                'approved': True,
                'message': 'Transaction is Successful.'
            }
            
            response = client.post('/zelle',
                                   json={
                                       'sender_email': 'sender@example.com',
                                       'receiver_email': 'receiver@example.com',
                                       'amount': '50',
                                       'reason': 'Zelle test'
                                   },
                                   content_type='application/json')
            
            assert response.status_code == 200

    def test_transaction_history_endpoint(self, client):
        with patch('transaction.transaction_generic') as mock_generic:
            mock_generic.GetTransactionsHistory.return_value = [
                {
                    'account_number': 'IBAN2222222222222222',
                    'amount': 100,
                    'reason': 'Test',
                    'time_stamp': '2024-01-01',
                    'type': 'credit',
                    'transaction_id': 'abc123'
                }
            ]
            
            response = client.post('/transaction-history',
                                   json={'account_number': 'IBAN1111111111111111'},
                                   content_type='application/json')
            
            assert response.status_code == 200

    def test_transaction_by_id_endpoint(self, client):
        with patch('transaction.transaction_generic') as mock_generic:
            mock_generic.GetTransactionByID.return_value = {
                'account_number': 'IBAN2222222222222222',
                'amount': 100,
                'reason': 'Test',
                'time_stamp': '2024-01-01',
                'type': 'credit',
                'transaction_id': 'abc123'
            }
            
            response = client.post('/transaction-with-id',
                                   json={'transaction_id': 'abc123'},
                                   content_type='application/json')
            
            assert response.status_code == 200
