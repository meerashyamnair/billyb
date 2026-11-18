import os
import re
import uuid
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger("extractor")
logging.basicConfig(level=logging.INFO)

# Optional OCR import
try:
    import pytesseract
    from PIL import Image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

import pdfplumber
import pandas as pd
try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

HEADER_CLEANUP_RULES = [
    (r'(?i)^\s*(cand(\.|idate)?\s*name|student\s*name|name\s*of\s*(the\s*)?student|name)\s*$', 'Student Name'),
    (r'(?i)^\s*(father(\'s)?\s*name|father)\s*$', 'Father Name'),
    (r'(?i)^\s*(mother(\'s)?\s*name|mother)\s*$', 'Mother Name'),
    (r'(?i)^\s*(guardian(\'s)?\s*name|guardian)\s*$', 'Guardian Name'),
    (r'(?i)^\s*(admn?|admission)\s*\.?\s*(no|number)(\.|\b)?\s*$', 'Admission No'),
    (r'(?i)^\s*(appln?|application)\s*\.?\s*(no|number)(\.|\b)?\s*$', 'Application No'),
    (r'(?i)^\s*(reg(\.|ister|istration)?)\s*\.?\s*(no|number)(\.|\b)?\s*$', 'Register No'),
    (r'(?i)^\s*(sl|serial)\s*\.?\s*(no|number)(\.|\b)?\s*$', 'Sl No'),
    (r'(?i)^\s*roll\s*no(\.|\b)\s*$', 'Roll No'),
    (r'(?i)^\s*(dob|date\s*of\s*birth)\s*$', 'Date of Birth'),
    (r'(?i)^\s*(gender|sex)\s*$', 'Gender'),
    (r'(?i)^\s*caste\s*$', 'Caste'),
    (r'(?i)^\s*(comm\s*unity|community)\s*$', 'Community'),
    (r'(?i)^\s*(religi\s*on|religion)\s*$', 'Religion'),
    (r'(?i)^\s*(sec\.?\s*lan|second\s*language)\s*$', 'Second Language'),
    (r'(?i)^\s*(acc\.?\s*spec|academic\s*specialization)\s*$', 'Academic Specialization'),
    (r'(?i)^\s*status\s*$', 'Status'),
    (r'(?i)^\s*scheme\s*$', 'Scheme'),
    (r'(?i)^\s*oh\s*$', 'Orthopedically Handicapped (OH)'),
    (r'(?i)^\s*(bli\s*nd|blind)\s*$', 'Blindness (Blind)'),
    (r'(?i)^\s*(de\s*af|deaf)\s*$', 'Deafness (Deaf)'),
    (r'(?i)^\s*mr\s*$', 'Mental Retardation (MR)'),
    (r'(?i)^\s*(address|permanent\s*address)\s*$', 'Address'),
    (r'(?i)^\s*(phone(\s*no)?|mobile(\s*no)?|contact(\s*no)?)\s*$', 'Phone Number'),
    (r'(?i)^\s*(course|class|class\s*\/\s*course)\s*$', 'Course'),
    (r'(?i)^\s*(department|dept)\s*$', 'Department'),
]

def clean_text(val: Any) -> str:
    if val is None:
        return ""
    s = str(val).strip()
    s = re.sub(r'[\r\n\t]+', ' ', s)
    s = re.sub(r'\s{2,}', ' ', s)
    return s.strip()

def normalize_header(raw_header: str) -> str:
    cleaned = clean_text(raw_header)
    for pattern, normalized in HEADER_CLEANUP_RULES:
        if re.search(pattern, cleaned):
            return normalized
    return cleaned

@dataclass
class StudentRecord:
    id: str
    student_name: str
    admission_no: str = ""
    register_no: str = ""
    roll_no: str = ""
    class_course: str = ""
    department: str = ""
    school_name: str = ""
    dob: str = ""
    gender: str = ""
    father_name: str = ""
    mother_name: str = ""
    guardian_name: str = ""
    category: str = ""
    caste: str = ""
    religion: str = ""
    address: str = ""
    phone: str = ""
    source_file: str = ""
    source_path: str = ""
    page_or_sheet: str = ""
    row_index: int = 0
    all_fields: Dict[str, str] = field(default_factory=dict)
    photo_url: str = ""
    has_photo: bool = False
    photo_path: str = ""
    photo_status: str = "none"  # "matched" | "unverified" | "none"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class FileProcessResult:
    filename: str
    filepath: str
    file_type: str
    status: str  # 'success' or 'error'
    records_count: int = 0
    pages_or_sheets: int = 0
    error_message: Optional[str] = None

