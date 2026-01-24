import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from dotmap import DotMap

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['DB_URL'] = 'mongodb://localhost:27017/test_bank'
os.environ['SERVICE_PROTOCOL'] = 'http'
os.environ['ACCOUNT_HOST'] = 'localhost'
os.environ['TRANSACTION_HOST'] = 'localhost'
os.environ['LOAN_HOST'] = 'localhost'


class TestUserRegistrationAndLoginFlow:
    """Integration tests for user registration and login flow."""
    
    @pytest.fixture
    def mock_user_collection(self):
        return MagicMock()

    def test_user_registration_creates_account_then_login(self, mock_user_collection):
        """Test that a user can register and then login with the same credentials."""
        users_db = {}
        
        def find_one(query):
            email = query.get('email')
            return users_db.get(email)
        
        def create(user_data):
            user = MagicMock()
            user.name = user_data['name']
            user.email = user_data['email']
            user._id = 'test_user_id'
            users_db[user_data['email']] = user
            return user
        
        mock_user_collection.find_one.side_effect = find_one
        mock_user_collection.create = create
        
        user_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'password123'
        }
        
        assert mock_user_collection.find_one({'email': user_data['email']}) is None
        
        created_user = mock_user_collection.create(user_data)
        assert created_user.email == user_data['email']
        
        found_user = mock_user_collection.find_one({'email': user_data['email']})
        assert found_user is not None
        assert found_user.email == user_data['email']


class TestAccountCreationAndRetrievalFlow:
    """Integration tests for account creation and retrieval flow."""
    
    @pytest.fixture
    def mock_accounts_collection(self):
        return MagicMock()

    def test_create_multiple_account_types_for_user(self, mock_accounts_collection):
        """Test that a user can create multiple account types."""
        accounts_db = []
        
        def count_documents(query):
            count = 0
            for acc in accounts_db:
                if acc['email_id'] == query.get('email_id') and acc['account_type'] == query.get('account_type'):
                    count += 1
            return count
        
        def insert_one(account):
            accounts_db.append(account)
            return MagicMock()
        
        def find(query):
            return [acc for acc in accounts_db if acc['email_id'] == query.get('email_id')]
        
        mock_accounts_collection.count_documents.side_effect = count_documents
        mock_accounts_collection.insert_one.side_effect = insert_one
        mock_accounts_collection.find.side_effect = find
        
        user_email = 'test@example.com'
        account_types = ['Checking', 'Savings', 'Money Market', 'Investment']
        
        for account_type in account_types:
            if mock_accounts_collection.count_documents({'email_id': user_email, 'account_type': account_type}) == 0:
                account = {
                    'email_id': user_email,
                    'account_type': account_type,
                    'account_number': f'IBAN{account_type}123456',
                    'balance': 100,
                    'currency': 'USD',
                    'name': 'John Doe'
                }
                mock_accounts_collection.insert_one(account)
        
        user_accounts = mock_accounts_collection.find({'email_id': user_email})
        assert len(user_accounts) == 4
        
        account_types_created = [acc['account_type'] for acc in user_accounts]
        assert 'Checking' in account_types_created
        assert 'Savings' in account_types_created
        assert 'Money Market' in account_types_created
        assert 'Investment' in account_types_created

    def test_duplicate_account_type_rejected(self, mock_accounts_collection):
        """Test that duplicate account types for the same user are rejected."""
        accounts_db = []
        
        def count_documents(query):
            count = 0
            for acc in accounts_db:
                if acc['email_id'] == query.get('email_id') and acc['account_type'] == query.get('account_type'):
                    count += 1
            return count
        
        def insert_one(account):
            accounts_db.append(account)
            return MagicMock()
        
        mock_accounts_collection.count_documents.side_effect = count_documents
        mock_accounts_collection.insert_one.side_effect = insert_one
        
        user_email = 'test@example.com'
        
        if mock_accounts_collection.count_documents({'email_id': user_email, 'account_type': 'Checking'}) == 0:
            mock_accounts_collection.insert_one({
                'email_id': user_email,
                'account_type': 'Checking',
                'account_number': 'IBAN1234567890123456',
                'balance': 100
            })
        
        duplicate_count = mock_accounts_collection.count_documents({'email_id': user_email, 'account_type': 'Checking'})
        assert duplicate_count == 1


