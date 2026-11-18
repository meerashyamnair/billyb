import React from 'react';
import { GraduationCap, RefreshCw, FileText, Users, AlertCircle } from 'lucide-react';
import type { PortalStats } from '../types';

interface HeaderProps {
  stats: PortalStats | null;
  isScanning: boolean;
  onRescan: () => void;
  onOpenFilesModal: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  stats,
  isScanning,
  onRescan,
  onOpenFilesModal
}) => {
  return (
    <header className="bg-slate-900 text-white shadow-md border-b border-slate-800 no-print">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          
          {/* Logo & Portal Identity */}
          <div className="flex items-center space-x-3.5">
            <div className="w-12 h-12 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-inner shrink-0">
              <GraduationCap className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-blue-400 bg-blue-950/80 px-2 py-0.5 rounded border border-blue-800/50">
                  Academic Archives
                </span>
                <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1 animate-pulse"></span>
                  Active Index
                </span>
              </div>
              <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white mt-0.5">
                STUDENT NOMINAL ROLL SEARCH PORTAL
              </h1>
              <p className="text-xs sm:text-sm text-slate-400">
                Search, Retrieve and Access Student Records Instantly.
              </p>
            </div>
          </div>

          {/* Quick Metrics & Actions */}
          <div className="flex flex-wrap items-center gap-3">
            {stats && (
              <>
                {/* Total Records Counter */}
                <div className="flex items-center space-x-2 bg-slate-800/90 border border-slate-700/80 px-3.5 py-2 rounded-lg text-slate-200">
                  <Users className="w-4 h-4 text-blue-400" />
                  <div className="text-left">
                    <div className="text-xs text-slate-400 font-medium">Students</div>
                    <div className="text-sm font-bold text-white">{stats.total_records.toLocaleString()}</div>
                  </div>
                </div>

                {/* Total Files Button / Modal Trigger */}
                <button
                  onClick={onOpenFilesModal}
                  className="flex items-center space-x-2 bg-slate-800/90 hover:bg-slate-750 border border-slate-700/80 hover:border-slate-600 px-3.5 py-2 rounded-lg text-slate-200 transition-colors cursor-pointer group"
                  title="View Scanned Files Status"
                >
                  <FileText className="w-4 h-4 text-emerald-400 group-hover:scale-110 transition-transform" />
                  <div className="text-left">
                    <div className="text-xs text-slate-400 font-medium flex items-center space-x-1">
                      <span>Files Scanned</span>
                      {stats.failed_files > 0 && (
                        <AlertCircle className="w-3 h-3 text-amber-400" />
                      )}
                    </div>
                    <div className="text-sm font-bold text-white">{stats.total_files}</div>
                  </div>
                </button>
              </>
            )}

            {/* Rescan Button */}
            <button
              onClick={onRescan}
              disabled={isScanning}
              className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-sm font-semibold transition-all shadow-sm ${
                isScanning
                  ? 'bg-blue-800/50 text-blue-300 cursor-not-allowed border border-blue-700/50'
                  : 'bg-blue-600 hover:bg-blue-500 text-white border border-blue-500 cursor-pointer active:scale-95'
              }`}
            >
              <RefreshCw className={`w-4 h-4 ${isScanning ? 'animate-spin text-blue-300' : ''}`} />
              <span className="hidden sm:inline">{isScanning ? 'Scanning...' : 'Rescan Folder'}</span>
              <span className="sm:hidden">{isScanning ? 'Scanning' : 'Rescan'}</span>
            </button>
          </div>

        </div>
      </div>
    </header>
  );
};
