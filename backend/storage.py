import time
import logging
from typing import List, Dict, Any, Optional
from extractor import StudentRecord, FileProcessResult, DocumentExtractor

logger = logging.getLogger("storage")

class StudentStorage:
    def __init__(self, nominal_dir: str):
        self.nominal_dir = nominal_dir
        self.extractor = DocumentExtractor(nominal_dir)
        self.records: List[StudentRecord] = []
        self.records_by_id: Dict[str, StudentRecord] = {}
        self.file_results: List[FileProcessResult] = []
        self.last_scan_time: Optional[float] = None
        self.is_scanning: bool = False

    def scan_and_index(self):
        self.is_scanning = True
        start = time.time()
        logger.info(f"Starting nominal roll scan in {self.nominal_dir}...")
        try:
            records, file_results = self.extractor.scan_all_files()
            self.records = records
            self.records_by_id = {r.id: r for r in records}
            self.file_results = file_results
            self.last_scan_time = time.time()
            elapsed = self.last_scan_time - start
            logger.info(f"Scan completed in {elapsed:.2f}s: {len(self.records)} records from {len(self.file_results)} files.")
        except Exception as e:
            logger.exception(f"Error during scan: {e}")
        finally:
            self.is_scanning = False

    def get_stats(self) -> Dict[str, Any]:
        successful_files = [f for f in self.file_results if f.status == "success"]
        error_files = [f for f in self.file_results if f.status == "error"]

        courses = set(r.class_course for r in self.records if r.class_course)
        schools = set(r.school_name for r in self.records if r.school_name)

        return {
            "total_files": len(self.file_results),
            "successful_files": len(successful_files),
            "failed_files": len(error_files),
            "total_records": len(self.records),
            "courses_count": len(courses),
            "schools_count": len(schools),
            "last_scanned_at": self.last_scan_time,
            "is_scanning": self.is_scanning,
            "files": [
                {
                    "filename": f.filename,
                    "file_type": f.file_type,
                    "status": f.status,
                    "records_count": f.records_count,
                    "pages_or_sheets": f.pages_or_sheets,
                    "error_message": f.error_message
                }
                for f in self.file_results
            ]
        }

    def suggest(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        q = query.strip().lower()
        if not q or len(q) < 1:
            return []

        suggestions: List[Dict[str, Any]] = []
        seen_names = set()

        # Score matching records
        scored_matches = []
        for r in self.records:
            name_lower = r.student_name.lower()
            score = 0
            if name_lower == q:
                score = 100
            elif name_lower.startswith(q):
                score = 80
            elif any(part.startswith(q) for part in name_lower.split()):
                score = 60
            elif q in name_lower:
                score = 40
            elif q in r.admission_no.lower() or q in r.register_no.lower():
                score = 50

            if score > 0:
                scored_matches.append((score, r))

        scored_matches.sort(key=lambda x: (x[0], x[1].student_name), reverse=True)

        for score, r in scored_matches:
            dedup_key = f"{r.student_name.lower()}_{r.admission_no}_{r.source_file}"
            if dedup_key in seen_names:
                continue
            seen_names.add(dedup_key)
            suggestions.append({
                "id": r.id,
                "student_name": r.student_name,
                "admission_no": r.admission_no,
                "register_no": r.register_no,
                "course": r.class_course,
                "source_file": r.source_file,
                "match_score": score,
                "photo_url": r.photo_url,
                "has_photo": r.has_photo,
                "photo_status": r.photo_status
            })
            if len(suggestions) >= limit:
                break

        return suggestions

    def search(self, query: str, course_filter: str = "", file_filter: str = "") -> List[Dict[str, Any]]:
        q = query.strip().lower()
        if not q and not course_filter and not file_filter:
            # If no query provided, return first 50 records as default list
            return [r.to_dict() for r in self.records[:50]]

        results = []
        for r in self.records:
            if course_filter and course_filter.lower() not in r.class_course.lower():
                continue
            if file_filter and file_filter.lower() not in r.source_file.lower():
                continue

            if not q:
                results.append((10, r))
                continue

            name_lower = r.student_name.lower()
            admn_lower = r.admission_no.lower()
            reg_lower = r.register_no.lower()
            father_lower = r.father_name.lower()

            score = 0
            # Exact match
            if name_lower == q:
                score = 100
            elif name_lower.startswith(q):
                score = 85
            elif any(word.startswith(q) for word in name_lower.split()):
                score = 75
            elif q in name_lower:
                score = 60
            elif q in admn_lower or q in reg_lower:
                score = 70
            elif q in father_lower:
                score = 50
            else:
                # Check any other field
                for f_val in r.all_fields.values():
                    if q in str(f_val).lower():
                        score = 30
                        break

            if score > 0:
                results.append((score, r))

        results.sort(key=lambda x: (x[0], x[1].student_name), reverse=True)
        return [r.to_dict() for _, r in results]

    def get_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        record = self.records_by_id.get(record_id)
        if not record:
            return None

        data = record.to_dict()
        # Find related records (e.g. students with same/similar name in other files or same class)
        related = []
        for r in self.records:
            if r.id == record.id:
                continue
            # Same student name in another document or batch
            if r.student_name.lower() == record.student_name.lower():
                related.append({
                    "id": r.id,
                    "student_name": r.student_name,
                    "admission_no": r.admission_no,
                    "course": r.class_course,
                    "source_file": r.source_file,
                    "photo_url": r.photo_url,
                    "has_photo": r.has_photo,
                    "relation_reason": "Same Student Name in Another Record/File"
                })
            elif (record.admission_no and r.admission_no == record.admission_no) or (record.register_no and r.register_no == record.register_no):
                related.append({
                    "id": r.id,
                    "student_name": r.student_name,
                    "admission_no": r.admission_no,
                    "course": r.class_course,
                    "source_file": r.source_file,
                    "photo_url": r.photo_url,
                    "has_photo": r.has_photo,
                    "relation_reason": "Matching Register/Admission Number"
                })

        data["related_records"] = related[:10]
        return data
