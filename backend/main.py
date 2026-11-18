import os
import io
import urllib.parse
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse, FileResponse

from storage import StudentStorage
from exporter import generate_student_pdf, generate_student_excel, generate_search_results_excel

# Locate the nominal_roll directory relative to project root or current directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

CANDIDATE_PATHS = [
    os.path.join(PROJECT_ROOT, "nominal_roll"),
    os.path.join(CURRENT_DIR, "nominal_roll"),
    os.path.abspath("nominal_roll")
]

NOMINAL_ROLL_DIR = None
for p in CANDIDATE_PATHS:
    if os.path.exists(p) and os.path.isdir(p):
        NOMINAL_ROLL_DIR = p
        break

if not NOMINAL_ROLL_DIR:
    NOMINAL_ROLL_DIR = os.path.join(PROJECT_ROOT, "nominal_roll")

storage = StudentStorage(NOMINAL_ROLL_DIR)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Scan on startup
    storage.scan_and_index()
    yield

app = FastAPI(
    title="Student Nominal Roll Search Portal API",
    description="Automated Nominal Roll Extraction, Search and Verification System",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "nominal-roll-backend",
        "nominal_dir": storage.nominal_dir,
        "indexed_records": len(storage.records)
    }

@app.get("/api/stats")
def get_portal_stats():
    stats = storage.get_stats()
    return stats

@app.post("/api/scan")
def trigger_rescan(background_tasks: BackgroundTasks):
    if storage.is_scanning:
        return {"status": "scanning", "message": "Scan is already in progress."}
    
    background_tasks.add_task(storage.scan_and_index)
    return {"status": "started", "message": "Nominal roll rescanning initiated in background."}

@app.get("/api/suggest")
def get_suggestions(q: str = Query("", description="Query for student name autocomplete")):
    if not q or len(q.strip()) < 1:
        return []
    return storage.suggest(query=q, limit=10)

@app.get("/api/search")
def search_students(
    q: str = Query("", description="Search student by name, admission no, or details"),
    course: str = Query("", description="Filter by course/department"),
    file: str = Query("", description="Filter by nominal roll source file")
):
    results = storage.search(query=q, course_filter=course, file_filter=file)
    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }

@app.get("/api/students/{student_id}")
def get_student_details(student_id: str):
    student = storage.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found.")
    return student

@app.get("/api/photos/{filename}")
def get_student_photo(filename: str):
    safe_filename = os.path.basename(filename)
    photos_dir = storage.extractor.photos_dir
    file_path = os.path.join(photos_dir, safe_filename)
    if not os.path.exists(file_path):
        if not safe_filename.endswith(".jpg"):
            alt_path = os.path.join(photos_dir, f"{safe_filename}.jpg")
            if os.path.exists(alt_path):
                file_path = alt_path
            else:
                raise HTTPException(status_code=404, detail="Student photograph not found.")
        else:
            raise HTTPException(status_code=404, detail="Student photograph not found.")

    return FileResponse(file_path, media_type="image/jpeg", headers={"Cache-Control": "public, max-age=86400"})

@app.get("/api/export/pdf/{student_id}")
def export_student_pdf(student_id: str):
    student = storage.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found.")
    
    pdf_buffer = generate_student_pdf(student)
    safe_name = "".join(c for c in student.get("student_name", "Student") if c.isalnum() or c in (' ', '_', '-')).strip()
    safe_name = safe_name.replace(" ", "_")
    filename = f"{safe_name}_Nominal_Profile.pdf"
    
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

@app.get("/api/export/excel/{student_id}")
def export_student_excel(student_id: str):
    student = storage.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found.")
    
    excel_buffer = generate_student_excel(student)
    safe_name = "".join(c for c in student.get("student_name", "Student") if c.isalnum() or c in (' ', '_', '-')).strip()
    safe_name = safe_name.replace(" ", "_")
    filename = f"{safe_name}_Nominal_Record.xlsx"
    
    return Response(
        content=excel_buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

@app.get("/api/export/search-excel")
def export_search_results_excel(
    q: str = Query("", description="Search term"),
    course: str = Query("", description="Course filter"),
    file: str = Query("", description="File filter")
):
    results = storage.search(query=q, course_filter=course, file_filter=file)
    if not results:
        raise HTTPException(status_code=404, detail="No matching records to export.")
    
    excel_buffer = generate_search_results_excel(results)
    filename = "Nominal_Roll_Search_Results.xlsx"
    
    return Response(
        content=excel_buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
