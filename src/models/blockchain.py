import time
from typing import List, Dict, Any, Optional
from .block import Block
from .transaction import Transaction
from .wallet import Wallet
from .mempool import Mempool
from config.constants import GENESIS_BLOCK_HASH, MINING_DIFFICULTY, BLOCK_REWARD


class Blockchain:
    def __init__(self):
        self.chain = []
        self.mempool = Mempool()
        self.difficulty = MINING_DIFFICULTY
        self.block_reward = BLOCK_REWARD
        self.create_genesis_block()
    
    def create_genesis_block(self):
        genesis_transaction = Transaction(
            sender="0",
            recipient="0000000000000000000000000000000000000000000000000000000000000000",
            amount=0
        )
        
        genesis_block = Block(
            index=0,
            transactions=[genesis_transaction],
            proof=100,
            previous_hash=GENESIS_BLOCK_HASH
        )
        
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        return self.chain[-1]
    
    def add_transaction(self, transaction: Transaction) -> bool:
        if not transaction.is_valid():
            return False
        
        return self.mempool.add_transaction(transaction)
    
    def mine_block(self, miner_address: str) -> Optional[Block]:
        if not self.mempool.get_transactions():
            return None
        
        latest_block = self.get_latest_block()
        new_block = Block(
            index=latest_block.index + 1,
            transactions=self.mempool.get_transactions_for_block(),
            proof=0,
            previous_hash=latest_block.hash
        )
        
        proof = new_block.mine_proof_of_work(self.difficulty)
        if proof:
            new_block.proof = proof
            new_block.hash = new_block.calculate_hash()
            
            reward_transaction = Transaction(
                sender="0",
                recipient=miner_address,
                amount=self.block_reward
            )
            new_block.transactions.insert(0, reward_transaction)
            
            self.chain.append(new_block)
            
            transaction_hashes = [tx.hash for tx in new_block.transactions[1:]]
            self.mempool.clear_transactions(transaction_hashes)
            
            self.adjust_difficulty()
            return new_block
        
        return None
    
    def adjust_difficulty(self):
        if len(self.chain) % 10 == 0:
            last_ten_blocks = self.chain[-10:]
            avg_mining_time = sum(block.timestamp - last_ten_blocks[i-1].timestamp 
                                for i, block in enumerate(last_ten_blocks[1:], 1)) / 9
            
            target_time = 60
            if avg_mining_time < target_time / 2:
                self.difficulty += 1
            elif avg_mining_time > target_time * 2:
                self.difficulty = max(1, self.difficulty - 1)
    
    def validate_chain(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            if current_block.previous_hash != previous_block.hash:
                return False
            
            if not current_block.is_valid():
                return False
            
            if current_block.hash != current_block.calculate_hash():
                return False
        
        return True
    
    def get_chain(self) -> List[Dict[str, Any]]:
        return [block.to_dict() for block in self.chain]
    
    def get_chain_length(self) -> int:
        return len(self.chain)
    
    def get_block_by_index(self, index: int) -> Optional[Block]:
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None
    
    def get_block_by_hash(self, block_hash: str) -> Optional[Block]:
        for block in self.chain:
            if block.hash == block_hash:
                return block
        return None
    
    def get_transaction_by_hash(self, transaction_hash: str) -> Optional[Transaction]:
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.hash == transaction_hash:
                    return transaction
        return None
    
    def get_balance(self, address: str) -> float:
        balance = 0.0
        
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.recipient == address:
                    balance += transaction.amount
                if transaction.sender == address:
                    balance -= transaction.amount
        
        return balance
    
    def replace_chain(self, new_chain: List[Block]) -> bool:
        if len(new_chain) <= len(self.chain):
            return False
        
        if not all(block.is_valid() for block in new_chain):
            return False
        
        for i in range(1, len(new_chain)):
            current_block = new_chain[i]
            previous_block = new_chain[i-1]
            
            if current_block.previous_hash != previous_block.hash:
                return False
        
        self.chain = new_chain
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'chain': [block.to_dict() for block in self.chain],
            'difficulty': self.difficulty,
            'block_reward': self.block_reward,
            'mempool': self.mempool.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Blockchain':
        blockchain = cls()
        blockchain.chain = []
        
        for block_data in data.get('chain', []):
            block = Block.from_dict(block_data)
            blockchain.chain.append(block)
        
        blockchain.difficulty = data.get('difficulty', MINING_DIFFICULTY)
        blockchain.block_reward = data.get('block_reward', BLOCK_REWARD)
        blockchain.mempool = Mempool.from_dict(data.get('mempool', {}))
        
        return blockchain
    
    def __str__(self) -> str:
        return f"Blockchain: {len(self.chain)} blocks, Difficulty: {self.difficulty}"
    
    def __repr__(self) -> str:
        return f"Blockchain(blocks={len(self.chain)}, difficulty={self.difficulty})" 