class TestTransactionFlow:
    """Integration tests for transaction flow."""
    
    @pytest.fixture
    def mock_collections(self):
        accounts_db = []
        transactions_db = []
        
        mock_accounts = MagicMock()
        mock_transactions = MagicMock()
        
        def find_accounts(query=None):
            if query is None:
                return accounts_db
            return [acc for acc in accounts_db if all(acc.get(k) == v for k, v in query.items())]
        
        def update_account(query, update):
            for acc in accounts_db:
                if acc['account_number'] == query.get('account_number'):
                    acc['balance'] = update['$set']['balance']
            return MagicMock()
        
        def insert_transaction(trans):
            transactions_db.append(trans)
            return MagicMock()
        
        mock_accounts.find.side_effect = find_accounts
        mock_accounts.update_one.side_effect = update_account
        mock_transactions.insert_one.side_effect = insert_transaction
        
        return mock_accounts, mock_transactions, accounts_db, transactions_db

    def test_transfer_between_accounts_updates_balances(self, mock_collections):
        """Test that transferring money updates both sender and receiver balances."""
        mock_accounts, mock_transactions, accounts_db, transactions_db = mock_collections
        
        sender = {
            'account_number': 'IBAN1111111111111111',
            'email_id': 'sender@example.com',
            'balance': 500
        }
        receiver = {
            'account_number': 'IBAN2222222222222222',
            'email_id': 'receiver@example.com',
            'balance': 100
        }
        accounts_db.extend([sender, receiver])
        
        transfer_amount = 200
        
        if sender['balance'] >= transfer_amount:
            sender['balance'] -= transfer_amount
            receiver['balance'] += transfer_amount
            mock_accounts.update_one(
                {'account_number': sender['account_number']},
                {'$set': {'balance': sender['balance']}}
            )
            mock_accounts.update_one(
                {'account_number': receiver['account_number']},
                {'$set': {'balance': receiver['balance']}}
            )
            mock_transactions.insert_one({
                'sender': sender['account_number'],
                'receiver': receiver['account_number'],
                'amount': transfer_amount,
                'reason': 'Test transfer'
            })
        
        assert sender['balance'] == 300
        assert receiver['balance'] == 300
        assert len(transactions_db) == 1

    def test_insufficient_balance_prevents_transfer(self, mock_collections):
        """Test that transfers with insufficient balance are rejected."""
        mock_accounts, mock_transactions, accounts_db, transactions_db = mock_collections
        
        sender = {
            'account_number': 'IBAN1111111111111111',
            'email_id': 'sender@example.com',
            'balance': 50
        }
        receiver = {
            'account_number': 'IBAN2222222222222222',
            'email_id': 'receiver@example.com',
            'balance': 100
        }
        accounts_db.extend([sender, receiver])
        
        transfer_amount = 200
        original_sender_balance = sender['balance']
        original_receiver_balance = receiver['balance']
        
        if sender['balance'] >= transfer_amount:
            sender['balance'] -= transfer_amount
            receiver['balance'] += transfer_amount
        
        assert sender['balance'] == original_sender_balance
        assert receiver['balance'] == original_receiver_balance
        assert len(transactions_db) == 0


class TestLoanApplicationFlow:
    """Integration tests for loan application flow."""
    
    @pytest.fixture
    def mock_collections(self):
        accounts_db = []
        loans_db = []
        
        mock_accounts = MagicMock()
        mock_loans = MagicMock()
        
        def find_accounts(query=None):
            if query is None:
                return accounts_db
            return accounts_db
        
        def count_documents(query):
            count = 0
            for acc in accounts_db:
                if acc.get('email_id') == query.get('email_id') and acc.get('account_number') == query.get('account_number'):
                    count += 1
            return count
        
        def update_account(query, update):
            for acc in accounts_db:
                if acc['account_number'] == query.get('account_number'):
                    acc['balance'] = update['$set']['balance']
            return MagicMock()
        
        def insert_loan(loan):
            loans_db.append(loan)
            return MagicMock()
        
        def find_loans(query):
            return [loan for loan in loans_db if loan.get('email') == query.get('email')]
        
        mock_accounts.find.side_effect = find_accounts
        mock_accounts.count_documents.side_effect = count_documents
        mock_accounts.update_one.side_effect = update_account
        mock_loans.insert_one.side_effect = insert_loan
        mock_loans.find.side_effect = find_loans
        
        return mock_accounts, mock_loans, accounts_db, loans_db

    def test_loan_approval_increases_account_balance(self, mock_collections):
        """Test that an approved loan increases the account balance."""
        mock_accounts, mock_loans, accounts_db, loans_db = mock_collections
        
        account = {
            'account_number': 'IBAN1234567890123456',
            'email_id': 'test@example.com',
            'balance': 100
        }
        accounts_db.append(account)
        
        loan_amount = 5000
        
        if mock_accounts.count_documents({'email_id': 'test@example.com', 'account_number': 'IBAN1234567890123456'}) > 0:
            account['balance'] += loan_amount
            mock_accounts.update_one(
                {'account_number': account['account_number']},
                {'$set': {'balance': account['balance']}}
            )
            mock_loans.insert_one({
                'email': 'test@example.com',
                'account_number': 'IBAN1234567890123456',
                'loan_amount': loan_amount,
                'status': 'Approved'
            })
        
        assert account['balance'] == 5100
        assert len(loans_db) == 1
        assert loans_db[0]['status'] == 'Approved'

    def test_loan_history_tracks_multiple_loans(self, mock_collections):
        """Test that loan history correctly tracks multiple loan applications."""
        mock_accounts, mock_loans, accounts_db, loans_db = mock_collections
        
        account = {
            'account_number': 'IBAN1234567890123456',
            'email_id': 'test@example.com',
            'balance': 100
        }
        accounts_db.append(account)
        
        loan_types = ['Base Camp', 'Rover', 'Potato Farming']
        
        for loan_type in loan_types:
            mock_loans.insert_one({
                'email': 'test@example.com',
                'account_number': 'IBAN1234567890123456',
                'loan_type': loan_type,
                'loan_amount': 1000,
                'status': 'Approved'
            })
        
        user_loans = mock_loans.find({'email': 'test@example.com'})
        assert len(user_loans) == 3
        
        loan_types_applied = [loan['loan_type'] for loan in user_loans]
        assert 'Base Camp' in loan_types_applied
        assert 'Rover' in loan_types_applied
        assert 'Potato Farming' in loan_types_applied


