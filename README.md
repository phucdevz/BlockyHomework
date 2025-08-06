# BlockyHomework

A miniature blockchain system built with Python following the MVVM (Model-View-ViewModel) architecture pattern.

## 🚀 Features

- **Complete Blockchain Implementation**: Full PoW (Proof of Work) consensus mechanism
- **P2P Network**: Peer-to-peer networking with automatic node discovery
- **Web Interface**: Modern, responsive UI for blockchain interaction
- **Attack Simulation**: 51% attack simulation for educational purposes
- **MVVM Architecture**: Clean separation of concerns with Model-View-ViewModel pattern

## 📁 Project Structure

```
blocky_homework/
├── src/
│   ├── models/           # MODEL Layer - Core blockchain logic
│   ├── viewmodels/       # VIEWMODEL Layer - Business logic bridge
│   ├── views/            # VIEW Layer - UI templates and routes
│   ├── networking/       # P2P networking and API
│   ├── utils/            # Utility functions
│   └── simulation/       # Attack simulation features
├── config/               # Configuration settings
├── tests/                # Test suite
├── docs/                 # Documentation
└── scripts/              # Utility scripts
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/blocky-homework.git
   cd blocky-homework
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python scripts/start_node.py
   ```

## 🎯 Usage

### Starting a Node
```bash
python scripts/start_node.py --port 5000
```

### Creating a Wallet
```bash
python scripts/create_wallet.py
```

### Running Attack Simulation
```bash
python scripts/simulate_attack.py --type 51-percent --power 60 --duration 60
```

## 🌐 Web Interface

Access the web interface at `http://localhost:5000` to:

- **Dashboard**: View blockchain statistics and recent blocks
- **Transactions**: Create and view transactions
- **Mining**: Control mining operations
- **Network**: Monitor P2P network status
- **Simulation**: Run attack simulations

## 🏗️ Architecture

### MVVM Pattern Implementation

- **Model**: Core blockchain classes (Block, Transaction, Wallet, Blockchain)
- **ViewModel**: Business logic and state management (NodeViewModel, BlockchainViewModel)
- **View**: Web interface templates and routes

### Key Components

- **Blockchain Engine**: Complete PoW implementation with difficulty adjustment
- **P2P Network**: Automatic node discovery and synchronization
- **Web API**: RESTful endpoints for blockchain operations
- **Attack Simulator**: Educational 51% attack simulation

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v --cov=src
```

## 📚 Documentation

- [API Documentation](docs/api_documentation.md)
- [Deployment Guide](docs/deployment_guide.md)
- [User Manual](docs/user_manual.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by Bitcoin's blockchain architecture
- Built for educational purposes
- Uses modern Python development practices



