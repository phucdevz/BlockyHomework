# BlockyHomework

A student-made mini blockchain project for learning, demonstration, and fun!

> **BlockyHomework** is a miniature blockchain system built with Python for educational purposes. It features Proof-of-Work, peer-to-peer networking, a basic wallet, transaction signing, and a simple web interface. Designed with MVVM architecture for modularity and easy extension. Includes a 51% attack simulation for research and teaching.

---

## Features

- Create, sign, and broadcast transactions
- Proof-of-Work mining with adjustable difficulty
- Peer-to-peer (P2P) networking and node discovery
- Blockchain synchronization (consensus: longest chain rule)
- Simple web interface for interaction and visualization
- Modular MVVM codebase – easy to read, maintain, and expand
- 51% attack simulation module for security experiments

---

## Project Structure

blockyhomework/
├── app/
│ ├── model/ # Block, Transaction, Wallet, Blockchain logic
│ ├── viewmodel/ # NodeViewModel: business logic, state handling
│ ├── view/ # Flask/FastAPI web routes & HTML templates
│ ├── networking/ # Peer discovery, sync, RESTful API
│ ├── utils/ # Crypto helpers, logging
│ └── config.py
├── scripts/ # Simulation (e.g., 51% attack)
├── tests/ # Unit and integration tests
├── requirements.txt
├── README.md
└── run.py # Entry point to start a node


---

## 🚀 Quick Start

1. **Install requirements:**
    ```bash
    pip install -r requirements.txt
    ```

2. **Run a node:**
    ```bash
    python run.py
    ```
    Open your browser at [http://localhost:5000](http://localhost:5000)

3. **Try multi-node:**
    - Start on different ports for multiple nodes (e.g., `python run.py --port 5001`).
    - Register new peers via the web UI or API.

---

## Core Concepts

- **Blockchain:** Immutable, linked list of blocks, each containing verified transactions.
- **Mining:** Proof-of-Work to add new blocks and secure the chain.
- **Transactions:** Signed with private keys, validated by network.
- **Consensus:** Nodes accept the longest valid chain.
- **P2P Networking:** Nodes discover and sync with each other automatically.
- **MVVM:** Clear separation between data (Model), logic (ViewModel), and interface (View).

---

## Educational Use

BlockyHomework is designed for students, teachers, and anyone curious about blockchain. You can:
- Visualize how transactions and mining work
- Experiment with consensus and security scenarios (like 51% attacks)
- Extend for your own research or coursework

---

## 🛡️ 51% Attack Simulation

A built-in module lets you simulate a 51% attack, visualizing chain forks and network takeover attempts—ideal for learning about blockchain security.

---

## Documentation

- [Project Overview](docs/overview.md)
- [API Reference](docs/api.md)
- [How MVVM Works in BlockyHomework](docs/mvvm.md)

---

## Contributing

PRs and suggestions are welcome! Fork the repo, create a branch, and submit your improvements.

---

## License



