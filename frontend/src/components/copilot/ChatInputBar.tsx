import React, { useState, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { useChatStore } from '../../store/useChatStore';
import { useComplaintStore } from '../../store/useComplaintStore';
import { SuggestedPrompts } from './SuggestedPrompts';

export const ChatInputBar: React.FC = () => {
  const [input, setInput] = useState('');
  const sendMessage = useChatStore((state) => state.sendMessage);
  const resetCounter = useChatStore((state) => state.resetCounter);
  const isAiProcessing = useComplaintStore((state) => state.isAiProcessing);

  useEffect(() => {
    setInput('');
  }, [resetCounter]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isAiProcessing) return;
    const text = input;
    setInput('');
    await sendMessage(text);
  };

  return (
    <div className="p-3 border-t border-slate-200 bg-white shrink-0">
      {/* Compact "Try asking" row */}
      <SuggestedPrompts />

      <form onSubmit={handleSubmit} className="space-y-1.5">
        <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5 focus-within:ring-2 focus-within:ring-indigo-400 focus-within:border-indigo-400 focus-within:bg-white transition-all shadow-2xs">
          <input
            type="text"
            value={input}
            disabled={isAiProcessing}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isAiProcessing ? 'AI is processing request...' : 'Ask me anything about this complaint...'}
            className="flex-1 text-xs bg-transparent border-none focus:outline-none text-slate-800 placeholder-slate-400 disabled:opacity-60"
          />
          <button
            type="submit"
            disabled={!input.trim() || isAiProcessing}
            className="h-7 w-7 rounded-lg bg-blue-600 hover:bg-blue-700 text-white flex items-center justify-center shadow-xs transition-colors shrink-0 disabled:opacity-40 disabled:hover:bg-blue-600 cursor-pointer disabled:cursor-not-allowed"
          >
            {isAiProcessing ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Send className="w-3.5 h-3.5" />
            )}
          </button>
        </div>

        <p className="text-[10px] text-slate-400 text-center select-none">
          AI responses may contain errors. Designed with auditability principles inspired by 21 CFR Part 11.
        </p>
      </form>
    </div>
  );
};
