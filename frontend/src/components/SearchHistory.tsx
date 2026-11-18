import React from 'react';
import { History, X } from 'lucide-react';

interface SearchHistoryProps {
  history: string[];
  onSelectQuery: (query: string) => void;
  onClearHistory: () => void;
}

export const SearchHistory: React.FC<SearchHistoryProps> = ({
  history,
  onSelectQuery,
  onClearHistory
}) => {
  if (history.length === 0) return null;

  return (
    <div className="flex items-center space-x-2 text-xs text-slate-500 mb-6 flex-wrap gap-y-2 no-print">
      <div className="flex items-center space-x-1 text-slate-400 font-medium">
        <History className="w-3.5 h-3.5" />
        <span>Recent Searches:</span>
      </div>

      <div className="flex flex-wrap items-center gap-1.5">
        {history.map((item, idx) => (
          <button
            key={idx}
            onClick={() => onSelectQuery(item)}
            className="px-2.5 py-1 bg-slate-100 hover:bg-blue-50 text-slate-700 hover:text-blue-700 rounded-md border border-slate-200 transition-colors cursor-pointer font-medium"
          >
            {item}
          </button>
        ))}

        <button
          onClick={onClearHistory}
          className="text-slate-400 hover:text-rose-500 p-1 transition-colors cursor-pointer"
          title="Clear search history"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
