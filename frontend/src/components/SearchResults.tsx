import React from 'react';
import { User, FileText, Calendar, Hash, ChevronRight, FileSpreadsheet, Search } from 'lucide-react';
import type { StudentRecord } from '../types';

interface SearchResultsProps {
  results: StudentRecord[];
  searchQuery: string;
  isLoading: boolean;
  onSelectStudent: (student: StudentRecord) => void;
  selectedStudentId?: string;
  onExportSearchResultsExcel: () => void;
}

export const SearchResults: React.FC<SearchResultsProps> = ({
  results,
  searchQuery,
  isLoading,
  onSelectStudent,
  selectedStudentId,
  onExportSearchResultsExcel
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

  if (isLoading) {
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-12 text-center">
        <div className="inline-block animate-spin rounded-full h-10 w-10 border-4 border-blue-600 border-t-transparent mb-4"></div>
        <h3 className="text-base font-semibold text-slate-700">Searching Nominal Roll Records...</h3>
        <p className="text-xs text-slate-400 mt-1">Cross-referencing names and details across documents</p>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-12 text-center">
        <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4 text-slate-400">
          <Search className="w-8 h-8" />
        </div>
        <h3 className="text-lg font-bold text-slate-800">No Student Records Found</h3>
        <p className="text-sm text-slate-500 max-w-md mx-auto mt-1">
          {searchQuery ? (
            <>No matches found for <span className="font-semibold text-slate-700">"{searchQuery}"</span>. Try searching with a partial name, first name, admission number, or check the active filters.</>
          ) : (
            "No nominal roll records available matching the selected criteria."
          )}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header bar with count and bulk export */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 px-1">
        <div>
          <h2 className="text-base font-bold text-slate-800 flex items-center space-x-2">
            <span>Search Results</span>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-200">
              {results.length} {results.length === 1 ? 'Record Found' : 'Records Found'}
            </span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Displaying all identified records matching your search query without arbitrary omission.
          </p>
        </div>

        <button
          onClick={onExportSearchResultsExcel}
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-lg transition-colors cursor-pointer self-start sm:self-auto"
          title="Export matching search results to Excel"
        >
          <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
          <span>Export Search Results (.xlsx)</span>
        </button>
      </div>

      {/* Grid of Student Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {results.map((student) => {
          const isSelected = selectedStudentId === student.id;

          return (
            <div
              key={student.id}
              onClick={() => onSelectStudent(student)}
              className={`bg-white rounded-xl p-5 border transition-all cursor-pointer relative group flex flex-col justify-between ${
                isSelected
                  ? 'border-blue-600 ring-2 ring-blue-500/20 shadow-md bg-blue-50/20'
                  : 'border-slate-200 hover:border-blue-300 hover:shadow-md'
              }`}
            >
              <div>
                {/* Top badges: Sl No & Source Document */}
                <div className="flex items-center justify-between text-xs text-slate-400 mb-2 gap-2">
                  <span className="inline-flex items-center space-x-1 font-mono bg-slate-100 text-slate-600 px-2 py-0.5 rounded text-[11px]">
                    <Hash className="w-3 h-3 text-slate-400" />
                    <span>Roll #{student.roll_no || student.row_index}</span>
                  </span>

                  <span className="inline-flex items-center space-x-1 text-[11px] text-slate-500 bg-slate-50 px-2 py-0.5 rounded border border-slate-100 truncate max-w-[170px]" title={`${student.source_file} (${student.page_or_sheet})`}>
                    <FileText className="w-3 h-3 text-blue-500 shrink-0" />
                    <span className="truncate">{student.page_or_sheet || student.source_file}</span>
                  </span>
                </div>

                {/* Student Photo + Name header */}
                <div className="flex items-start space-x-3 mb-2">
                  {student.has_photo && student.photo_url ? (
                    <img
                      src={student.photo_url}
                      alt={student.student_name}
                      className="w-12 h-16 object-cover rounded-md border border-slate-200 shrink-0 shadow-xs bg-slate-100"
                      loading="lazy"
                    />
                  ) : (
                    <div className="w-12 h-16 bg-slate-100 rounded-md border border-slate-200 flex items-center justify-center text-slate-400 shrink-0">
                      <User className="w-5 h-5 text-slate-300" />
                    </div>
                  )}

                  <div className="min-w-0 flex-1">
                    <h3 className="text-sm sm:text-base font-bold text-slate-900 group-hover:text-blue-700 transition-colors leading-tight">
                      {highlightMatch(student.student_name, searchQuery)}
                    </h3>

                    {/* Course Stream */}
                    {student.class_course && (
                      <p className="text-[11px] text-blue-800 font-medium bg-blue-50/80 border border-blue-100 rounded px-1.5 py-0.5 mt-1 line-clamp-1">
                        {student.class_course}
                      </p>
                    )}
                  </div>
                </div>

                {/* Key metadata grid */}
                <div className="grid grid-cols-2 gap-2 text-xs text-slate-600 mt-3 pt-3 border-t border-slate-100">
                  {student.admission_no && (
                    <div>
                      <span className="text-slate-400 block text-[11px]">Admission No</span>
                      <span className="font-semibold text-slate-800">{highlightMatch(student.admission_no, searchQuery)}</span>
                    </div>
                  )}

                  {student.register_no && (
                    <div>
                      <span className="text-slate-400 block text-[11px]">Register No</span>
                      <span className="font-semibold text-slate-800">{highlightMatch(student.register_no, searchQuery)}</span>
                    </div>
                  )}

                  {student.gender && (
                    <div>
                      <span className="text-slate-400 block text-[11px]">Gender</span>
                      <span className="font-medium text-slate-700">{student.gender}</span>
                    </div>
                  )}

                  {student.dob && (
                    <div>
                      <span className="text-slate-400 block text-[11px]">Date of Birth</span>
                      <span className="font-medium text-slate-700 flex items-center space-x-1">
                        <Calendar className="w-3 h-3 text-slate-400" />
                        <span>{student.dob}</span>
                      </span>
                    </div>
                  )}

                  {student.father_name && (
                    <div className="col-span-2">
                      <span className="text-slate-400 block text-[11px]">Father / Guardian</span>
                      <span className="font-medium text-slate-700 truncate block">{student.father_name || student.guardian_name}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* View Full Profile CTA */}
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-blue-600 group-hover:text-blue-700">
                <span>View Full Profile</span>
                <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
