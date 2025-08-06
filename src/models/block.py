"""
Block model for BlockyHomework blockchain system.
Represents a single block in the blockchain.
"""

import hashlib
import json
import time
from typing import List, Dict, Any, Optional
from .transaction import Transaction


class Block:
    """
    Represents a block in the blockchain.
    
    Attributes:
        index (int): The block's position in the blockchain
        timestamp (float): When the block was created
        transactions (List[Transaction]): List of transactions in the block
        proof (int): The proof of work nonce
        previous_hash (str): Hash of the previous block
        hash (str): Hash of this block
    """
    
    def __init__(self, index: int, transactions: List[Transaction], 
                 proof: int, previous_hash: str):
        """
        Initialize a new block.
        
        Args:
            index: Block's position in the chain
            transactions: List of transactions to include
            proof: Proof of work nonce
            previous_hash: Hash of the previous block
        """
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.proof = proof
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """
        Calculate the hash of the block using SHA-256.
        
        Returns:
            str: The block's hash
        """
        block_string = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert block to dictionary for serialization.
        
        Returns:
            Dict containing block data
        """
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'proof': self.proof,
            'previous_hash': self.previous_hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        """
        Create a Block instance from dictionary.
        
        Args:
            data: Dictionary containing block data
            
        Returns:
            Block instance
        """
        transactions = [Transaction.from_dict(tx) for tx in data['transactions']]
        return cls(
            index=data['index'],
            transactions=transactions,
            proof=data['proof'],
            previous_hash=data['previous_hash']
        )
    
    def mine_proof_of_work(self, difficulty: int = 4) -> int:
        """
        Mine the block by finding a valid proof of work.
        
        Args:
            difficulty: Number of leading zeros required
            
        Returns:
            int: The valid proof of work
        """
        target = '0' * difficulty
        
        while True:
            self.proof += 1
            self.hash = self.calculate_hash()
            
            if self.hash[:difficulty] == target:
                return self.proof
    
    def is_valid(self) -> bool:
        """
        Validate the block structure and proof of work.
        
        Returns:
            bool: True if block is valid
        """
        # Check if hash is correct
        if self.hash != self.calculate_hash():
            return False
        
        # Check if proof of work is valid (basic check)
        if not self.proof or self.proof <= 0:
            return False
        
        # Check if all transactions are valid
        for transaction in self.transactions:
            if not transaction.is_valid():
                return False
        
        return True
    
    def __str__(self) -> str:
        """String representation of the block."""
        return f"Block #{self.index} - Hash: {self.hash[:8]}..."
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Block(index={self.index}, hash='{self.hash[:8]}...', proof={self.proof})" 