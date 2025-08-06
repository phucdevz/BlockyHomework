# BLOCKYHOMEWORK - KẾ HOẠCH PHÂN CÔNG ĐỘI NHÓM (2 TUẦN)

## THÔNG TIN ĐỘI NHÓM
- **Số lượng thành viên:** 4 người
- **Thời gian thực hiện:** 2 tuần (10 ngày làm việc)
- **Dự án:** BlockyHomework - Blockchain Miniature System
- **Kiến trúc:** MVVM (Model-View-ViewModel)

---

## PHÂN CÔNG THÀNH VIÊN

### 🧑‍💻 **THÀNH VIÊN 1: BACKEND DEVELOPER (Core Blockchain)**
**Tên:** [Tên thành viên]
**Vai trò:** Blockchain Core Developer
**Chuyên môn:** Python, Cryptography, Data Structures

#### **TUẦN 1:**
**Ngày 1-2:**
- [ ] Thiết kế và implement class `Block`
  - Cấu trúc block với index, timestamp, transactions, proof, previous_hash
  - Phương thức `calculate_hash()` sử dụng SHA-256
  - Validation logic cho block structure

**Ngày 3-4:**
- [ ] Thiết kế và implement class `Transaction`
  - Cấu trúc transaction với sender, recipient, amount, signature
  - Phương thức `sign_transaction()` và `verify_signature()` sử dụng ECDSA
  - Transaction validation logic

**Ngày 5:**
- [ ] Thiết kế và implement class `Wallet`
  - Key pair generation (ECDSA)
  - Balance calculation methods
  - Transaction creation methods

#### **TUẦN 2:**
**Ngày 6-7:**
- [ ] Implement class `Blockchain` (Core Engine)
  - Genesis block creation
  - Add transaction to mempool
  - Chain validation logic
  - Difficulty adjustment mechanism

**Ngày 8-9:**
- [ ] Proof of Work Implementation
  - Hashcash algorithm
  - Nonce finding mechanism
  - Mining difficulty calculation

**Ngày 10:**
- [ ] Testing và Documentation
  - Unit tests cho tất cả classes
  - API documentation
  - Code review và optimization

---

### 🎨 **THÀNH VIÊN 2: FRONTEND DEVELOPER (UI/UX)**
**Tên:** [Tên thành viên]
**Vai trò:** Frontend Developer & UI/UX Designer
**Chuyên môn:** HTML/CSS/JavaScript, Flask, User Interface Design

#### **TUẦN 1:**
**Ngày 1-2:**
- [ ] Thiết kế UI/UX cho hệ thống
  - Wireframes và mockups
  - Color scheme và typography
  - Responsive design planning

**Ngày 3-4:**
- [ ] Implement HTML Templates
  - `base.html` template với navigation
  - `dashboard.html` với blockchain overview
  - `transactions.html` với transaction form

**Ngày 5:**
- [ ] Implement CSS Styling
  - Modern, clean design
  - Responsive layout
  - Interactive elements styling

#### **TUẦN 2:**
**Ngày 6-7:**
- [ ] Implement JavaScript Functionality
  - Real-time updates
  - Form validation
  - Interactive blockchain explorer
  - Mining interface

**Ngày 8-9:**
- [ ] Additional UI Pages
  - `mining.html` với mining controls
  - `network.html` với network status
  - `simulation.html` với attack simulation

**Ngày 10:**
- [ ] UI Testing và Polish
  - Cross-browser testing
  - Mobile responsiveness
  - User experience optimization

---

### 🔗 **THÀNH VIÊN 3: NETWORKING DEVELOPER (P2P & API)**
**Tên:** [Tên thành viên]
**Vai trò:** Networking & API Developer
**Chuyên môn:** HTTP, Socket Programming, RESTful APIs

#### **TUẦN 1:**
**Ngày 1-2:**
- [ ] Setup Flask/FastAPI Server
  - Server configuration
  - Basic routing setup
  - Error handling middleware

**Ngày 3-4:**
- [ ] Implement Core API Endpoints
  - `POST /api/transactions/new`
  - `GET /api/chain`
  - `POST /api/mine`
  - `GET /api/transactions/pending`

**Ngày 5:**
- [ ] Implement Wallet API
  - `POST /api/wallet/create`
  - `GET /api/wallet/balance/{address}`
  - `POST /api/wallet/send`

#### **TUẦN 2:**
**Ngày 6-7:**
- [ ] Implement P2P Networking
  - Node discovery mechanism
  - Peer-to-peer communication
  - Network topology management

**Ngày 8-9:**
- [ ] Implement Broadcasting System
  - Transaction broadcasting
  - Block broadcasting
  - Network synchronization

