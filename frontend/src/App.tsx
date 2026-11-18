import { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { SearchBar } from './components/SearchBar';
import { SearchResults } from './components/SearchResults';
import { StudentProfileView } from './components/StudentProfileView';
import { SearchHistory } from './components/SearchHistory';
import { FilesStatusModal } from './components/FilesStatusModal';
import type { StudentRecord, PortalStats, Suggestion } from './types';
import { GraduationCap, Shield } from 'lucide-react';

export function App() {
  const [stats, setStats] = useState<PortalStats | null>(null);
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [isFilesModalOpen, setIsFilesModalOpen] = useState<boolean>(false);

  // Search state
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [activeQuery, setActiveQuery] = useState<string>('');
  const [selectedCourse, setSelectedCourse] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<string>('');
  
  // Results & Selection
  const [results, setResults] = useState<StudentRecord[]>([]);
  const [isLoadingResults, setIsLoadingResults] = useState<boolean>(false);
  const [selectedStudent, setSelectedStudent] = useState<StudentRecord | null>(null);

  // Search history during current session
  const [searchHistory, setSearchHistory] = useState<string[]>(() => {
    try {
      const saved = sessionStorage.getItem('nominal_search_history');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // Unique courses for filter dropdown
  const [coursesList, setCoursesList] = useState<string[]>([]);

  // Fetch portal statistics
  const fetchStats = useCallback(async () => {
    try {
      const res = await fetch('/api/stats');
      if (res.ok) {
        const data: PortalStats = await res.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Failed to fetch portal stats:', err);
    }
  }, []);

  // Fetch search results
  const fetchResults = useCallback(async (q: string, course: string = '', file: string = '') => {
    try {
      setIsLoadingResults(true);
      const params = new URLSearchParams();
      if (q.trim()) params.append('q', q.trim());
      if (course) params.append('course', course);
      if (file) params.append('file', file);

      const res = await fetch(`/api/search?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setResults(data.results || []);
        
        // Extract distinct course names if not set
        if (data.results) {
          const courses = Array.from(new Set(
            data.results
              .map((r: StudentRecord) => r.class_course)
              .filter(Boolean)
          )) as string[];
          if (courses.length > 0) {
            setCoursesList(prev => Array.from(new Set([...prev, ...courses])));
          }
        }
      }
    } catch (err) {
      console.error('Search fetch failed:', err);
    } finally {
      setIsLoadingResults(false);
    }
  }, []);

  // Fetch specific student details by ID
  const fetchStudentDetails = useCallback(async (studentId: string) => {
    try {
      setIsLoadingResults(true);
      const res = await fetch(`/api/students/${studentId}`);
      if (res.ok) {
        const data: StudentRecord = await res.json();
        setSelectedStudent(data);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    } catch (err) {
      console.error('Failed to fetch student details:', err);
    } finally {
      setIsLoadingResults(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchStats();
    fetchResults('', '', '');
  }, [fetchStats, fetchResults]);

  // Handle Rescan trigger
  const handleRescan = async () => {
    try {
      setIsScanning(true);
      const res = await fetch('/api/scan', { method: 'POST' });
      if (res.ok) {
        // Poll briefly until scan completes
        setTimeout(async () => {
          await fetchStats();
          await fetchResults(searchQuery, selectedCourse, selectedFile);
          setIsScanning(false);
        }, 3000);
      } else {
        setIsScanning(false);
      }
    } catch (err) {
      console.error('Rescan failed:', err);
      setIsScanning(false);
    }
  };

  // Save query to session history
  const addToHistory = (query: string) => {
    const trimmed = query.trim();
    if (!trimmed || trimmed.length < 2) return;
    setSearchHistory(prev => {
      const filtered = prev.filter(item => item.toLowerCase() !== trimmed.toLowerCase());
      const updated = [trimmed, ...filtered].slice(0, 10);
      try {
        sessionStorage.setItem('nominal_search_history', JSON.stringify(updated));
      } catch (e) {
        console.warn(e);
      }
      return updated;
    });
  };

  const handleClearHistory = () => {
    setSearchHistory([]);
    sessionStorage.removeItem('nominal_search_history');
  };

  // Search submission
  const handleSearchSubmit = (query: string) => {
    setSelectedStudent(null);
    setActiveQuery(query);
    addToHistory(query);
    fetchResults(query, selectedCourse, selectedFile);
  };

  const handleClear = () => {
    setSearchQuery('');
    setActiveQuery('');
    setSelectedStudent(null);
    fetchResults('', selectedCourse, selectedFile);
  };

  const handleReset = () => {
    setSearchQuery('');
    setActiveQuery('');
    setSelectedCourse('');
    setSelectedFile('');
    setSelectedStudent(null);
    fetchResults('', '', '');
  };

  const handleSelectSuggestion = (suggestion: Suggestion) => {
    setSearchQuery(suggestion.student_name);
    setActiveQuery(suggestion.student_name);
    addToHistory(suggestion.student_name);
    fetchStudentDetails(suggestion.id);
  };

  const handleExportSearchResultsExcel = () => {
    const params = new URLSearchParams();
    if (activeQuery) params.append('q', activeQuery);
    if (selectedCourse) params.append('course', selectedCourse);
    if (selectedFile) params.append('file', selectedFile);
    window.open(`/api/export/search-excel?${params.toString()}`, '_blank');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      
      {/* Institutional Top Navbar */}
      <Header
        stats={stats}
        isScanning={isScanning}
        onRescan={handleRescan}
        onOpenFilesModal={() => setIsFilesModalOpen(true)}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Banner with Institution Details */}
        <div className="mb-6 text-center max-w-3xl mx-auto no-print">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-800 border border-blue-200 mb-3">
            <Shield className="w-3.5 h-3.5 text-blue-600" />
            <span>Official Academic Nominal Roll Archive & Verification</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            STUDENT NOMINAL ROLL SEARCH PORTAL
          </h2>
          <p className="text-sm sm:text-base text-slate-600 mt-1.5">
            Search, Retrieve and Access Student Records Instantly.
          </p>
        </div>

        {/* Search Bar Component */}
        <SearchBar
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onSearchSubmit={handleSearchSubmit}
          onClear={handleClear}
          onReset={handleReset}
          onSelectSuggestion={handleSelectSuggestion}
          selectedCourse={selectedCourse}
          onCourseChange={(c) => {
            setSelectedCourse(c);
            fetchResults(activeQuery, c, selectedFile);
          }}
          selectedFile={selectedFile}
          onFileChange={(f) => {
            setSelectedFile(f);
            fetchResults(activeQuery, selectedCourse, f);
          }}
          stats={stats}
          coursesList={coursesList}
        />

        {/* Search History Chips */}
        <SearchHistory
          history={searchHistory}
          onSelectQuery={(q) => {
            setSearchQuery(q);
            handleSearchSubmit(q);
          }}
          onClearHistory={handleClearHistory}
        />

        {/* Detail View OR Results List */}
        {selectedStudent ? (
          <StudentProfileView
            student={selectedStudent}
            searchQuery={activeQuery || searchQuery}
            onBack={() => setSelectedStudent(null)}
            onSelectRelated={(relatedId) => fetchStudentDetails(relatedId)}
          />
        ) : (
          <SearchResults
            results={results}
            searchQuery={activeQuery || searchQuery}
            isLoading={isLoadingResults}
            onSelectStudent={(student) => fetchStudentDetails(student.id)}
            selectedStudentId={selectedStudent ? (selectedStudent as StudentRecord).id : undefined}
            onExportSearchResultsExcel={handleExportSearchResultsExcel}
          />
        )}

      </main>

      {/* Files Status Modal */}
      <FilesStatusModal
        isOpen={isFilesModalOpen}
        onClose={() => setIsFilesModalOpen(false)}
        files={stats?.files || []}
        onRescan={handleRescan}
        isScanning={isScanning}
      />

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 mt-auto text-xs text-slate-500 text-center no-print">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center space-x-2">
            <GraduationCap className="w-4 h-4 text-blue-600" />
            <span className="font-semibold text-slate-700">Student Nominal Roll Search Portal</span>
            <span>• Authorized Academic Archive System</span>
          </div>
          <div>
            Direct archival extraction from <span className="font-mono text-slate-700 font-semibold">nominal_roll/</span> documents
          </div>
        </div>
      </footer>

    </div>
  );
}

export default App;
