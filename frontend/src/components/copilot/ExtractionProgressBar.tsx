import React from 'react';
import { useChatStore } from '../../store/useChatStore';
import { Loader2 } from 'lucide-react';

export const ExtractionProgressBar: React.FC = () => {
  const uploadProgress = useChatStore((state) => state.uploadProgress);
  const uploadStatusText = useChatStore((state) => state.uploadStatusText);

  if (uploadProgress === null) return null;

  return (
    <div className="p-3.5 bg-blue-50/70 border border-blue-200 rounded-xl space-y-2 animate-in fade-in duration-200">
      <div className="flex items-center justify-between text-xs">
        <span className="font-bold text-blue-900 uppercase tracking-wider flex items-center gap-1.5 text-[11px]">
          <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-600" />
          <span>Extraction Progress</span>
        </span>
        <span className="font-mono font-bold text-blue-700 text-xs">
          {uploadProgress}%
        </span>
      </div>

      {/* Progress Bar Track */}
      <div className="w-full bg-blue-100 rounded-full h-2 overflow-hidden">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out shadow-xs"
          style={{ width: `${uploadProgress}%` }}
        />
      </div>

      <p className="text-[11px] text-slate-600 font-medium">
        {uploadStatusText || 'Analyzing document content and extracting key details... Please wait, this may take a few moments.'}
      </p>
    </div>
  );
};
