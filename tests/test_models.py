"""
Unit tests for BlockyHomework model layer.
Tests Block, Transaction, Wallet, Blockchain, and Mempool classes.
"""

import unittest
import time
import json
from unittest.mock import Mock, patch

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.block import Block
from models.transaction import Transaction
from models.wallet import Wallet
from models.blockchain import Blockchain
from models.mempool import Mempool


class TestBlock(unittest.TestCase):
    """Test cases for Block class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.transactions = [
            Transaction("sender1", "recipient1", 10.0),
            Transaction("sender2", "recipient2", 5.0)
        ]
        self.block = Block(
            index=1,
            transactions=self.transactions,
            proof=12345,
            previous_hash="0000000000000000000000000000000000000000000000000000000000000000"
        )
    
    def test_block_creation(self):
        """Test block creation with valid parameters."""
        self.assertEqual(self.block.index, 1)
        self.assertEqual(len(self.block.transactions), 2)
        self.assertEqual(self.block.proof, 12345)
        self.assertEqual(self.block.previous_hash, "0000000000000000000000000000000000000000000000000000000000000000")
        self.assertIsNotNone(self.block.timestamp)
        self.assertIsNotNone(self.block.hash)
    
    def test_calculate_hash(self):
        """Test hash calculation."""
        original_hash = self.block.hash
        new_hash = self.block.calculate_hash()
        self.assertEqual(original_hash, new_hash)
        
        # Hash should change when block data changes
        self.block.proof = 54321
        updated_hash = self.block.calculate_hash()
        self.assertNotEqual(original_hash, updated_hash)
    
    def test_to_dict(self):
        """Test block serialization to dictionary."""
        block_dict = self.block.to_dict()
        
        self.assertEqual(block_dict['index'], 1)
        self.assertEqual(block_dict['proof'], 12345)
        self.assertEqual(block_dict['previous_hash'], "0000000000000000000000000000000000000000000000000000000000000000")
        self.assertEqual(len(block_dict['transactions']), 2)
        self.assertIn('timestamp', block_dict)
    
    def test_from_dict(self):
        """Test block deserialization from dictionary."""
        block_dict = self.block.to_dict()
        new_block = Block.from_dict(block_dict)
        
        self.assertEqual(new_block.index, self.block.index)
        self.assertEqual(new_block.proof, self.block.proof)
        self.assertEqual(new_block.previous_hash, self.block.previous_hash)
        self.assertEqual(len(new_block.transactions), len(self.block.transactions))
    
    def test_mine_proof_of_work(self):
        """Test proof of work mining."""
        difficulty = 2
        proof = self.block.mine_proof_of_work(difficulty)
        
        self.assertIsNotNone(proof)
        self.assertGreater(proof, 0)
        
        # Verify the proof is valid
        self.block.proof = proof
        block_hash = self.block.calculate_hash()
        self.assertTrue(block_hash.startswith('0' * difficulty))
    
    def test_is_valid(self):
        """Test block validation."""
        # Valid block should pass validation
        self.assertTrue(self.block.is_valid())
        
        # Invalid hash should fail validation
        original_hash = self.block.hash
        self.block.hash = "invalid_hash"
        self.assertFalse(self.block.is_valid())
        self.block.hash = original_hash
        
        # Invalid proof should fail validation
        original_proof = self.block.proof
        self.block.proof = 0
        self.assertFalse(self.block.is_valid())
        self.block.proof = original_proof


class TestTransaction(unittest.TestCase):
    """Test cases for Transaction class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.transaction = Transaction(
            sender="sender_address",
            recipient="recipient_address",
            amount=25.5
        )
    
    def test_transaction_creation(self):
        """Test transaction creation with valid parameters."""
        self.assertEqual(self.transaction.sender, "sender_address")
        self.assertEqual(self.transaction.recipient, "recipient_address")
        self.assertEqual(self.transaction.amount, 25.5)
        self.assertIsNotNone(self.transaction.timestamp)
        self.assertIsNotNone(self.transaction.hash)
    
    def test_calculate_hash(self):
        """Test transaction hash calculation."""
        original_hash = self.transaction.hash
        new_hash = self.transaction.calculate_hash()
        self.assertEqual(original_hash, new_hash)
        
        # Hash should change when transaction data changes
        self.transaction.amount = 30.0
        updated_hash = self.transaction.calculate_hash()
        self.assertNotEqual(original_hash, updated_hash)
    
    def test_sign_transaction(self):
        """Test transaction signing."""
        # Create a wallet for signing
        wallet = Wallet()
        
        # Sign the transaction
        success = self.transaction.sign_transaction(wallet.private_key)
        self.assertTrue(success)
        self.assertIsNotNone(self.transaction.signature)
    
    def test_verify_signature(self):
        """Test signature verification."""
        wallet = Wallet()
        
        # Sign and verify
        self.transaction.sign_transaction(wallet.private_key)
        self.assertTrue(self.transaction.verify_signature())
        
        # Invalid signature should fail
        self.transaction.signature = "invalid_signature"
        self.assertFalse(self.transaction.verify_signature())
    
    def test_is_valid(self):
        """Test transaction validation."""
        # Valid transaction should pass validation
        self.assertTrue(self.transaction.is_valid())
        
        # Invalid amount should fail
        self.transaction.amount = 0
        self.assertFalse(self.transaction.is_valid())
        self.transaction.amount = -5
        self.assertFalse(self.transaction.is_valid())
        self.transaction.amount = 25.5  # Reset
        
        # Invalid addresses should fail
        self.transaction.sender = ""
        self.assertFalse(self.transaction.is_valid())
        self.transaction.sender = "sender_address"  # Reset
        
        self.transaction.recipient = ""
        self.assertFalse(self.transaction.is_valid())
        self.transaction.recipient = "recipient_address"  # Reset
        
        # Same sender and recipient should fail
        self.transaction.recipient = "sender_address"
        self.assertFalse(self.transaction.is_valid())
    
    def test_to_dict(self):
        """Test transaction serialization."""
        transaction_dict = self.transaction.to_dict()
        
        self.assertEqual(transaction_dict['sender'], "sender_address")
        self.assertEqual(transaction_dict['recipient'], "recipient_address")
        self.assertEqual(transaction_dict['amount'], 25.5)
        self.assertIn('timestamp', transaction_dict)
        self.assertIn('hash', transaction_dict)
    
    def test_from_dict(self):
        """Test transaction deserialization."""
        transaction_dict = self.transaction.to_dict()
        new_transaction = Transaction.from_dict(transaction_dict)
        
        self.assertEqual(new_transaction.sender, self.transaction.sender)
        self.assertEqual(new_transaction.recipient, self.transaction.recipient)
        self.assertEqual(new_transaction.amount, self.transaction.amount)
        self.assertEqual(new_transaction.hash, self.transaction.hash)


