# John-the-Ripper-Cyber-Security-

A web-based **password auditing tool** using **John the Ripper**.  
This project allows users to upload a file containing password hashes and see the cracked passwords directly in the browser. It combines a **Flask backend** to run John the Ripper with a **modern frontend** for an interactive experience.

---

## About John the Ripper

**John the Ripper (JtR)** is a free, open-source **password cracking tool** widely used in cybersecurity.  
It is designed to detect weak passwords and audit password security.  

### Key points:

- Works with multiple hash types (MD5, SHA1, bcrypt, DES, etc.).
- Can perform **dictionary attacks**, **brute-force attacks**, and **hybrid attacks**.
- Commonly used in **penetration testing**, **security audits**, and **ethical hacking**.

---

## Project Features

In this project, we included the following features:

1. **File Upload**: Upload a hash file (`hashes.txt`) directly from the browser.  
2. **Password Cracking**: Uses John the Ripper to crack passwords on the server-side.  
3. **Result Display**: Cracked passwords are displayed in a **table format** showing User/Hash → Password.  
4. **Error Handling**: Shows clear messages if no passwords are cracked or if there is a server error.  
5. **Interactive Frontend**: Styled using CSS with a clean card layout, gradient background, and responsive design.  

---

## Project Structure
john-project/
│
├─ backend/
│ ├─ app.py # Flask backend for file upload & John execution
│ ├─ uploads/ # Folder to store uploaded hash files
│ └─ venv/ # Python virtual environment
│
├─ frontend/
│ └─ index.html # Frontend interface
│
├─ README.md
└─ hashes.txt # Sample hash file for testing


---

## Prerequisites

- **Python 3.10+**
- **Flask** and **Flask-CORS**
- **John the Ripper** installed (Windows/Linux/Mac)

---

## Setup Instructions

1. **Clone the repository**:

```bash
git clone <your-repo-url>
cd john-project/backend

