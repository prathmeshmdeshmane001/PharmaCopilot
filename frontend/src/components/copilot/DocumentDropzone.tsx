import React, { useRef, useState } from 'react';
import { UploadCloud, FileText, CheckCircle2 } from 'lucide-react';
import { useChatStore } from '../../store/useChatStore';
import { PasteModal } from './PasteModal';

export const DocumentDropzone: React.FC = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isPasteOpen, setIsPasteOpen] = useState(false);
  const uploadFile = useChatStore((state) => state.uploadFile);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      await uploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      await uploadFile(e.target.files[0]);
      e.target.value = '';
    }
  };

  return (
    <div className="space-y-2.5">
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx,.txt,.eml"
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* Dashed Dropzone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-5 text-center transition-all cursor-pointer select-none ${
          isDragging
            ? 'border-indigo-500 bg-indigo-50/60 scale-[0.99]'
            : 'border-slate-200 hover:border-indigo-400 bg-slate-50/50 hover:bg-slate-50'
        }`}
      >
        <UploadCloud className="w-8 h-8 text-indigo-500 mx-auto mb-1.5" />
        <p className="text-xs font-semibold text-slate-700">
          Drag &amp; drop complaint document here
        </p>
        <p className="text-[11px] text-slate-500 mt-0.5">
          or <span className="text-indigo-600 font-semibold underline">click to browse</span>
        </p>
      </div>

      {/* OR Divider */}
      <div className="relative flex items-center justify-center my-1">
        <div className="border-t border-slate-200 w-full" />
        <span className="bg-white px-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider absolute">
          OR
        </span>
      </div>

      {/* Paste Button */}
      <button
        type="button"
        onClick={() => setIsPasteOpen(true)}
        className="w-full py-2 px-3 border border-slate-200 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-50 flex items-center justify-center gap-2 transition-colors shadow-2xs"
      >
        <FileText className="w-3.5 h-3.5 text-slate-500" />
        <span>Paste Complaint Text / Email</span>
      </button>

      {/* Supported Formats Banner */}
      <div className="px-3 py-2 rounded-lg bg-emerald-50/70 border border-emerald-200/80 text-[11px] text-emerald-800 flex items-center gap-2">
        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
        <span>Supported formats: PDF, DOCX, TXT, EML • Max size: 10MB</span>
      </div>

      {/* Paste Modal */}
      <PasteModal isOpen={isPasteOpen} onClose={() => setIsPasteOpen(false)} />
    </div>
  );
};