class DocumentExtractor:
    def __init__(self, base_nominal_dir: str, photos_dir: Optional[str] = None):
        self.nominal_dir = os.path.abspath(base_nominal_dir)
        if photos_dir:
            self.photos_dir = os.path.abspath(photos_dir)
        else:
            self.photos_dir = os.path.abspath(os.path.join(os.path.dirname(self.nominal_dir), "student_photos"))
        os.makedirs(self.photos_dir, exist_ok=True)

    def scan_all_files(self) -> Tuple[List[StudentRecord], List[FileProcessResult]]:
        if not os.path.exists(self.nominal_dir):
            logger.warning(f"Nominal roll folder not found at {self.nominal_dir}")
            return [], [FileProcessResult(
                filename="nominal_roll",
                filepath=self.nominal_dir,
                file_type="folder",
                status="error",
                error_message=f"Directory '{self.nominal_dir}' does not exist."
            )]

        all_records: List[StudentRecord] = []
        file_results: List[FileProcessResult] = []

        files = sorted(os.listdir(self.nominal_dir))
        for filename in files:
            full_path = os.path.join(self.nominal_dir, filename)
            if not os.path.isfile(full_path):
                continue
            
            # Skip hidden files or temporary lock files
            if filename.startswith('~') or filename.startswith('.'):
                continue

            ext = os.path.splitext(filename)[1].lower()
            try:
                records, result = self.process_file(full_path, filename, ext)
                all_records.extend(records)
                file_results.append(result)
            except Exception as e:
                logger.exception(f"Unhandled error processing {filename}: {e}")
                file_results.append(FileProcessResult(
                    filename=filename,
                    filepath=full_path,
                    file_type=ext.lstrip('.'),
                    status="error",
                    records_count=0,
                    error_message=f"Processing failed: {str(e)}"
                ))

        return all_records, file_results

    def process_file(self, full_path: str, filename: str, ext: str) -> Tuple[List[StudentRecord], FileProcessResult]:
        if ext == '.pdf':
            return self.extract_pdf(full_path, filename)
        elif ext in ['.xlsx', '.xls']:
            return self.extract_excel(full_path, filename, ext)
        elif ext == '.docx':
            return self.extract_docx(full_path, filename)
        elif ext == '.csv':
            return self.extract_csv(full_path, filename)
        elif ext == '.txt':
            return self.extract_txt(full_path, filename)
        else:
            return [], FileProcessResult(
                filename=filename,
                filepath=full_path,
                file_type=ext.lstrip('.'),
                status="error",
                records_count=0,
                error_message=f"Unsupported file format '{ext}'. Supported: PDF, DOCX, XLSX, XLS, CSV, TXT."
            )

    def extract_pdf(self, full_path: str, filename: str) -> Tuple[List[StudentRecord], FileProcessResult]:
        records: List[StudentRecord] = []
        total_pages = 0

        try:
            with pdfplumber.open(full_path) as pdf:
                total_pages = len(pdf.pages)
                active_header: Optional[List[str]] = None
                global_school = ""
                global_course = ""

                for p_idx, page in enumerate(pdf.pages):
                    page_num = p_idx + 1
                    page_label = f"Page {page_num}"
                    text = page.extract_text() or ""

                    # Check for OCR fallback if page has minimal or no text
                    if len(text.strip()) < 30 and HAS_OCR:
                        try:
                            pil_img = page.to_image(resolution=200).original
                            ocr_text = pytesseract.image_to_string(pil_img)
                            if len(ocr_text.strip()) > len(text.strip()):
                                text = ocr_text
                        except Exception as ocr_err:
                            logger.warning(f"OCR fallback failed for {filename} page {page_num}: {ocr_err}")

                    # Extract page-level metadata (School, Course, etc.)
                    lines = [clean_text(l) for l in text.split('\n') if clean_text(l)]
                    page_school = global_school
                    page_course = global_course

                    for line in lines:
                        if 'School Name:' in line:
                            page_school = clean_text(line.split('School Name:')[1])
                            global_school = page_school
                        elif 'Course Name:' in line:
                            page_course = clean_text(line.split('Course Name:')[1])
                            global_course = page_course

                    # Extract and sort embedded student images on this page
                    page_images = sorted(page.images, key=lambda im: (im['top'], im['x0']))
                    # Filter student photo dimensions (width 25-100, height 35-120)
                    candidate_photos = [
                        im for im in page_images
                        if 25 <= im['width'] <= 100 and 35 <= im['height'] <= 120
                    ]

                    # Extract tables from page
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            if not table or len(table) == 0:
                                continue

                            first_row = [clean_text(c) for c in table[0]]
                            # Determine if first row is a header
                            is_header = any(
                                re.search(r'(?i)(cand.*name|student.*name|sl.*no|admn|reg.*no)', c)
                                for c in first_row
                            )

                            if is_header:
                                active_header = [normalize_header(c) for c in first_row]
                                data_rows = table[1:]
                            else:
                                data_rows = table

                            if not active_header:
                                continue

                            # Collect all valid student rows on this page first
                            valid_rows = []
                            for r_idx, row in enumerate(data_rows):
                                cleaned_row = [clean_text(c) for c in row]
                                if not any(cleaned_row):
                                    continue

                                # Map header to values
                                row_dict: Dict[str, str] = {}
                                for h_idx, val in enumerate(cleaned_row):
                                    if h_idx < len(active_header):
                                        h_key = active_header[h_idx]
                                        if h_key and val:
                                            row_dict[h_key] = val

                                # Find student name
                                student_name = self._find_field_value(row_dict, ['Student Name', 'Cand Name', 'Name'])
                                if not student_name or student_name.lower() in ['cand name', 'student name', 'name', 'photo']:
                                    continue
                                valid_rows.append(row_dict)

                            # Match each student row with their corresponding photo
                            for row_i, row_dict in enumerate(valid_rows):
                                photo_bytes = None
                                photo_status = "none"

                                if len(candidate_photos) == len(valid_rows):
                                    # 1:1 exact row match on the page
                                    photo_img = candidate_photos[row_i]
                                    stream = photo_img.get('stream')
                                    if stream:
                                        try:
                                            photo_bytes = stream.get_data()
                                            photo_status = "matched"
                                        except Exception as p_err:
                                            logger.warning(f"Failed to read photo stream: {p_err}")
                                            photo_status = "unverified"
                                elif len(candidate_photos) > 0:
                                    # Positional alignment
                                    if row_i < len(candidate_photos):
                                        photo_img = candidate_photos[row_i]
                                        stream = photo_img.get('stream')
                                        if stream:
                                            try:
                                                photo_bytes = stream.get_data()
                                                photo_status = "unverified"
                                            except Exception:
                                                pass

                                rec = self._create_student_record(
                                    raw_dict=row_dict,
                                    filename=filename,
                                    filepath=full_path,
                                    page_or_sheet=page_label,
                                    row_idx=len(records) + 1,
                                    default_school=page_school,
                                    default_course=page_course,
                                    photo_bytes=photo_bytes,
                                    photo_status=photo_status
                                )
                                records.append(rec)
                    else:
                        # Fallback: line-based parsing if no table lines detected
                        fallback_records = self._parse_lines_fallback(lines, filename, full_path, page_label, page_school, page_course)
                        records.extend(fallback_records)

            return records, FileProcessResult(
                filename=filename,
                filepath=full_path,
                file_type="pdf",
                status="success",
                records_count=len(records),
                pages_or_sheets=total_pages
            )
        except Exception as e:
            return [], FileProcessResult(
                filename=filename,
                filepath=full_path,
                file_type="pdf",
                status="error",
                records_count=0,
                error_message=f"PDF extraction error: {str(e)}"
            )

    def extract_excel(self, full_path: str, filename: str, ext: str) -> Tuple[List[StudentRecord], FileProcessResult]:
        records: List[StudentRecord] = []
        try:
            excel_file = pd.ExcelFile(full_path)
            sheet_names = excel_file.sheet_names
            for sheet_name in sheet_names:
                df = pd.read_excel(full_path, sheet_name=sheet_name)
                # Find header row if not row 0
                df = df.dropna(how='all')
                if df.empty:
                    continue

                # If first row has mostly NaNs or metadata, find the actual header row
                headers = [clean_text(c) for c in df.columns]
                normalized_headers = [normalize_header(h) for h in headers]

                for r_idx, row in df.iterrows():
                    row_dict: Dict[str, str] = {}
                    for col_idx, col_name in enumerate(normalized_headers):
                        val = clean_text(row.iloc[col_idx])
                        if val and val.lower() != 'nan':
                            row_dict[col_name] = val

                    student_name = self._find_field_value(row_dict, ['Student Name', 'Cand Name', 'Name'])
                    if not student_name:
                        continue

                    rec = self._create_student_record(
                        raw_dict=row_dict,
                        filename=filename,
                        filepath=full_path,
                        page_or_sheet=f"Sheet: {sheet_name}",
                        row_idx=len(records) + 1,
                        default_school="",
                        default_course=""
                    )
                    records.append(rec)

            return records, FileProcessResult(
                filename=filename,
                filepath=full_path,
                file_type=ext.lstrip('.'),
                status="success",
                records_count=len(records),
                pages_or_sheets=len(sheet_names)
            )
        except Exception as e:
            return [], FileProcessResult(
                filename=filename,
                filepath=full_path,
                file_type=ext.lstrip('.'),
                status="error",
                records_count=0,
                error_message=f"Excel extraction error: {str(e)}"
            )

    def extract_csv(self, full_path: str, filename: str) -> Tuple[List[StudentRecord], FileProcessResult]:
        records: List[StudentRecord] = []
        try:
            df = pd.read_csv(full_path, dtype=str)
            df = df.dropna(how='all')
            normalized_headers = [normalize_header(clean_text(c)) for c in df.columns]

            for r_idx, row in df.iterrows():
                row_dict: Dict[str, str] = {}
                for col_idx, col_name in enumerate(normalized_headers):
                    val = clean_text(row.iloc[col_idx])
                    if val and val.lower() != 'nan':
                        row_dict[col_name] = val

                student_name = self._find_field_value(row_dict, ['Student Name', 'Cand Name', 'Name'])
                if not student_name:
                    continue

                rec = self._create_student_record(
                    raw_dict=row_dict,
                    filename=filename,
                    filepath=full_path,
                    page_or_sheet="CSV",
                    row_idx=len(records) + 1,
                    default_school="",
                    default_course=""
                )
                records.append(rec)

            return records, FileProcessResult(
                filename=filename,
                filepath=full_path,
                file_type="csv",
                status="success",
                records_count=len(records),
                pages_or_sheets=1
            )
        except Exception as e:
            return [], FileProcessResult(
                filename=filename,
                filepath=full_path,
                file_type="csv",
                status="error",
                records_count=0,
                error_message=f"CSV extraction error: {str(e)}"
            )

    def extract_docx(self, full_path: str, filename: str) -> Tuple[List[StudentRecord], FileProcessResult]:
        if not HAS_DOCX:
            return [], FileProcessResult(
                filename=filename,
                filepath=full_path,
                file_type="docx",
                status="error",
                records_count=0,
                error_message="python-docx library is not installed."
            )
        records: List[StudentRecord] = []
        try:
            doc = docx.Document(full_path)
            for t_idx, table in enumerate(doc.tables):
                if not table.rows:
                    continue
                header = [normalize_header(clean_text(cell.text)) for cell in table.rows[0].cells]
                for r_idx, row in enumerate(table.rows[1:]):
                    row_dict: Dict[str, str] = {}
                    for c_idx, cell in enumerate(row.cells):
                        if c_idx < len(header):
                            col_name = header[c_idx]
                            val = clean_text(cell.text)
                            if val:
                                row_dict[col_name] = val

                    student_name = self._find_field_value(row_dict, ['Student Name', 'Cand Name', 'Name'])
                    if not student_name:
                        continue

                    rec = self._create_student_record(
                        raw_dict=row_dict,
                        filename=filename,
                        filepath=full_path,
                        page_or_sheet=f"Table {t_idx+1}",
                        row_idx=len(records) + 1,
                        default_school="",
                        default_course=""
                    )
                    records.append(rec)

            # If no tables found, check paragraphs for key-value format
            if not records:
                current_dict: Dict[str, str] = {}
                for p in doc.paragraphs:
                    text = clean_text(p.text)
                    if not text:
                        if current_dict:
                            s_name = self._find_field_value(current_dict, ['Student Name', 'Cand Name', 'Name'])
                            if s_name:
                                records.append(self._create_student_record(
                                    raw_dict=current_dict,
                                    filename=filename,
                                    filepath=full_path,
                                    page_or_sheet="Document",
                                    row_idx=len(records)+1
                                ))
                            current_dict = {}
                        continue

                    if ':' in text:
                        parts = text.split(':', 1)
                        k = normalize_header(parts[0])
                        v = clean_text(parts[1])
                        current_dict[k] = v

                if current_dict:
                    s_name = self._find_field_value(current_dict, ['Student Name', 'Cand Name', 'Name'])
                    if s_name:
                        records.append(self._create_student_record(
                            raw_dict=current_dict,
                            filename=filename,
                            filepath=full_path,
                            page_or_sheet="Document",
                            row_idx=len(records)+1
                        ))

            return records, FileProcessResult(
                filename=filename,
                filepath=full_path,
                file_type="docx",
                status="success",
                records_count=len(records),
                pages_or_sheets=len(doc.tables) or 1
            )
        except Exception as e:
            return [], FileProcessResult(
                filename=filename,
                filepath=full_path,
                file_type="docx",
                status="error",
                records_count=0,
                error_message=f"DOCX extraction error: {str(e)}"
            )

    def extract_txt(self, full_path: str, filename: str) -> Tuple[List[StudentRecord], FileProcessResult]:
        records: List[StudentRecord] = []
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            lines = [clean_text(l) for l in content.splitlines() if clean_text(l)]
            # Check if tab or pipe separated
            if lines and ('\t' in lines[0] or '|' in lines[0] or ',' in lines[0]):
                delim = '\t' if '\t' in lines[0] else ('|' if '|' in lines[0] else ',')
                header = [normalize_header(c) for c in lines[0].split(delim)]
                for r_idx, line in enumerate(lines[1:]):
                    parts = [clean_text(c) for c in line.split(delim)]
                    row_dict = {header[i]: parts[i] for i in range(min(len(header), len(parts))) if parts[i]}
                    s_name = self._find_field_value(row_dict, ['Student Name', 'Cand Name', 'Name'])
                    if s_name:
                        records.append(self._create_student_record(
                            raw_dict=row_dict,
                            filename=filename,
                            filepath=full_path,
                            page_or_sheet="Text File",
                            row_idx=len(records)+1
                        ))
            else:
                # Key: value blocks
                current_dict: Dict[str, str] = {}
                for line in lines:
                    if ':' in line:
                        k, v = line.split(':', 1)
                        current_dict[normalize_header(k)] = clean_text(v)
                    elif '---' in line or not line:
                        if current_dict:
                            s_name = self._find_field_value(current_dict, ['Student Name', 'Cand Name', 'Name'])
                            if s_name:
                                records.append(self._create_student_record(
                                    raw_dict=current_dict,
                                    filename=filename,
                                    filepath=full_path,
                                    page_or_sheet="Text File",
                                    row_idx=len(records)+1
                                ))
                            current_dict = {}

                if current_dict:
                    s_name = self._find_field_value(current_dict, ['Student Name', 'Cand Name', 'Name'])
                    if s_name:
                        records.append(self._create_student_record(
                            raw_dict=current_dict,
                            filename=filename,
                            filepath=full_path,
                            page_or_sheet="Text File",
                            row_idx=len(records)+1
                        ))

            return records, FileProcessResult(
                filename=filename,
                filepath=full_path,
                file_type="txt",
                status="success",
                records_count=len(records),
                pages_or_sheets=1
            )
        except Exception as e:
            return [], FileProcessResult(
                filename=filename,
                filepath=full_path,
                file_type="txt",
                status="error",
                records_count=0,
                error_message=f"TXT extraction error: {str(e)}"
            )

    def _parse_lines_fallback(self, lines: List[str], filename: str, filepath: str, page_label: str, school: str, course: str) -> List[StudentRecord]:
        records: List[StudentRecord] = []
        for line in lines:
            # Pattern like: 1 2607111443 9592 SSLC 691701 AJMAL SHAMNAS Male 30-03-2010 ...
            match = re.search(r'^\s*(\d+)\s+(\d{8,12})\s+(\d{3,6})\s+.*?([A-Z\s\.]{3,35})\s+(Male|Female)\s+(\d{2}-\d{2}-\d{4})', line)
            if match:
                sl, appln, admn, name, gender, dob = match.groups()
                clean_name = clean_text(name)
                row_dict = {
                    'Sl No': sl,
                    'Application No': appln,
                    'Admission No': admn,
                    'Student Name': clean_name,
                    'Gender': gender,
                    'Date of Birth': dob
                }
                rec = self._create_student_record(
                    raw_dict=row_dict,
                    filename=filename,
                    filepath=filepath,
                    page_or_sheet=page_label,
                    row_idx=len(records)+1,
                    default_school=school,
                    default_course=course
                )
                records.append(rec)
        return records

    def _find_field_value(self, d: Dict[str, str], candidates: List[str]) -> str:
        # First check exact matches
        for c in candidates:
            if c in d and d[c]:
                return clean_text(d[c])
        # Then check case-insensitive exact matches
        lower_candidates = {c.lower(): c for c in candidates}
        for k, v in d.items():
            if k.lower() in lower_candidates and v:
                return clean_text(v)
        return ""

    def _create_student_record(
        self,
        raw_dict: Dict[str, str],
        filename: str,
        filepath: str,
        page_or_sheet: str,
        row_idx: int,
        default_school: str = "",
        default_course: str = "",
        photo_bytes: Optional[bytes] = None,
        photo_status: str = "none"
    ) -> StudentRecord:
        student_name = self._find_field_value(raw_dict, ['Student Name', 'Cand Name', 'Name'])
        admission_no = self._find_field_value(raw_dict, ['Admission No', 'Admn No', 'Admn. No', 'Admn . No', 'Admission Number'])
        register_no = self._find_field_value(raw_dict, ['Register No', 'Reg No', 'Reg. No', 'Reg No.', 'Registration No'])
        roll_no = self._find_field_value(raw_dict, ['Sl No', 'Sl. No', 'Roll No', 'Roll No.', 'Serial No'])
        dob = self._find_field_value(raw_dict, ['Date of Birth', 'DOB'])
        gender = self._find_field_value(raw_dict, ['Gender', 'Sex'])
        father_name = self._find_field_value(raw_dict, ['Father Name', 'Father\'s Name'])
        mother_name = self._find_field_value(raw_dict, ['Mother Name', 'Mother\'s Name'])
        guardian_name = self._find_field_value(raw_dict, ['Guardian Name'])
        category = self._find_field_value(raw_dict, ['Community', 'Category', 'Social Category'])
        caste = self._find_field_value(raw_dict, ['Caste'])
        religion = self._find_field_value(raw_dict, ['Religion'])
        address = self._find_field_value(raw_dict, ['Address', 'Permanent Address', 'Residential Address'])
        phone = self._find_field_value(raw_dict, ['Phone Number', 'Phone', 'Mobile Number', 'Contact Number'])
        
        class_course = self._find_field_value(raw_dict, ['Course', 'Class', 'Class / Course']) or default_course
        school_name = self._find_field_value(raw_dict, ['School Name', 'Institution', 'College']) or default_school
        department = self._find_field_value(raw_dict, ['Department', 'Dept'])

        # Filter empty values from dynamic all_fields
        all_fields = {k: v for k, v in raw_dict.items() if v and not k.startswith('_')}
        if default_course and 'Course' not in all_fields and 'Course Name' not in all_fields:
            all_fields['Course'] = default_course
        if default_school and 'School Name' not in all_fields and 'Institution' not in all_fields:
            all_fields['School / Institution'] = default_school

        # Generate a deterministic unique ID
        unique_seed = f"{filename}_{page_or_sheet}_{row_idx}_{student_name}_{admission_no}_{register_no}"
        record_id = uuid.uuid5(uuid.NAMESPACE_DNS, unique_seed).hex[:12]

        photo_url = ""
        photo_path = ""
        has_photo = False

        if photo_bytes:
            photo_filename = f"{record_id}.jpg"
            photo_path = os.path.join(self.photos_dir, photo_filename)
            try:
                with open(photo_path, "wb") as pf:
                    pf.write(photo_bytes)
                photo_url = f"/api/photos/{photo_filename}"
                has_photo = True
                all_fields['Photograph Status'] = 'Extracted from Nominal Roll (Verified)'
            except Exception as e:
                logger.warning(f"Could not save student photo for {record_id}: {e}")
                photo_status = "none"

        return StudentRecord(
            id=record_id,
            student_name=student_name,
            admission_no=admission_no,
            register_no=register_no,
            roll_no=roll_no,
            class_course=class_course,
            department=department,
            school_name=school_name,
            dob=dob,
            gender=gender,
            father_name=father_name,
            mother_name=mother_name,
            guardian_name=guardian_name,
            category=category,
            caste=caste,
            religion=religion,
            address=address,
            phone=phone,
            source_file=filename,
            source_path=filepath,
            page_or_sheet=page_or_sheet,
            row_index=row_idx,
            all_fields=all_fields,
            photo_url=photo_url,
            has_photo=has_photo,
            photo_path=photo_path,
            photo_status=photo_status
        )
