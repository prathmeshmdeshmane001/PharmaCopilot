import React, { useEffect, useRef } from 'react';
import { CopilotHeader } from './CopilotHeader';
import { DocumentDropzone } from './DocumentDropzone';
import { ExtractionProgressBar } from './ExtractionProgressBar';
import { ChatMessageItem } from './ChatMessageItem';
import { ChatInputBar } from './ChatInputBar';
import { useChatStore } from '../../store/useChatStore';

export const CopilotContainer: React.FC = () => {
  const messages = useChatStore((state) => state.messages);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <section className="bg-white rounded-xl border border-slate-200 shadow-xs flex flex-col h-[calc(100vh-110px)] sticky top-[76px] overflow-hidden">
      {/* Header */}
      <CopilotHeader />

      {/* Scrollable Assistant Body */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Document Ingestion Zone */}
        <DocumentDropzone />

        {/* Progress Bar (Visible during active document upload) */}
        <ExtractionProgressBar />

        {/* Message Stream */}
        <div className="space-y-3 pt-2 border-t border-slate-100">
          {messages.map((msg) => (
            <ChatMessageItem key={msg.id} message={msg} />
          ))}
        </div>
      </div>

      {/* Bottom Sticky Input Bar */}
      <ChatInputBar />
    </section>
  );
};
