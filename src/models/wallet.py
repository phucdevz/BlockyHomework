import hashlib
import json
from typing import Dict, Any, List, Tuple
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from ecdsa.util import sigencode_der, sigdecode_der
from .transaction import Transaction


class Wallet:
    def __init__(self, private_key: str = None):
        if private_key:
            self.private_key = private_key
            self.signing_key = SigningKey.from_string(bytes.fromhex(private_key), curve=SECP256k1)
        else:
            self.signing_key = SigningKey.generate(curve=SECP256k1)
            self.private_key = self.signing_key.to_string().hex()
        
        self.verifying_key = self.signing_key.get_verifying_key()
        self.public_key = self.verifying_key.to_string().hex()
        self.address = self.generate_address()
    
    def generate_address(self) -> str:
        address_data = {
            'public_key': self.public_key,
            'timestamp': 0
        }
        address_string = json.dumps(address_data, sort_keys=True)
        return hashlib.sha256(address_string.encode()).hexdigest()
    
    def get_balance(self, blockchain) -> float:
        balance = 0.0
        
        for block in blockchain.chain:
            for transaction in block.transactions:
                if transaction.recipient == self.address:
                    balance += transaction.amount
                if transaction.sender == self.address:
                    balance -= transaction.amount
        
        return balance
    
    def create_transaction(self, recipient: str, amount: float) -> Transaction:
        transaction = Transaction(
            sender=self.address,
            recipient=recipient,
            amount=amount
        )
        
        transaction.sign_transaction(self.private_key)
        return transaction
    
    def sign_transaction(self, transaction: Transaction) -> bool:
        return transaction.sign_transaction(self.private_key)
    
    def verify_transaction(self, transaction: Transaction) -> bool:
        return transaction.verify_signature()
    
    def get_transaction_history(self, blockchain) -> List[Transaction]:
        history = []
        
        for block in blockchain.chain:
            for transaction in block.transactions:
                if transaction.sender == self.address or transaction.recipient == self.address:
                    history.append(transaction)
        
        return history
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'address': self.address,
            'public_key': self.public_key,
            'private_key': self.private_key
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Wallet':
        wallet = cls()
        wallet.private_key = data['private_key']
        wallet.public_key = data['public_key']
        wallet.address = data['address']
        wallet.signing_key = SigningKey.from_string(bytes.fromhex(wallet.private_key), curve=SECP256k1)
        wallet.verifying_key = wallet.signing_key.get_verifying_key()
        return wallet
    
    def __str__(self) -> str:
        return f"Wallet: {self.address[:8]}... (Balance: {self.get_balance(None)} ZTL Coin)"
    
    def __repr__(self) -> str:
        return f"Wallet(address='{self.address[:8]}...')" 