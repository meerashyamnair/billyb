import React, { useState, useEffect, useRef } from 'react';
import { Search, X, RotateCcw, Filter, User, ArrowRight, Loader2 } from 'lucide-react';
import type { Suggestion, PortalStats } from '../types';

interface SearchBarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onSearchSubmit: (query: string) => void;
  onClear: () => void;
  onReset: () => void;
  onSelectSuggestion: (suggestion: Suggestion) => void;
  selectedCourse: string;
  onCourseChange: (course: string) => void;
  selectedFile: string;
  onFileChange: (file: string) => void;
  stats: PortalStats | null;
  coursesList: string[];
}

export const SearchBar: React.FC<SearchBarProps> = ({
  searchQuery,
  onSearchChange,
  onSearchSubmit,
  onClear,
  onReset,
  onSelectSuggestion,
  selectedCourse,
  onCourseChange,
  selectedFile,
  onFileChange,
  stats,
  coursesList
}) => {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [showDropdown, setShowDropdown] = useState<boolean>(false);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState<boolean>(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Debounced suggestion fetch
  useEffect(() => {
    if (!searchQuery.trim() || searchQuery.trim().length < 1) {
      setSuggestions([]);
      setShowDropdown(false);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        setIsLoadingSuggestions(true);
        const res = await fetch(`/api/suggest?q=${encodeURIComponent(searchQuery.trim())}`);
        if (res.ok) {
          const data: Suggestion[] = await res.json();
          setSuggestions(data);
          setShowDropdown(data.length > 0);
        }
      } catch (err) {
        console.error("Suggestion fetch failed:", err);
      } finally {
        setIsLoadingSuggestions(false);
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Handle outside click to close dropdown
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      setShowDropdown(false);
      onSearchSubmit(searchQuery);
    } else if (e.key === 'Escape') {
      setShowDropdown(false);
    }
  };

  const handleSuggestionClick = (item: Suggestion) => {
    setShowDropdown(false);
    onSelectSuggestion(item);
  };

  const highlightMatch = (text: string, query: string) => {
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

  return (
    <div className="w-full bg-white rounded-2xl shadow-xl border border-slate-200 p-5 md:p-6 mb-8 no-print" ref={containerRef}>
      
      {/* Search Input Bar */}
      <div className="relative">
        <div className="relative flex items-center">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
            {isLoadingSuggestions ? (
              <Loader2 className="h-6 w-6 text-blue-600 animate-spin" />
            ) : (
              <Search className="h-6 w-6 text-blue-600" />
            )}
          </div>

          <input
            ref={inputRef}
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            onFocus={() => {
              if (suggestions.length > 0) setShowDropdown(true);
            }}
            onKeyDown={handleKeyDown}
            placeholder="Search student by full name, partial name, admission number, or register number..."
            className="w-full pl-12 pr-28 py-4 text-base md:text-lg text-slate-800 placeholder-slate-400 bg-slate-50 hover:bg-slate-50/80 focus:bg-white border-2 border-slate-300 focus:border-blue-600 rounded-xl transition-all outline-none shadow-inner"
          />

          <div className="absolute inset-y-0 right-0 pr-3 flex items-center space-x-2">
            {searchQuery && (
              <button
                type="button"
                onClick={() => {
                  onClear();
                  inputRef.current?.focus();
                }}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-200 transition-colors"
                title="Clear search"
              >
                <X className="w-5 h-5" />
              </button>
            )}

            <button
              type="button"
              onClick={() => {
                setShowDropdown(false);
                onSearchSubmit(searchQuery);
              }}
              className="px-4 py-2 bg-blue-700 hover:bg-blue-800 text-white rounded-lg text-sm font-semibold shadow-sm transition-all flex items-center space-x-1.5 cursor-pointer active:scale-95"
            >
              <span>Search</span>
            </button>
          </div>
        </div>

        {/* Autocomplete Suggestions Dropdown */}
        {showDropdown && suggestions.length > 0 && (
          <div className="absolute z-50 left-0 right-0 mt-2 bg-white rounded-xl shadow-2xl border border-slate-200 overflow-hidden divide-y divide-slate-100 max-h-96 overflow-y-auto">
            <div className="px-4 py-2 bg-slate-50 text-xs font-semibold text-slate-500 flex justify-between items-center">
              <span>Matching Student Suggestions ({suggestions.length})</span>
              <span className="text-[11px] text-slate-400">Click to view details</span>
            </div>
            {suggestions.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => handleSuggestionClick(item)}
                className="w-full px-4 py-3 text-left hover:bg-blue-50/80 transition-colors flex items-center justify-between group cursor-pointer"
              >
                <div className="flex items-center space-x-3">
                  {item.has_photo && item.photo_url ? (
                    <img
                      src={item.photo_url}
                      alt={item.student_name}
                      className="w-8 h-10 object-cover rounded-md border border-slate-200 shrink-0 shadow-2xs bg-slate-100"
                    />
                  ) : (
                    <div className="w-8 h-10 rounded-md bg-blue-100 text-blue-800 flex items-center justify-center font-bold text-xs shrink-0">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                  <div>
                    <div className="text-sm font-bold text-slate-900 group-hover:text-blue-700">
                      {highlightMatch(item.student_name, searchQuery)}
                    </div>
                    <div className="text-xs text-slate-500 flex flex-wrap items-center gap-x-2 gap-y-0.5 mt-0.5">
                      {item.admission_no && (
                        <span>Admn: <span className="font-semibold text-slate-700">{item.admission_no}</span></span>
                      )}
                      {item.register_no && (
                        <span>• Reg: <span className="font-semibold text-slate-700">{item.register_no}</span></span>
                      )}
                      {item.course && (
                        <span className="text-blue-600 font-medium truncate max-w-xs">• {item.course}</span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center text-xs text-slate-400 group-hover:text-blue-600 transition-colors pl-2 shrink-0">
                  <span className="hidden sm:inline mr-1">Select</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Filter and Reset Bar */}
      <div className="mt-4 pt-4 border-t border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-3 text-sm">
        
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center space-x-1.5 text-slate-500 font-medium text-xs uppercase tracking-wider">
            <Filter className="w-3.5 h-3.5 text-blue-600" />
            <span>Filters:</span>
          </div>

          {/* Course / Program Filter */}
          <div className="relative min-w-44">
            <select
              value={selectedCourse}
              onChange={(e) => onCourseChange(e.target.value)}
              className="w-full bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700 text-xs rounded-lg px-3 py-1.5 pr-8 focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all cursor-pointer"
            >
              <option value="">All Courses / Streams ({coursesList.length})</option>
              {coursesList.map((c, i) => (
                <option key={i} value={c}>
                  {c.length > 50 ? `${c.slice(0, 48)}...` : c}
                </option>
              ))}
            </select>
          </div>

          {/* Nominal Roll File Filter */}
          {stats && stats.files && stats.files.length > 0 && (
            <div className="relative min-w-44">
              <select
                value={selectedFile}
                onChange={(e) => onFileChange(e.target.value)}
                className="w-full bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700 text-xs rounded-lg px-3 py-1.5 pr-8 focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all cursor-pointer"
              >
                <option value="">All Nominal Roll Files ({stats.files.length})</option>
                {stats.files.map((f, i) => (
                  <option key={i} value={f.filename}>
                    {f.filename.length > 45 ? `${f.filename.slice(0, 42)}...` : f.filename} ({f.records_count} rec)
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Reset All Button */}
        <div className="flex items-center justify-end space-x-2">
          {(searchQuery || selectedCourse || selectedFile) && (
            <button
              type="button"
              onClick={onReset}
              className="flex items-center space-x-1.5 text-xs text-rose-600 hover:text-rose-700 hover:bg-rose-50 px-2.5 py-1.5 rounded-lg border border-rose-200 transition-colors cursor-pointer font-medium"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Search & Filters</span>
            </button>
          )}
        </div>

      </div>

    </div>
  );
};