class TestWallet(unittest.TestCase):
    """Test cases for Wallet class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wallet = Wallet()
        self.blockchain = Blockchain()
    
    def test_wallet_creation(self):
        """Test wallet creation."""
        self.assertIsNotNone(self.wallet.private_key)
        self.assertIsNotNone(self.wallet.public_key)
        self.assertIsNotNone(self.wallet.address)
        self.assertIsNotNone(self.wallet.signing_key)
        self.assertIsNotNone(self.wallet.verifying_key)
    
    def test_address_generation(self):
        """Test address generation from public key."""
        address = self.wallet.generate_address()
        self.assertIsNotNone(address)
        self.assertEqual(len(address), 64)  # SHA-256 hash length
        self.assertEqual(address, self.wallet.address)
    
    def test_get_balance(self):
        """Test balance calculation."""
        # Initial balance should be 0
        balance = self.wallet.get_balance(self.blockchain)
        self.assertEqual(balance, 0.0)
        
        # Add a transaction to the blockchain
        transaction = Transaction(
            sender="0",  # Genesis transaction
            recipient=self.wallet.address,
            amount=100.0
        )
        self.blockchain.chain[0].transactions.append(transaction)
        
        # Balance should now be 100
        balance = self.wallet.get_balance(self.blockchain)
        self.assertEqual(balance, 100.0)
    
    def test_create_transaction(self):
        """Test transaction creation."""
        recipient = "recipient_address"
        amount = 50.0
        
        transaction = self.wallet.create_transaction(recipient, amount)
        
        self.assertEqual(transaction.sender, self.wallet.address)
        self.assertEqual(transaction.recipient, recipient)
        self.assertEqual(transaction.amount, amount)
        self.assertTrue(transaction.verify_signature())
    
    def test_sign_transaction(self):
        """Test transaction signing."""
        transaction = Transaction(
            sender=self.wallet.address,
            recipient="recipient_address",
            amount=25.0
        )
        
        success = self.wallet.sign_transaction(transaction)
        self.assertTrue(success)
        self.assertTrue(transaction.verify_signature())
    
    def test_verify_transaction(self):
        """Test transaction verification."""
        transaction = self.wallet.create_transaction("recipient_address", 10.0)
        
        # Should verify successfully
        self.assertTrue(self.wallet.verify_transaction(transaction))
        
        # Invalid transaction should fail
        transaction.amount = 0
        self.assertFalse(self.wallet.verify_transaction(transaction))
    
    def test_get_transaction_history(self):
        """Test transaction history retrieval."""
        # Add some transactions to blockchain
        tx1 = Transaction("0", self.wallet.address, 100.0)
        tx2 = Transaction(self.wallet.address, "other_address", 50.0)
        
        self.blockchain.chain[0].transactions.extend([tx1, tx2])
        
        history = self.wallet.get_transaction_history(self.blockchain)
        self.assertEqual(len(history), 2)
    
    def test_to_dict(self):
        """Test wallet serialization."""
        wallet_dict = self.wallet.to_dict()
        
        self.assertEqual(wallet_dict['address'], self.wallet.address)
        self.assertEqual(wallet_dict['public_key'], self.wallet.public_key)
        self.assertEqual(wallet_dict['private_key'], self.wallet.private_key)
    
    def test_from_dict(self):
        """Test wallet deserialization."""
        wallet_dict = self.wallet.to_dict()
        new_wallet = Wallet.from_dict(wallet_dict)
        
        self.assertEqual(new_wallet.address, self.wallet.address)
        self.assertEqual(new_wallet.public_key, self.wallet.public_key)
        self.assertEqual(new_wallet.private_key, self.wallet.private_key)


class TestBlockchain(unittest.TestCase):
    """Test cases for Blockchain class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.blockchain = Blockchain()
        self.wallet = Wallet()
    
    def test_blockchain_creation(self):
        """Test blockchain creation."""
        self.assertIsNotNone(self.blockchain.chain)
        self.assertEqual(len(self.blockchain.chain), 1)  # Genesis block
        self.assertIsNotNone(self.blockchain.mempool)
        self.assertGreater(self.blockchain.difficulty, 0)
        self.assertGreater(self.blockchain.block_reward, 0)
    
    def test_genesis_block(self):
        """Test genesis block creation."""
        genesis_block = self.blockchain.chain[0]
        
        self.assertEqual(genesis_block.index, 0)
        self.assertEqual(genesis_block.previous_hash, "0000000000000000000000000000000000000000000000000000000000000000")
        self.assertEqual(len(genesis_block.transactions), 1)  # Genesis transaction
    
    def test_get_latest_block(self):
        """Test getting the latest block."""
        latest_block = self.blockchain.get_latest_block()
        self.assertEqual(latest_block.index, 0)  # Genesis block
    
    def test_add_transaction(self):
        """Test adding transactions to mempool."""
        transaction = self.wallet.create_transaction("recipient_address", 10.0)
        
        success = self.blockchain.add_transaction(transaction)
        self.assertTrue(success)
        self.assertEqual(len(self.blockchain.mempool.transactions), 1)
    
    def test_mine_block(self):
        """Test block mining."""
        # Add some transactions
        for i in range(3):
            transaction = self.wallet.create_transaction(f"recipient_{i}", 10.0)
            self.blockchain.add_transaction(transaction)
        
        # Mine a block
        block = self.blockchain.mine_block(self.wallet.address)
        
        self.assertIsNotNone(block)
        self.assertEqual(block.index, 1)
        self.assertEqual(len(self.blockchain.chain), 2)
        self.assertEqual(len(self.blockchain.mempool.transactions), 0)  # Transactions should be cleared
    
    def test_mine_block_no_transactions(self):
        """Test mining with no transactions."""
        block = self.blockchain.mine_block(self.wallet.address)
        self.assertIsNone(block)
    
    def test_adjust_difficulty(self):
        """Test difficulty adjustment."""
        original_difficulty = self.blockchain.difficulty
        
        # Mine some blocks to trigger difficulty adjustment
        for i in range(10):
            transaction = self.wallet.create_transaction(f"recipient_{i}", 10.0)
            self.blockchain.add_transaction(transaction)
            block = self.blockchain.mine_block(self.wallet.address)
            self.assertIsNotNone(block)
        
        # Difficulty should have been adjusted
        self.assertNotEqual(self.blockchain.difficulty, original_difficulty)
    
    def test_validate_chain(self):
        """Test chain validation."""
        # Valid chain should pass validation
        self.assertTrue(self.blockchain.validate_chain())
        
        # Add some blocks
        for i in range(3):
            transaction = self.wallet.create_transaction(f"recipient_{i}", 10.0)
            self.blockchain.add_transaction(transaction)
            block = self.blockchain.mine_block(self.wallet.address)
            self.assertIsNotNone(block)
        
        # Chain should still be valid
        self.assertTrue(self.blockchain.validate_chain())
    
    def test_get_chain(self):
        """Test getting chain data."""
        chain_data = self.blockchain.get_chain()
        self.assertEqual(len(chain_data), 1)  # Genesis block
        self.assertIsInstance(chain_data[0], dict)
    
    def test_get_chain_length(self):
        """Test getting chain length."""
        length = self.blockchain.get_chain_length()
        self.assertEqual(length, 1)  # Genesis block
        
        # Mine a block
        transaction = self.wallet.create_transaction("recipient", 10.0)
        self.blockchain.add_transaction(transaction)
        block = self.blockchain.mine_block(self.wallet.address)
        
        length = self.blockchain.get_chain_length()
        self.assertEqual(length, 2)
    
    def test_get_balance(self):
        """Test balance calculation for an address."""
        # Add transaction to blockchain
        transaction = Transaction("0", self.wallet.address, 100.0)
        self.blockchain.chain[0].transactions.append(transaction)
        
        balance = self.blockchain.get_balance(self.wallet.address)
        self.assertEqual(balance, 100.0)
    
    def test_replace_chain(self):
        """Test chain replacement."""
        # Create a longer valid chain
        new_chain = Blockchain()
        for i in range(5):
            transaction = Transaction("0", "recipient", 10.0)
            new_chain.add_transaction(transaction)
            block = new_chain.mine_block("miner")
            self.assertIsNotNone(block)
        
        # Replace current chain
        success = self.blockchain.replace_chain(new_chain.chain)
        self.assertTrue(success)
        self.assertEqual(len(self.blockchain.chain), 5)
    
    def test_replace_chain_invalid(self):
        """Test chain replacement with invalid chain."""
        # Try to replace with shorter chain
        new_chain = Blockchain()
        success = self.blockchain.replace_chain(new_chain.chain)
        self.assertFalse(success)


