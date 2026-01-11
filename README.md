# Serverless Invoice Manager 🧾

> **Automated Invoice Processing Pipeline powered by Groq AI (Llama 3).**

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![Groq](https://img.shields.io/badge/AI-Groq%20Llama%203-f55036?style=flat)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat&logo=fastapi&logoColor=white)
![Status](https://img.shields.io/badge/Status-Deployment%20Ready-success)

A high-performance, serverless-ready application that automates financial document organization. It leverages **Groq AI (Llama 3 70B)** for near-instant data extraction and **Google Drive API** for intelligent cloud storage.

---

## ✨ Key Features

*   **⚡ Ultra-Fast AI Extraction**: Uses **Groq (Llama 3)** to extract Vendor, Date, and Amount in milliseconds.
*   **📂 Automated Cloud Sync**: Auto-sorts files into a `Year/Month/Day` nested folder structure in Google Drive.
*   **🏷️ Smart Renaming**: Standardizes filenames to `YYYY_MM_DD_Vendor_Amount.pdf` for effortless searchability.
*   **📷 Hybrid OCR**: Combines **PyMuPDF** and **Tesseract 5** for 100% coverage.
*   **🛡️ Robust Error Handling**: Graceful handling of API rate limits and invalid file types.
*   **☁️ Deployment Ready**: Container-friendly architecture.

---

## 🛠️ Tech Stack

*   **Backend**: Python (FastAPI, Uvicorn)
*   **AI Engine**: [Groq API](https://groq.com) (Llama 3 70B Versatile)
*   **OCR Engine**: Tesseract OCR & PyMuPDF
*   **Storage**: Google Drive API v3
*   **Frontend**: Vanilla HTML5/CSS3/JS

---

## 🚀 Quick Start

### 1. Requirements
*   Python 3.10+
*   [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) installed.

### 2. Setup
```bash
git clone https://github.com/YOUR_USERNAME/invoice-project.git
cd invoice-project
python -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
```

### 3. Environment Variables
Create a `.env` file in `backend/`:
```env
GROQ_API_KEY=gsk_...
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```


### 4. Run
```bash
python -m uvicorn backend.main:app --reload
```
Visit `http://localhost:8000` to start processing invoices.

---

## 📄 License
MIT License. Free for educational and personal use.
