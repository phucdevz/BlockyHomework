<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:8EC5FC,100:E0C3FC&height=180&section=header&text=BlockyHomework&fontSize=45&fontAlign=50&fontColor=fff" alt="BlockyHomework Banner"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square"/>
  <img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square"/>
  <img src="https://img.shields.io/badge/Made%20by-Zero%20Latency%20Team-orange?style=flat-square"/>
</p>

---

- **Complete Blockchain Implementation**: Full PoW (Proof of Work) consensus mechanism
- **P2P Network**: Peer-to-peer networking with automatic node discovery
- **Web Interface**: Modern, responsive UI for blockchain interaction
- **Attack Simulation**: 51% attack simulation for educational purposes
- **MVVM Architecture**: Clean separation of concerns with Model-View-ViewModel pattern
- **ZTL Coin**: Native cryptocurrency for the blockchain network
**BlockyHomework**  
> _A student-crafted, MVVM-powered, fully interactive blockchain playground for learning, research, and innovation._

---

## Overview

**BlockyHomework** is a miniature yet powerful blockchain system developed with Python and MVVM architecture, enabling students and enthusiasts to visualize, interact with, and experiment on core blockchain concepts — all in one clean and modern web interface.

- **Proof-of-Work mining**  
- **Peer-to-peer networking (P2P)**  
- **Secure wallet & transaction signing**  
- **Consensus & chain synchronization**  
- **51% attack simulation module**  
- **Modular, extensible, and hackable for all levels**

---

## Key Features

- **Intuitive MVVM Design:**  
  Modular code separation (Model, ViewModel, View) for maximum scalability and clean maintenance.

- **Proof-of-Work Blockchain:**  
  Mine new blocks, adjust difficulty, and understand security by design.

- **P2P Node Discovery & Networking:**  
  Connect, register, and sync with other nodes—no manual setup needed.

- **Digital Wallet & Transaction Signing:**  
  Create and sign transactions securely using your private key.

- **51% Attack Simulation:**  
  Experience consensus mechanisms and blockchain vulnerabilities firsthand.

- **Modern Web Interface:**  
  Simple, responsive, and interactive for all users.

---

## Quick Start

1. **Clone the repo:**
    ```bash
    git clone https://github.com/phucdevz/BlockyHomework.git
    cd BlockyHomework
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Run your first node:**
    ```bash
    python run.py
    ```
    Open your browser at [http://localhost:5000](http://localhost:5000)

4. **Launch multiple nodes:**  
   Open new terminals and run on different ports:  
    ```bash
    python run.py --port 5001
    ```

---

## Core Concepts

- **Blockchain:** Immutable ledger secured by cryptographic hashes, proof-of-work, and digital signatures.
- **Mining:** Find valid nonces to add blocks; get rewarded and secure the chain.
- **Transactions:** Signed and broadcast to the network. Validated and stored immutably.
- **Consensus:** Nodes auto-select the longest valid chain (Nakamoto consensus).
- **P2P Networking:** Nodes discover each other and sync chains automatically.
- **MVVM Pattern:** Clean separation between logic, data, and presentation.

---

## 51% Attack Simulation

> Try the [scripts/simulate_51_attack.py](scripts/simulate_51_attack.py) module to visualize a 51% attack scenario, learn about blockchain security, and see the chain resolve forks in real time.

---

## User Interface Preview

<img src="https://raw.githubusercontent.com/phucdevz/BlockyHomework/main/docs/ui_mockup.png" alt="UI Preview" width="80%"/>

---

## Documentation

- [API Reference](docs/api.md)
- [System Design & Architecture](docs/architecture.md)
- [How MVVM Works in BlockyHomework](docs/mvvm.md)

---

## Authors & Contributors

**Zero Latency Team From University of Transport**  
- Nguyễn Trường Phục  
- Nguyễn Phạm Thiên Phước  
- Nguyễn Đức Lượng  
- Lê Đức Anh  

Contact: [phucdeeptry723@gmail.com](mailto:phucdeeptry723@gmail.com)

---

## Contribution

We welcome all PRs, issue reports, and suggestions!  
Fork the repo, make a branch, and let’s build something great together.