class TestMempool(unittest.TestCase):
    """Test cases for Mempool class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mempool = Mempool()
        self.wallet = Wallet()
    
    def test_mempool_creation(self):
        """Test mempool creation."""
        self.assertIsNotNone(self.mempool.transactions)
        self.assertEqual(len(self.mempool.transactions), 0)
        self.assertGreater(self.mempool.max_size, 0)
    
    def test_add_transaction(self):
        """Test adding valid transaction."""
        transaction = self.wallet.create_transaction("recipient", 10.0)
        
        success = self.mempool.add_transaction(transaction)
        self.assertTrue(success)
        self.assertEqual(len(self.mempool.transactions), 1)
    
    def test_add_invalid_transaction(self):
        """Test adding invalid transaction."""
        transaction = Transaction("sender", "recipient", 0)  # Invalid amount
        
        success = self.mempool.add_transaction(transaction)
        self.assertFalse(success)
        self.assertEqual(len(self.mempool.transactions), 0)
    
    def test_add_duplicate_transaction(self):
        """Test adding duplicate transaction."""
        transaction = self.wallet.create_transaction("recipient", 10.0)
        
        # Add first time
        success1 = self.mempool.add_transaction(transaction)
        self.assertTrue(success1)
        
        # Add second time (should fail)
        success2 = self.mempool.add_transaction(transaction)
        self.assertFalse(success2)
        self.assertEqual(len(self.mempool.transactions), 1)
    
    def test_remove_transaction(self):
        """Test removing transaction."""
        transaction = self.wallet.create_transaction("recipient", 10.0)
        self.mempool.add_transaction(transaction)
        
        success = self.mempool.remove_transaction(transaction.hash)
        self.assertTrue(success)
        self.assertEqual(len(self.mempool.transactions), 0)
    
    def test_get_transactions(self):
        """Test getting transactions."""
        # Add some transactions
        for i in range(3):
            transaction = self.wallet.create_transaction(f"recipient_{i}", 10.0)
            self.mempool.add_transaction(transaction)
        
        transactions = self.mempool.get_transactions()
        self.assertEqual(len(transactions), 3)
        
        # Test with limit
        limited_transactions = self.mempool.get_transactions(limit=2)
        self.assertEqual(len(limited_transactions), 2)
    
    def test_get_transaction_by_hash(self):
        """Test getting transaction by hash."""
        transaction = self.wallet.create_transaction("recipient", 10.0)
        self.mempool.add_transaction(transaction)
        
        found_transaction = self.mempool.get_transaction_by_hash(transaction.hash)
        self.assertEqual(found_transaction.hash, transaction.hash)
        
        # Test with non-existent hash
        not_found = self.mempool.get_transaction_by_hash("invalid_hash")
        self.assertIsNone(not_found)
    
    def test_clear_transactions(self):
        """Test clearing transactions."""
        # Add some transactions
        transactions = []
        for i in range(3):
            transaction = self.wallet.create_transaction(f"recipient_{i}", 10.0)
            self.mempool.add_transaction(transaction)
            transactions.append(transaction)
        
        # Clear specific transactions
        hashes_to_clear = [transactions[0].hash, transactions[1].hash]
        self.mempool.clear_transactions(hashes_to_clear)
        
        self.assertEqual(len(self.mempool.transactions), 1)
        self.assertEqual(self.mempool.transactions[0].hash, transactions[2].hash)
    
    def test_prioritize_transactions(self):
        """Test transaction prioritization."""
        # Add transactions with different amounts
        tx1 = self.wallet.create_transaction("recipient1", 5.0)
        tx2 = self.wallet.create_transaction("recipient2", 15.0)
        tx3 = self.wallet.create_transaction("recipient3", 10.0)
        
        self.mempool.add_transaction(tx1)
        self.mempool.add_transaction(tx2)
        self.mempool.add_transaction(tx3)
        
        prioritized = self.mempool.prioritize_transactions()
        
        # Should be sorted by fee (amount) in descending order
        self.assertEqual(prioritized[0].amount, 15.0)
        self.assertEqual(prioritized[1].amount, 10.0)
        self.assertEqual(prioritized[2].amount, 5.0)
    
    def test_get_transactions_for_block(self):
        """Test getting transactions for block."""
        # Add more transactions than block limit
        for i in range(150):
            transaction = self.wallet.create_transaction(f"recipient_{i}", 10.0)
            self.mempool.add_transaction(transaction)
        
        block_transactions = self.mempool.get_transactions_for_block(max_transactions=100)
        self.assertEqual(len(block_transactions), 100)
    
    def test_is_full(self):
        """Test mempool full status."""
        # Fill mempool
        for i in range(self.mempool.max_size):
            transaction = self.wallet.create_transaction(f"recipient_{i}", 10.0)
            self.mempool.add_transaction(transaction)
        
        self.assertTrue(self.mempool.is_full())
        
        # Try to add one more
        extra_transaction = self.wallet.create_transaction("recipient_extra", 10.0)
        success = self.mempool.add_transaction(extra_transaction)
        self.assertFalse(success)


if __name__ == '__main__':
    unittest.main()
