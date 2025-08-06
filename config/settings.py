"""
Settings configuration for BlockyHomework blockchain system.
"""

class Config:
    # Blockchain Settings
    DIFFICULTY = 4
    BLOCK_REWARD = 10
    BLOCK_SIZE_LIMIT = 1000
    
    # Network Settings
    DEFAULT_PORT = 5000
    P2P_TIMEOUT = 30
    MAX_PEERS = 10
    
    # Security Settings
    KEY_SIZE = 256
    HASH_ALGORITHM = 'sha256'
    
    # UI Settings
    REFRESH_INTERVAL = 5000  # ms
    MAX_DISPLAY_BLOCKS = 50
    
    # Development Settings
    DEBUG = True
    LOG_LEVEL = 'INFO' 