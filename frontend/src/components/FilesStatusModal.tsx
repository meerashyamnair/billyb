import React from 'react';
import { X, CheckCircle2, AlertTriangle, Folder, RefreshCw } from 'lucide-react';
import type { FileItem } from '../types';

interface FilesStatusModalProps {
  isOpen: boolean;
  onClose: () => void;
  files: FileItem[];
  onRescan: () => void;
  isScanning: boolean;
}

export const FilesStatusModal: React.FC<FilesStatusModalProps> = ({
  isOpen,
  onClose,
  files,
  onRescan,
  isScanning
}) => {
  if (!isOpen) return null;

  const totalFiles = files.length;
  const successFiles = files.filter(f => f.status === 'success').length;
  const failedFiles = files.filter(f => f.status === 'error').length;
  const totalRecords = files.reduce((acc, f) => acc + (f.records_count || 0), 0);

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-2xl w-full overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        
        {/* Header */}
        <div className="bg-slate-900 text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
              <Folder className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Nominal Roll Document Archives</h3>
              <p className="text-xs text-slate-400">Status of scanned nominal roll directory files</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Quick Stats Summary */}
        <div className="bg-slate-50 px-6 py-3 border-b border-slate-200 grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Total Scanned</div>
            <div className="text-lg font-bold text-slate-800">{totalFiles}</div>
          </div>
          <div>
            <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Processed OK</div>
            <div className="text-lg font-bold text-emerald-600">{successFiles} {failedFiles > 0 && `(${failedFiles} err)`}</div>
          </div>
          <div>
            <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Total Records</div>
            <div className="text-lg font-bold text-blue-700">{totalRecords.toLocaleString()}</div>
          </div>
        </div>

        {/* Files Table / List */}
        <div className="p-6 max-h-96 overflow-y-auto divide-y divide-slate-100">
          {files.length === 0 ? (
            <div className="text-center py-8 text-slate-400 text-sm">
              No files found in the nominal_roll directory.
            </div>
          ) : (
            files.map((file, idx) => (
              <div key={idx} className="py-3 flex items-start justify-between gap-3 text-sm">
                <div className="flex items-start space-x-3 min-w-0">
                  <div className="mt-0.5 shrink-0">
                    {file.status === 'success' ? (
                      <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                    ) : (
                      <AlertTriangle className="w-5 h-5 text-rose-500" />
                    )}
                  </div>
                  <div className="min-w-0">
                    <p className="font-semibold text-slate-800 truncate" title={file.filename}>
                      {file.filename}
                    </p>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Type: <span className="uppercase font-mono text-slate-600">{file.file_type}</span> • {file.pages_or_sheets} {file.file_type === 'pdf' ? 'pages' : 'sheets/sections'}
                    </p>
                    {file.error_message && (
                      <p className="text-xs text-rose-600 mt-1 bg-rose-50 p-1.5 rounded border border-rose-200">
                        {file.error_message}
                      </p>
                    )}
                  </div>
                </div>

                <div className="text-right shrink-0">
                  {file.status === 'success' ? (
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                      {file.records_count} records
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                      Failed
                    </span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="bg-slate-50 px-6 py-3 border-t border-slate-200 flex items-center justify-between">
          <button
            onClick={onRescan}
            disabled={isScanning}
            className="flex items-center space-x-1.5 text-xs font-semibold text-blue-700 hover:text-blue-800 hover:bg-blue-50 px-3 py-1.5 rounded-lg border border-blue-200 transition-colors cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isScanning ? 'animate-spin' : ''}`} />
            <span>Rescan Directory</span>
          </button>

          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold transition-colors cursor-pointer"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
};