**Ngày 10:**
- [ ] API Testing và Documentation
  - API testing với Postman/curl
  - API documentation
  - Performance optimization

---

### 🎯 **THÀNH VIÊN 4: VIEWMODEL DEVELOPER (Business Logic)**
**Tên:** [Tên thành viên]
**Vai trò:** ViewModel & Integration Developer
**Chuyên môn:** MVVM Pattern, State Management, Data Binding

#### **TUẦN 1:**
**Ngày 1-2:**
- [ ] Thiết kế ViewModel Architecture
  - MVVM pattern implementation
  - Data binding mechanisms
  - State management design

**Ngày 3-4:**
- [ ] Implement NodeViewModel Class
  - State management for node
  - Data binding with Model
  - Command pattern implementation

**Ngày 5:**
- [ ] Implement BlockchainViewModel Class
  - Chain display formatting
  - Transaction list management
  - Mining status tracking

#### **TUẦN 2:**
**Ngày 6-7:**
- [ ] ViewModel-Model Integration
  - Connect ViewModel với Blockchain Model
  - Implement data flow between layers
  - State synchronization mechanisms

**Ngày 8-9:**
- [ ] Command Implementation
  - Create transaction commands
  - Mine block commands
  - Network synchronization commands

**Ngày 10:**
- [ ] Integration Testing
  - End-to-end testing
  - MVVM pattern validation
  - Performance testing

---

## LỊCH TRÌNH HỢP TÁC

### **DAILY STANDUP (Mỗi ngày 9:00 AM)**
- **Thời gian:** 15 phút
- **Nội dung:**
  - Hôm qua đã làm gì?
  - Hôm nay sẽ làm gì?
  - Có gặp khó khăn gì không?

### **WEEKLY REVIEW (Cuối tuần)**
- **Thời gian:** 1 giờ
- **Nội dung:**
  - Demo progress
  - Code review
  - Planning cho tuần tiếp theo

### **INTEGRATION POINTS**
- **Ngày 5:** Integration test giữa Backend và ViewModel
- **Ngày 7:** Integration test giữa Frontend và API
- **Ngày 9:** Full system integration test
- **Ngày 10:** Final testing và deployment preparation

---

## DELIVERABLES SAU 2 TUẦN

### **TUẦN 1 DELIVERABLES:**
- ✅ Core blockchain classes (Block, Transaction, Wallet)
- ✅ Basic UI templates và styling
- ✅ Core API endpoints
- ✅ ViewModel architecture và basic implementation

### **TUẦN 2 DELIVERABLES:**
- ✅ Complete blockchain engine với PoW
- ✅ Full UI với JavaScript functionality
- ✅ P2P networking và broadcasting
- ✅ Complete MVVM integration

### **FINAL DELIVERABLES:**
- ✅ Working blockchain system với web interface
- ✅ P2P network với multiple nodes
- ✅ Complete API documentation
- ✅ Test suite với 90% coverage

---

## CÔNG CỤ VÀ MÔI TRƯỜNG

### **Development Tools:**
- **IDE:** VS Code (recommended)
- **Version Control:** Git với feature branches
- **Communication:** Slack/Discord cho daily updates
- **Project Management:** GitHub Issues/Trello

### **Testing Environment:**
- **Unit Testing:** pytest
- **API Testing:** Postman/curl
- **UI Testing:** Browser developer tools
- **Integration Testing:** Local network setup

### **Documentation:**
- **Code Documentation:** Docstrings và comments
- **API Documentation:** OpenAPI/Swagger
- **User Manual:** Markdown documentation
- **Architecture Documentation:** UML diagrams

---

## RISK MITIGATION

### **Technical Risks:**
- **Backend Developer:** Có backup plan cho cryptographic implementation
- **Frontend Developer:** Sử dụng CSS frameworks nếu cần
- **Networking Developer:** Có fallback cho P2P communication
- **ViewModel Developer:** Có simplified version nếu MVVM phức tạp

### **Team Risks:**
- **Communication:** Daily standup bắt buộc
- **Knowledge Sharing:** Code review sessions
- **Dependencies:** Clear interface definitions
- **Timeline:** Buffer time trong planning

---

## SUCCESS METRICS

### **Technical Metrics:**
- ✅ 90% code coverage
- ✅ All API endpoints working
- ✅ UI responsive trên mobile
- ✅ P2P network functional

### **Team Metrics:**
- ✅ Daily standup attendance
- ✅ Code review completion
- ✅ Documentation quality
- ✅ Integration success

---

**Document Version:** 1.0  
**Created by:** Project Manager  
**Team Size:** 4 members  
**Timeline:** 2 weeks  
**Next Review:** End of Week 1 