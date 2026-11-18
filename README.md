# STUDENT NOMINAL ROLL SEARCH PORTAL
> **Search, Retrieve and Access Student Records Instantly.**

An institutional-grade, modern, and responsive web application built with **React (TypeScript) + Tailwind CSS** and **Python FastAPI**. It automatically scans, indexes, extracts, and searches student nominal roll records across diverse document formats (`.pdf`, `.docx`, `.xlsx`, `.xls`, `.csv`, `.txt`), with OCR fallback for scanned materials, typeahead search suggestions, verification dashboards, and official PDF/Excel export capabilities.

---

## 🏛️ Key Features

1. **Automatic Multi-Format Document Scanning**:
   - Automatically detects and reads all nominal roll documents located in `nominal_roll/`.
   - Supports **PDF** (multi-page tabular extraction + OCR fallback), **DOCX**, **Excel (.xlsx, .xls)**, **CSV**, and **TXT**.
   - Preserves original documents without altering or deleting any files.
   - Provides granular status and error reporting for every processed file.

2. **Intelligent & Resilient Search**:
   - **Full & Partial Name Search**: Substring and token-based name matching.
   - **Case-Insensitive**: Search regardless of casing.
   - **Typeahead Suggestions**: Real-time autocomplete dropdown while typing.
   - **Admission / Register / Roll Number Search**: Instant lookup by ID numbers.
   - **Multi-Record Handling**: Displays all matching student records rather than picking one arbitrarily.

3. **Dynamic Field Extraction (Zero Fabrication)**:
   - Accurately captures only fields that actually exist in the source file:
     - Student Name, Admission No, Register No, Roll / Sl No
     - Class / Course, Stream, School / Institution
     - Date of Birth, Gender
     - Father's Name, Mother's Name, Guardian's Name
     - Caste, Community, Religion
     - Orthopedically Handicapped (OH), Blindness, Deafness, Mental Retardation flags
     - Second Language, Academic Specialization, Admission Status, etc.
   - Does **not** fabricate missing fields.

4. **Institutional Dashboard Interface**:
   - Professional Navy Blue (`#1e3a8a`, `#0f172a`) and White aesthetic.
   - Student name header with verification badges.
   - Highlight of matching characters across search results and profile view.
   - Archival provenance card citing the exact source file and page/sheet location.
   - Related records section for cross-document student identification.

5. **Export & Print Capabilities**:
   - **Download PDF**: Generates an official, beautifully styled Verification Profile PDF.
   - **Export Excel**: Generates clean `.xlsx` spreadsheets for single students or bulk search results.
   - **Print Profile**: Clean, formatted print layout (`Ctrl+P` or via the "Print Profile" button).

6. **Session History & File Tracking**:
   - Recent search query chips saved during the active browser session.
   - Real-time directory statistics (Total Files, OK/Failed counts, Total Student Records).
   - "Nominal Roll Document Archives" modal displaying the exact parsing outcome of each file.

---

## 📁 Project Architecture

```
billyb/
├── backend/
│   ├── main.py              # FastAPI application & REST endpoints
│   ├── extractor.py         # Multi-format document parser (PDF, DOCX, XLSX, CSV, TXT, OCR)
│   ├── storage.py           # In-memory indexing, search engine & autocomplete
│   ├── exporter.py          # PDF generation (ReportLab) & Excel exporter (pandas/openpyxl)
│   └── requirements.txt     # Backend Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx             # Navbar with institutional branding & metrics
│   │   │   ├── SearchBar.tsx          # Autocomplete search bar, filters & clear/reset
│   │   │   ├── SearchResults.tsx      # Matching student cards with highlight
│   │   │   ├── StudentProfileView.tsx # Complete extracted student profile dashboard
│   │   │   ├── SearchHistory.tsx      # Recent search history chips
│   │   │   └── FilesStatusModal.tsx   # Scanned files status & error inspection modal
│   │   ├── App.tsx                    # Main portal state orchestration
│   │   ├── types.ts                   # TypeScript interfaces
│   │   └── index.css                  # Tailwind CSS styling & print formatting
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── nominal_roll/                      # Folder containing student nominal roll documents
│   ├── 2026 Nominal list-Business Studies, Accountancy, Economics,Computer Applications 39.pdf
│   ├── 2026 Nominal list-Business Studies, Accountancy, Economics,Political Science 38.pdf
│   ├── 2026 Nominal list-Economics, Gandhian Studies, Communicative English, Computer Applications 33.pdf
│   ├── 2026 Nominal list-Physics, Chemistry, Biology,Mathematics (1).pdf
│   ├── 2026 Nominal list-Physics, Chemistry, Mathematics, Computer Science 05.pdf
│   ├── nominal_roll_vocational_records.xlsx
│   └── nominal_roll_arts_humanities.csv
├── run_app.bat                        # One-click Windows launcher for both frontend & backend
├── start_backend.bat                  # Starts FastAPI backend server on port 8000
├── start_frontend.bat                 # Starts Vite frontend server on port 5173
└── README.md
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: 3.10+
- **Node.js**: 18+ (npm included)

### Option 1: Automatic Launch (Windows)
Double-click `run_app.bat` or run in terminal:
```cmd
run_app.bat
```
This automatically starts both the FastAPI backend and Vite frontend and opens the terminal windows.

---

### Option 2: Manual Step-by-Step Launch

#### 1. Start the Backend
Open a terminal in the project root:
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
The backend will automatically locate `../nominal_roll`, scan and index all documents on startup, and serve APIs at `http://127.0.0.1:8000`.

#### 2. Start the Frontend
Open a second terminal in the project root:
```bash
cd frontend
npm install
npm run dev
```
Open your browser and navigate to:
```
http://localhost:5173
```

---

## 🔍 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status and indexed record count |
| `GET` | `/api/stats` | Aggregated statistics, course counts, and list of all processed files |
| `POST` | `/api/scan` | Triggers a fresh background rescan of the `nominal_roll` directory |
| `GET` | `/api/suggest?q={term}` | Returns autocomplete suggestions while typing in search bar |
| `GET` | `/api/search?q={query}&course={course}&file={file}` | Searches student records with optional course and file filtering |
| `GET` | `/api/students/{id}` | Retrieves complete extracted profile and related records for a student |
| `GET` | `/api/export/pdf/{id}` | Generates and downloads the official student profile as PDF |
| `GET` | `/api/export/excel/{id}` | Generates and downloads the student profile as an Excel (`.xlsx`) sheet |
| `GET` | `/api/export/search-excel?q=...` | Exports all current matching search results to an Excel spreadsheet |
