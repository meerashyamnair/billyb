export interface StudentRecord {
  id: string;
  student_name: string;
  admission_no: string;
  register_no: string;
  roll_no: string;
  class_course: string;
  department: string;
  school_name: string;
  dob: string;
  gender: string;
  father_name: string;
  mother_name: string;
  guardian_name: string;
  category: string;
  caste: string;
  religion: string;
  address: string;
  phone: string;
  source_file: string;
  source_path: string;
  page_or_sheet: string;
  row_index: number;
  all_fields: Record<string, string>;
  photo_url?: string;
  has_photo?: boolean;
  photo_status?: string;
  related_records?: Array<{
    id: string;
    student_name: string;
    admission_no: string;
    course: string;
    source_file: string;
    relation_reason: string;
    photo_url?: string;
    has_photo?: boolean;
  }>;
}

export interface FileItem {
  filename: string;
  file_type: string;
  status: 'success' | 'error' | 'warning';
  records_count: number;
  pages_or_sheets: number;
  error_message?: string | null;
}

export interface PortalStats {
  total_files: number;
  successful_files: number;
  failed_files: number;
  total_records: number;
  courses_count: number;
  schools_count: number;
  last_scanned_at?: number | null;
  is_scanning: boolean;
  files: FileItem[];
}

export interface Suggestion {
  id: string;
  student_name: string;
  admission_no: string;
  register_no: string;
  course: string;
  source_file: string;
  match_score: number;
  photo_url?: string;
  has_photo?: boolean;
  photo_status?: string;
}
