import hashlib
import json
import time
from typing import Dict, Any, Optional
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from ecdsa.util import sigencode_der, sigdecode_der


class Transaction:
    def __init__(self, sender: str, recipient: str, amount: float, signature: str = None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = time.time()
        self.signature = signature
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        transaction_string = json.dumps({
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp
        }, sort_keys=True)
        return hashlib.sha256(transaction_string.encode()).hexdigest()
    
    def sign_transaction(self, private_key: str) -> bool:
        try:
            signing_key = SigningKey.from_string(bytes.fromhex(private_key), curve=SECP256k1)
            transaction_hash = self.calculate_hash()
            signature = signing_key.sign(transaction_hash.encode(), sigencode=sigencode_der)
            self.signature = signature.hex()
            return True
        except Exception:
            return False
    
    def verify_signature(self) -> bool:
        if not self.signature:
            return False
        
        try:
            verifying_key = VerifyingKey.from_string(bytes.fromhex(self.sender), curve=SECP256k1)
            transaction_hash = self.calculate_hash()
            signature_bytes = bytes.fromhex(self.signature)
            return verifying_key.verify(signature_bytes, transaction_hash.encode(), sigdecode=sigdecode_der)
        except Exception:
            return False
    
    def is_valid(self) -> bool:
        if self.amount <= 0:
            return False
        
        if not self.sender or not self.recipient:
            return False
        
        if self.sender == self.recipient:
            return False
        
        return self.verify_signature()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp,
            'signature': self.signature,
            'hash': self.hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        transaction = cls(
            sender=data['sender'],
            recipient=data['recipient'],
            amount=data['amount']
        )
        transaction.timestamp = data.get('timestamp', time.time())
        transaction.signature = data.get('signature')
        transaction.hash = data.get('hash', transaction.calculate_hash())
        return transaction
    
    def __str__(self) -> str:
        return f"Transaction: {self.sender[:8]}... -> {self.recipient[:8]}... ({self.amount} ZTL Coin)"
    
    def __repr__(self) -> str:
        return f"Transaction(sender='{self.sender[:8]}...', recipient='{self.recipient[:8]}...', amount={self.amount})" 