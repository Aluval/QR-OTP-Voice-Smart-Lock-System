# QR-OTP-Voice-Smart-Lock-System 🔐

A **Multi-Factor Authentication Smart Lock System** that integrates **QR Code Scanning, Email OTP Verification, and AI-Based Voice Authentication** to provide a secure and contactless access control solution.

This project is developed for **educational and research purposes** and demonstrates how modern authentication methods can be combined to enhance physical security systems.

---

## 👨‍💻 Author

**Aluvala Ediga Harsha Vardhan Goud**  
MCA Student [MINI PROJECT]  
RGM College of Engineering and Technology, Nandyal

---

## 📌 Project Overview

Traditional lock systems relying on keys, RFID cards, or fingerprints have several security limitations such as duplication, spoofing, and hardware dependency.

This project introduces a **multi-layer authentication mechanism** using:

- QR Code Verification
- Email-based One Time Password (OTP)
- AI Voice Recognition using Resemblyzer

The system ensures that **only authorized users can unlock the system** after successfully completing all authentication steps.

---

## 🚀 Features

- QR Code scanning using **OpenCV**
- Email OTP verification for identity confirmation
- Voice authentication using **Resemblyzer embeddings**
- Multi-factor authentication security
- Real-time authentication validation
- Access logs for monitoring
- Contactless and secure authentication workflow

---

## 🛠️ Technologies Used

- **Python**
- **OpenCV**
- **SpeechRecognition**
- **Resemblyzer**
- **Firebase Firestore**
- **SMTP (Email OTP Service)**

---

## ⚙️ Authentication Workflow

1. User registers with **Name, Email, and ID**
2. System generates a **unique QR code**
3. A **voice sample is recorded and stored as embeddings**
4. During authentication:
   - OTP is sent to the registered email
   - User scans the QR code
   - User provides a live voice sample
5. System verifies:
   - OTP validity
   - QR code match
   - Voice similarity score
6. If all checks pass → **Access Granted**

---

## 📂 Project Structure
```
QR-OTP-Voice-Smart-Lock-System
│
├── main.py
├── qr_scanner.py
├── otp_module.py
├── voice_auth.py
├── firebase_config.py
├── requirements.txt
└── README.md
```

---

## ⚠️ Usage Notice

This project is **primarily intended for educational and research purposes**.

You are allowed to:

- Study the code
- Modify the project
- Use it for learning or academic projects

However, you **must give proper credit to the original author**.

---

## 📢 Attribution Requirement

If you use this project or its code in:

- another project
- a commercial system
- academic submission
- or any public repository

You **must clearly mention the original author**:

> **Project originally developed by Aluvala Ediga Harsha Vardhan Goud**

Failure to provide attribution while using this code may be considered **misrepresentation of authorship**.

---

## 🚨 Misuse Warning

If this project or its code is:

- copied and redistributed without attribution
- falsely claimed as another person's work
- used commercially while misleading users about authorship
- sold without proper credit

The author reserves the right to take **serious action including reporting copyright violations**.

---

## 📜 License

This project is licensed under the **Apache License 2.0**.

See the LICENSE file for more details.

---

## ⭐ Support

If you found this project helpful:

- ⭐ Star the repository
- 🍴 Fork the project
- 🛠️ Contribute improvements

---

## 📬 Contact

**Author:**  
Aluvala Ediga Harsha Vardhan Goud

For academic collaboration or queries, feel free to reach out.

---
