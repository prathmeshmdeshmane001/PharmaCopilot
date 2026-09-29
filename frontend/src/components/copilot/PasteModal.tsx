import React, { useState } from 'react';
import { X, FileText, ArrowRight } from 'lucide-react';
import { useChatStore } from '../../store/useChatStore';

interface PasteModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PasteModal: React.FC<PasteModalProps> = ({ isOpen, onClose }) => {
  const [text, setText] = useState('');
  const pasteText = useChatStore((state) => state.pasteText);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    await pasteText(text);
    setText('');
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4 animate-in fade-in duration-150">
      <div className="bg-white rounded-xl border border-slate-200 shadow-xl max-w-lg w-full overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-indigo-600" />
            <h3 className="text-sm font-bold text-slate-900">Paste Complaint Text / Email</h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-3">
          <p className="text-xs text-slate-500">
            Paste the raw customer email, transcript, or incident narrative below. The AI will extract pharmaceutical details and populate the complaint form.
          </p>

          <textarea
            rows={7}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="From: pharmacy@hospital.org&#10;Product: Epinephrine 1mg/mL&#10;Batch: B24017&#10;Quantity: 50 vials&#10;Issue: Defective rubber seal leaking liquid..."
            className="w-full p-3 text-xs rounded-lg border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 outline-none resize-none font-mono text-slate-800"
          />

          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:bg-slate-100 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!text.trim()}
              className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-1.5 shadow-xs disabled:opacity-50 transition-colors"
            >
              <span>Extract &amp; Populate</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
