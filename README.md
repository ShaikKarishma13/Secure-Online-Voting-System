# Secure Online Voting System

## 📌 Project Overview

The **Secure Online Voting System** is a cybersecurity-focused web application developed using **Python Flask**, designed to provide a secure and transparent digital voting process.
The system uses modern cryptographic techniques such as:

* **AES Encryption**
* **RSA Encryption**
* **SHA-256 Hashing**

to ensure:

* secure vote transmission
* vote confidentiality
* integrity verification
* protected authentication
* tampering detection

The project also includes a professional analytics dashboard, cybersecurity-themed UI effects, downloadable encrypted receipts, and a vote verification system.

---

# 🚀 Key Objectives

* Build a secure online voting platform
* Prevent unauthorized access and duplicate voting
* Protect vote confidentiality using encryption
* Verify vote integrity using SHA-256 hashing
* Provide a professional admin analytics dashboard
* Demonstrate real-world cybersecurity concepts
* Create an expo-ready and resume-quality project

---

# 🛡️ Core Security Technologies Used

| Technology         | Purpose                      |
| ------------------ | ---------------------------- |
| AES-256 Encryption | Encrypting votes securely    |
| RSA Encryption     | Encrypting AES keys securely |
| SHA-256 Hashing    | Vote integrity verification  |
| Password Hashing   | Secure authentication        |
| Flask Sessions     | Session management           |
| SQLite             | Database storage             |

---

# ⚙️ Features Implemented

---

# ✅ PHASE 1 — Real Authentication System

### Implemented Features

* ✅ Voter Login
* ✅ Admin Login
* ✅ One Vote Per User
* ✅ Session Management
* ✅ Logout System
* ✅ Password Hashing
* ✅ Input Validation
* ✅ Secure Authentication Workflow

### Security Benefits

* Prevents multiple voting
* Protects user credentials
* Maintains authenticated sessions
* Restricts admin access securely

---

# ✅ PHASE 2 — Professional Dashboard

### Admin Dashboard Features

* ✅ Total Registered Voters
* ✅ Total Votes Cast
* ✅ Live Election Statistics
* ✅ Candidate Rankings
* ✅ Animated Statistics Cards
* ✅ Pie Chart Analytics
* ✅ Bar Graph Visualization
* ✅ Responsive Dashboard UI

### Visualization Libraries Used

* **Chart.js**

### Benefits

* Real-time election monitoring
* Professional analytics interface
* Clear visualization of election data

---

# ✅ PHASE 3 — Cybersecurity Effects

### Implemented Features

* ✅ Matrix Background Animation
* ✅ Secure Transmission Animation
* ✅ Terminal-Style Security Effects
* ✅ Tampering Alert Effects
* ✅ Cybersecurity-Themed UI


# ✅ PHASE 4 — Advanced Security Features

### Implemented Features

* ✅ Download Encrypted Receipt
* ✅ Vote Verification System

### Downloadable Receipt Includes

* Encrypted Vote
* SHA-256 Integrity Hash
* Timestamp
* Security Status

### Verification System

Users can verify:

* whether vote data was modified
* whether integrity remains intact

If any data is altered:

* the system detects tampering immediately

---

# 🧠 Working Architecture

## Voting Process Flow

1. User logs into system
2. Vote is selected
3. AES key is generated
4. Vote is encrypted using AES
5. AES key is encrypted using RSA
6. SHA-256 hash is generated
7. Encrypted vote stored in database
8. Receipt generated for verification

---

# 🔐 Security Workflow

## Authentication

* Passwords are hashed before storage
* Sessions manage authenticated users
* Admin and voter roles are separated

## Encryption

* Votes encrypted using AES-256
* AES keys protected using RSA encryption

## Integrity Verification

* SHA-256 hashes detect tampering
* Verification module confirms authenticity

---

# 📊 Dashboard Analytics

The admin dashboard provides:

* live election monitoring
* vote statistics
* candidate rankings
* vote distribution charts
* participation percentage

Charts included:

* Pie Chart
* Bar Graph

---

# 💻 Technologies Used

## Frontend

* HTML5
* CSS3
* JavaScript

## Backend

* Python
* Flask

## Database

* SQLite

## Security Libraries

* Cryptography
* Werkzeug Security

## Visualization

* Chart.js

---

# 📁 Project Structure

```text
Secure-Online-Voting-System/
│
├── app.py
├── database.db
├── keys/
│   ├── admin_private.pem
│   └── admin_public.pem
│
├── crypto/
│   ├── aes_utils.py
│   ├── rsa_utils.py
│   └── hash_utils.py
│
├── database/
│   └── db_setup.py
│
├── templates/
│   ├── login.html
│   ├── vote.html
│   ├── dashboard.html
│   ├── results.html
│   └── verify.html
│
├── static/
│   └── style.css
│
└── README.md
```

---

# ▶️ How To Run The Project

## Step 1 — Clone Repository

```bash
git clone <your-repository-link>
```

---

## Step 2 — Install Dependencies

```bash
pip install flask cryptography werkzeug
```

---

## Step 3 — Create Database

```bash
python database/db_setup.py
```

---

## Step 4 — Run Application

```bash
python app.py
```

---

## Step 5 — Open Browser

```text
http://127.0.0.1:5000
```

---

# 👤 Default Login Workflow

## Admin Login

Create admin account using:

```text
Username: admin
Password: Admin@123
```

The system automatically assigns:

```text
role = admin
```

---

## Voter Login Example

```text
Username: Avi
Password: Avi@1234
```

---

# 📸 Major Screens Included

* Secure Login Page
* Voting Interface
* Encryption Animation
* Admin Dashboard
* Pie & Bar Charts
* Security Monitor
* Receipt Verification Page

---

# 🔥 Major Highlights

* Real encryption implementation
* Secure authentication workflow
* Modern cybersecurity UI
* Tampering detection
* Resume-quality architecture
* Expo-ready presentation project

---

# 📌 Future Enhancements

Possible future improvements:

* Email OTP verification
* Biometric authentication
* Blockchain integration
* Cloud database deployment
* Multi-election support
* Real-time live voting updates

---

# 📚 Learning Outcomes

This project demonstrates practical implementation of:

* Cryptography
* Authentication systems
* Secure session management
* Hash verification
* Role-based access control
* Secure software design
* Cybersecurity visualization

---

# 👩‍💻 Developed By

**Karishma**
B.Tech Computer Science Engineering Student


