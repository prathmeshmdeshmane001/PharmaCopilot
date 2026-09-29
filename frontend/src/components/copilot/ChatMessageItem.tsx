import React from 'react';
import { Sparkles, User, CheckCircle2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import type { ChatMessage } from '../../store/useChatStore';

interface ChatMessageItemProps {
  message: ChatMessage;
}

export const ChatMessageItem: React.FC<ChatMessageItemProps> = ({ message }) => {
  const isUser = message.sender === 'user';

  return (
    <div className={`flex gap-3 text-xs ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div
        className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5 shadow-2xs ${
          isUser
            ? 'bg-slate-700 text-white'
            : 'bg-blue-600 text-white'
        }`}
      >
        {isUser ? <User className="w-3.5 h-3.5" /> : <Sparkles className="w-3.5 h-3.5" />}
      </div>

      {/* Message Content */}
      <div className={`space-y-1.5 max-w-[85%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`p-3 rounded-xl text-xs leading-relaxed ${
            isUser
              ? 'bg-blue-600 text-white rounded-tr-xs shadow-xs font-normal whitespace-pre-wrap'
              : 'bg-slate-100 text-slate-800 rounded-tl-xs border border-slate-200/80 shadow-2xs font-normal'
          }`}
        >
          {isUser ? (
            <div className="font-normal leading-relaxed">{message.text}</div>
          ) : (
            <div className="markdown-content font-normal text-slate-800 leading-relaxed">
              <ReactMarkdown
                remarkPlugins={[remarkGfm, remarkBreaks]}
                components={{
                  p: ({ children }) => (
                    <p className="mb-2 last:mb-0 leading-relaxed font-normal">{children}</p>
                  ),
                  strong: ({ children }) => (
                    <strong className="font-semibold text-slate-900">{children}</strong>
                  ),
                  b: ({ children }) => (
                    <b className="font-semibold text-slate-900">{children}</b>
                  ),
                  em: ({ children }) => (
                    <em className="italic text-slate-800">{children}</em>
                  ),
                  i: ({ children }) => (
                    <i className="italic text-slate-800">{children}</i>
                  ),
                  ul: ({ children }) => (
                    <ul className="list-disc list-outside pl-4 my-2 space-y-1">{children}</ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="list-decimal list-outside pl-4 my-2 space-y-1">{children}</ol>
                  ),
                  li: ({ children }) => (
                    <li className="font-normal leading-relaxed text-slate-800 pl-0.5">{children}</li>
                  ),
                  h1: ({ children }) => (
                    <h1 className="text-sm font-semibold text-slate-900 mt-2.5 mb-1.5 first:mt-0">{children}</h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className="text-xs font-semibold text-slate-900 mt-2 mb-1 first:mt-0">{children}</h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className="text-xs font-semibold text-slate-900 mt-1.5 mb-0.5 first:mt-0">{children}</h3>
                  ),
                  code: ({ children }) => (
                    <code className="px-1.5 py-0.5 rounded bg-slate-200/80 text-slate-800 font-mono text-[11px]">{children}</code>
                  ),
                  blockquote: ({ children }) => (
                    <blockquote className="border-l-2 border-indigo-400 pl-2.5 my-2 italic text-slate-600 bg-slate-50/50 py-1 rounded-r">
                      {children}
                    </blockquote>
                  ),
                }}
              >
                {message.text}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Embedded Tool Badges */}
        {message.toolBadges && message.toolBadges.length > 0 && (
          <div className="flex flex-wrap gap-1 pt-1">
            {message.toolBadges.map((badge, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200"
              >
                <CheckCircle2 className="w-2.5 h-2.5 text-emerald-600" />
                <span>{badge}</span>
              </span>
            ))}
          </div>
        )}

        {/* Timestamp */}
        <div className={`text-[10px] text-slate-400 px-1 ${isUser ? 'text-right' : 'text-left'}`}>
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
};
