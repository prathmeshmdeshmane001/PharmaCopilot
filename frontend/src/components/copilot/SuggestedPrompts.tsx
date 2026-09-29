import React from 'react';
import { Sparkles } from 'lucide-react';
import { useChatStore } from '../../store/useChatStore';
import { useComplaintStore } from '../../store/useComplaintStore';

interface SuggestedChip {
  label: string;
  prompt: string;
}

const CHIPS: SuggestedChip[] = [
  { label: 'Check completeness', prompt: 'Check if this complaint is complete.' },
  { label: 'Summarize complaint', prompt: 'Give me a structured summary of this complaint.' },
  { label: 'Recommend CAPA', prompt: 'What CAPA actions would you recommend for this complaint?' },
];

export const SuggestedPrompts: React.FC = () => {
  const messages = useChatStore((state) => state.messages);
  const sendMessage = useChatStore((state) => state.sendMessage);
  const isAiProcessing = useComplaintStore((state) => state.isAiProcessing);

  // Show primarily when conversation is empty or has minimal messages (<= 1 user turn)
  const userMessagesCount = messages.filter((m) => m.sender === 'user').length;
  if (userMessagesCount > 0 || messages.length > 2) {
    return null;
  }

  return (
    <div className="flex items-center gap-1.5 flex-wrap px-0.5 pb-2 text-[11px] select-none transition-all animate-fadeIn">
      <span className="text-slate-400 font-medium flex items-center gap-1 shrink-0">
        <Sparkles className="w-3 h-3 text-indigo-500" />
        <span>Try asking:</span>
      </span>
      <div className="flex items-center gap-1.5 flex-wrap">
        {CHIPS.map((chip, idx) => (
          <button
            key={idx}
            type="button"
            disabled={isAiProcessing}
            onClick={() => sendMessage(chip.prompt)}
            className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-slate-100 hover:bg-indigo-50 text-slate-600 hover:text-indigo-700 border border-slate-200/80 hover:border-indigo-300 transition-all cursor-pointer shadow-2xs disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {chip.label}
          </button>
        ))}
      </div>
    </div>
  );
};

