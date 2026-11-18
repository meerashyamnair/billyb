import React from 'react';
import { 
  Building, 
  Printer, 
  Download, 
  FileSpreadsheet, 
  ArrowLeft, 
  ShieldCheck, 
  BookOpen, 
  Layers, 
  Users,
  ExternalLink,
  User,
  AlertCircle
} from 'lucide-react';
import type { StudentRecord } from '../types';

interface StudentProfileViewProps {
  student: StudentRecord;
  searchQuery: string;
  onBack: () => void;
  onSelectRelated: (studentId: string) => void;
}

export const StudentProfileView: React.FC<StudentProfileViewProps> = ({
  student,
  searchQuery,
  onBack,
  onSelectRelated
}) => {
  const highlightMatch = (text: string, query: string) => {
    if (!text) return '—';
    if (!query.trim()) return text;
    const parts = text.split(new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'));
    return (
      <span>
        {parts.map((part, i) =>
          part.toLowerCase() === query.toLowerCase() ? (
            <mark key={i} className="bg-yellow-200 text-slate-900 rounded-xs px-0.5 font-bold">
              {part}
            </mark>
          ) : (
            part
          )
        )}
      </span>
    );
  };

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadPdf = () => {
    window.open(`/api/export/pdf/${student.id}`, '_blank');
  };

  const handleDownloadExcel = () => {
    window.open(`/api/export/excel/${student.id}`, '_blank');
  };

  const allFields = student.all_fields || {};
  const entries = Object.entries(allFields);

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden mb-12">
      
      {/* Top Action & Navigation Bar */}
      <div className="bg-slate-900 text-white px-6 py-4 flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 no-print">
        <button
          onClick={onBack}
          className="inline-flex items-center space-x-2 text-sm text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Search Results</span>
        </button>

        {/* Action Buttons: PDF, Excel, Print */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleDownloadPdf}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white shadow-sm transition-colors cursor-pointer"
            title="Download verified student nominal profile as PDF"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download PDF</span>
          </button>

          <button
            onClick={handleDownloadExcel}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm transition-colors cursor-pointer"
            title="Export student record as Excel"
          >
            <FileSpreadsheet className="w-3.5 h-3.5" />
            <span>Export Excel</span>
          </button>

          <button
            onClick={handlePrint}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-700 hover:bg-slate-600 text-slate-200 shadow-sm transition-colors cursor-pointer"
            title="Print student profile"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>Print Profile</span>
          </button>
        </div>
      </div>

      <div className="p-6 md:p-8 space-y-8">
        
        {/* Institutional Profile Header / Banner with Extracted Photograph */}
        <div className="border-b border-slate-200 pb-6">
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
            
            {/* Left: Prominent Photograph + Student Details */}
            <div className="flex flex-col sm:flex-row items-start gap-5">
              {/* Prominent Student Photograph */}
              <div className="shrink-0 flex flex-col items-center">
                {student.has_photo && student.photo_url ? (
                  <div className="relative group">
                    <img
                      src={student.photo_url}
                      alt={student.student_name}
                      className="w-28 h-36 sm:w-32 sm:h-40 object-cover rounded-xl shadow-md border-2 border-white ring-2 ring-blue-600/30 bg-slate-100"
                    />
                    <div className="mt-1.5 text-center">
                      {student.photo_status === 'matched' ? (
                        <span className="inline-flex items-center space-x-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                          <span>Extracted Photo</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center space-x-1 text-[11px] font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
                          <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                          <span>Verify Photo</span>
                        </span>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="w-28 h-36 sm:w-32 sm:h-40 bg-slate-100 rounded-xl border border-dashed border-slate-300 flex flex-col items-center justify-center text-slate-400 p-2 text-center text-xs">
                    <User className="w-8 h-8 text-slate-300 mb-1" />
                    <span className="text-[11px]">No Photo in File</span>
                  </div>
                )}
              </div>

              {/* Basic Info */}
              <div>
                <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-blue-700 mb-1">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                  <span>Verified Nominal Roll Record</span>
                  <span className="text-slate-300">•</span>
                  <span className="text-slate-500">{student.page_or_sheet}</span>
                </div>
                
                <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                  {highlightMatch(student.student_name, searchQuery)}
                </h1>

                {student.class_course && (
                  <p className="text-sm sm:text-base font-semibold text-blue-900 mt-1 flex items-center space-x-1.5">
                    <BookOpen className="w-4 h-4 text-blue-600 shrink-0" />
                    <span>{student.class_course}</span>
                  </p>
                )}

                {student.school_name && (
                  <p className="text-xs sm:text-sm text-slate-500 mt-0.5 flex items-center space-x-1.5">
                    <Building className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    <span>{student.school_name}</span>
                  </p>
                )}
              </div>
            </div>

            {/* Document Badges */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 text-xs text-slate-600 shrink-0 flex flex-col gap-1 min-w-[220px]">
              <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-0.5">
                Archival Reference
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Document:</span>
                <span className="font-semibold text-slate-800 truncate max-w-[140px]" title={student.source_file}>
                  {student.source_file}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Location:</span>
                <span className="font-semibold text-slate-800">{student.page_or_sheet}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Record ID:</span>
                <span className="font-mono text-slate-700 text-[11px]">{student.id}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Primary Identification Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
          {student.admission_no && (
            <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-3.5">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Admission No</span>
              <span className="text-base font-bold text-slate-800 mt-0.5 block">
                {highlightMatch(student.admission_no, searchQuery)}
              </span>
            </div>
          )}

          {student.register_no && (
            <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-3.5">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Register No</span>
              <span className="text-base font-bold text-slate-800 mt-0.5 block">
                {highlightMatch(student.register_no, searchQuery)}
              </span>
            </div>
          )}

          {student.roll_no && (
            <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-3.5">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Roll / Sl No</span>
              <span className="text-base font-bold text-slate-800 mt-0.5 block">
                #{student.roll_no}
              </span>
            </div>
          )}

          {student.gender && (
            <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-3.5">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Gender</span>
              <span className="text-base font-bold text-slate-800 mt-0.5 block">
                {student.gender}
              </span>
            </div>
          )}

          {student.dob && (
            <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-3.5">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Date of Birth</span>
              <span className="text-base font-bold text-slate-800 mt-0.5 block">
                {student.dob}
              </span>
            </div>
          )}
        </div>

        {/* All Extracted Information Table (Complete & Dynamic) */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
              <Layers className="w-4 h-4 text-blue-600" />
              <span>Complete Extracted Document Details</span>
            </h2>
            <span className="text-xs text-slate-400 font-medium">
              Dynamically derived from source without fabrication
            </span>
          </div>

          <div className="border border-slate-200 rounded-xl overflow-hidden shadow-xs">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider w-1/3">
                    Attribute / Field
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">
                    Extracted Value
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-100">
                {entries.length > 0 ? (
                  entries.map(([key, value], idx) => (
                    <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'}>
                      <td className="px-4 py-2.5 font-semibold text-slate-700 text-xs sm:text-sm whitespace-nowrap">
                        {key}
                      </td>
                      <td className="px-4 py-2.5 text-slate-900 text-xs sm:text-sm font-medium">
                        {key.toLowerCase().includes('name') || key.toLowerCase().includes('no') ? (
                          highlightMatch(value, searchQuery)
                        ) : (
                          value
                        )}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={2} className="px-4 py-6 text-center text-slate-400 text-sm">
                      No additional fields extracted from this record.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Related Student Records */}
        {student.related_records && student.related_records.length > 0 && (
          <div className="pt-4 border-t border-slate-200 no-print">
            <h3 className="text-sm font-bold text-slate-800 flex items-center space-x-2 mb-3">
              <Users className="w-4 h-4 text-blue-600" />
              <span>Other Matching or Related Records ({student.related_records.length})</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {student.related_records.map((rel) => (
                <div
                  key={rel.id}
                  onClick={() => onSelectRelated(rel.id)}
                  className="p-3 rounded-lg border border-slate-200 hover:border-blue-300 hover:bg-blue-50/30 transition-all cursor-pointer group text-xs"
                >
                  <div className="font-bold text-slate-900 group-hover:text-blue-700 flex items-center justify-between">
                    <span>{rel.student_name}</span>
                    <ExternalLink className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-600" />
                  </div>
                  <div className="text-slate-500 mt-1">
                    {rel.course}
                  </div>
                  <div className="text-[11px] text-slate-400 flex items-center justify-between mt-2 pt-1 border-t border-slate-100">
                    <span className="truncate max-w-[150px]">{rel.source_file}</span>
                    <span className="text-blue-600 font-medium">View</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
