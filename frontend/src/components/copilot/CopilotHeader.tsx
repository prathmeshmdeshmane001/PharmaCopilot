import React from 'react';
import { Sparkles, RotateCcw } from 'lucide-react';
import { useComplaintStore } from '../../store/useComplaintStore';
import { useChatStore } from '../../store/useChatStore';

export const CopilotHeader: React.FC = () => {
  const resetComplaint = useComplaintStore((state) => state.resetComplaint);
  const setComplaint = useComplaintStore((state) => state.setComplaint);
  const setIsAiProcessing = useComplaintStore((state) => state.setIsAiProcessing);
  const resetChat = useChatStore((state) => state.resetChat);

  const handleReset = async () => {
    // 1. Immediately reset frontend state (complaint form + copilot chat + processing flags)
    setIsAiProcessing(false);
    resetComplaint();
    resetChat();

    // 2. Call backend reset endpoint to clear session in state store
    try {
      const response = await fetch('/api/complaints/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: 'default' }),
      });
      if (response.ok) {
        const freshRecord = await response.json();
        setComplaint(freshRecord);
      }
    } catch (err) {
      console.error('Failed to reset backend session:', err);
    }
  };

  return (
    <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-white shrink-0">
      <div className="flex items-center gap-2">
        <div className="h-7 w-7 rounded-md bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 shadow-2xs">
          <Sparkles className="w-4 h-4" />
        </div>
        <div>
          <h2 className="text-sm font-bold text-slate-900 tracking-tight">AI Complaint Intake Assistant</h2>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={handleReset}
          title="Reset active complaint and copilot session"
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-slate-500 hover:text-rose-600 hover:bg-rose-50 border border-slate-200/80 hover:border-rose-200 text-xs font-medium transition-all shadow-2xs cursor-pointer"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset</span>
        </button>
        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-indigo-50 text-indigo-700 border border-indigo-200">
          BETA
        </span>
      </div>
    </div>
  );
};