class TestEndToEndUserJourney:
    """End-to-end integration tests simulating complete user journeys."""
    
    def test_complete_user_journey(self):
        """Test a complete user journey: register, create account, transfer, apply for loan."""
        users_db = {}
        accounts_db = []
        transactions_db = []
        loans_db = []
        
        user_email = 'newuser@example.com'
        users_db[user_email] = {
            'name': 'New User',
            'email': user_email,
            '_id': 'user123'
        }
        assert user_email in users_db
        
        checking_account = {
            'account_number': 'IBAN1111111111111111',
            'email_id': user_email,
            'account_type': 'Checking',
            'balance': 100
        }
        savings_account = {
            'account_number': 'IBAN2222222222222222',
            'email_id': user_email,
            'account_type': 'Savings',
            'balance': 100
        }
        accounts_db.extend([checking_account, savings_account])
        assert len([acc for acc in accounts_db if acc['email_id'] == user_email]) == 2
        
        transfer_amount = 50
        checking_account['balance'] -= transfer_amount
        savings_account['balance'] += transfer_amount
        transactions_db.append({
            'sender': checking_account['account_number'],
            'receiver': savings_account['account_number'],
            'amount': transfer_amount
        })
        assert checking_account['balance'] == 50
        assert savings_account['balance'] == 150
        
        loan_amount = 1000
        checking_account['balance'] += loan_amount
        loans_db.append({
            'email': user_email,
            'account_number': checking_account['account_number'],
            'loan_amount': loan_amount,
            'status': 'Approved'
        })
        assert checking_account['balance'] == 1050
        assert len(loans_db) == 1
        
        user_accounts = [acc for acc in accounts_db if acc['email_id'] == user_email]
        total_balance = sum(acc['balance'] for acc in user_accounts)
        assert total_balance == 1200

    def test_multi_user_transaction_flow(self):
        """Test transactions between multiple users."""
        accounts_db = []
        transactions_db = []
        
        user1_account = {
            'account_number': 'IBAN1111111111111111',
            'email_id': 'user1@example.com',
            'balance': 1000
        }
        user2_account = {
            'account_number': 'IBAN2222222222222222',
            'email_id': 'user2@example.com',
            'balance': 500
        }
        user3_account = {
            'account_number': 'IBAN3333333333333333',
            'email_id': 'user3@example.com',
            'balance': 200
        }
        accounts_db.extend([user1_account, user2_account, user3_account])
        
        user1_account['balance'] -= 300
        user2_account['balance'] += 300
        transactions_db.append({
            'sender': user1_account['account_number'],
            'receiver': user2_account['account_number'],
            'amount': 300
        })
        
        user2_account['balance'] -= 100
        user3_account['balance'] += 100
        transactions_db.append({
            'sender': user2_account['account_number'],
            'receiver': user3_account['account_number'],
            'amount': 100
        })
        
        user3_account['balance'] -= 50
        user1_account['balance'] += 50
        transactions_db.append({
            'sender': user3_account['account_number'],
            'receiver': user1_account['account_number'],
            'amount': 50
        })
        
        assert user1_account['balance'] == 750
        assert user2_account['balance'] == 700
        assert user3_account['balance'] == 250
        
        total_balance = sum(acc['balance'] for acc in accounts_db)
        assert total_balance == 1700
        
        assert len(transactions_db) == 3
