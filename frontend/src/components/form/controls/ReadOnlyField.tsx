import React from 'react';
import { Calendar, ChevronDown, Sparkles } from 'lucide-react';
import { useComplaintStore } from '../../../store/useComplaintStore';

interface ReadOnlyFieldProps {
  id?: string;
  name: string;
  label: string;
  value: string | number | null | undefined;
  placeholder?: string;
  type?: 'text' | 'date' | 'textarea' | 'select';
  unit?: string;
  isMonospace?: boolean;
  className?: string;
  rows?: number;
  severityColor?: string;
}

export const ReadOnlyField: React.FC<ReadOnlyFieldProps> = ({
  name,
  label,
  value,
  placeholder = 'Awaiting AI extraction...',
  type = 'text',
  unit,
  isMonospace = false,
  className = '',
  rows = 3,
  severityColor,
}) => {
  const highlight = useComplaintStore((state) => state.highlights[name]);
  const isHighlighted = !!highlight;

  const displayValue = value !== null && value !== undefined && value !== '' ? String(value) : '';

  return (
    <div className={`relative ${className}`}>
      {/* Label and AI Updated Badge */}
      <div className="flex items-center justify-between mb-1.5">
        <label className="block text-xs font-semibold text-slate-700 tracking-tight">
          {label}
        </label>
        {isHighlighted && (
          <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700 border border-indigo-200 animate-pulse">
            <Sparkles className="w-2.5 h-2.5 text-indigo-500" />
            <span>{highlight.label}</span>
          </span>
        )}
      </div>

      {/* Input container with dynamic highlight ring */}
      <div
        className={`relative transition-all duration-300 rounded-lg ${
          isHighlighted
            ? 'ring-2 ring-indigo-400 border-indigo-400 bg-indigo-50/40 shadow-sm'
            : ''
        }`}
      >
        {type === 'textarea' ? (
          <textarea
            rows={rows}
            readOnly
            disabled
            tabIndex={-1}
            value={displayValue}
            placeholder={placeholder}
            className={`w-full px-3.5 py-2 text-sm rounded-lg border border-slate-200 bg-slate-50/70 text-slate-800 placeholder-slate-400 cursor-default select-text resize-none focus:outline-none ${
              isHighlighted ? 'border-indigo-400' : ''
            }`}
          />
        ) : type === 'select' ? (
          <div className="relative flex items-center">
            <input
              type="text"
              readOnly
              disabled
              tabIndex={-1}
              value={displayValue}
              placeholder={placeholder}
              className={`w-full px-3.5 py-2 text-sm rounded-lg border border-slate-200 bg-slate-50/70 text-slate-800 placeholder-slate-400 cursor-default select-text pr-9 focus:outline-none ${
                severityColor ? severityColor : ''
              } ${isHighlighted ? 'border-indigo-400' : ''}`}
            />
            <ChevronDown className="w-4 h-4 text-slate-400 absolute right-3 pointer-events-none" />
          </div>
        ) : (
          <div className="relative flex">
            <input
              type="text"
              readOnly
              disabled
              tabIndex={-1}
              value={displayValue}
              placeholder={placeholder}
              className={`w-full px-3.5 py-2 text-sm border border-slate-200 bg-slate-50/70 text-slate-800 placeholder-slate-400 cursor-default select-text focus:outline-none ${
                unit ? 'rounded-l-lg' : 'rounded-lg'
              } ${type === 'date' ? 'pr-9' : ''} ${
                isMonospace ? 'font-mono text-slate-900 font-medium' : ''
              } ${isHighlighted ? 'border-indigo-400' : ''}`}
            />
            {type === 'date' && (
              <Calendar className="w-4 h-4 text-slate-400 absolute right-3 top-2.5 pointer-events-none" />
            )}
            {unit && (
              <span className="inline-flex items-center px-3 rounded-r-lg border border-l-0 border-slate-200 bg-slate-100 text-slate-500 text-xs font-semibold select-none">
                {unit}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
