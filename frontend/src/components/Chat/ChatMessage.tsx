import React from 'react';
import { Bot, User, CheckCircle2, AlertTriangle, Info } from 'lucide-react';
import { ChatMessage as ChatMessageType } from '../../types';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessageItem: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  if (isSystem) {
    return (
      <div className="flex items-center justify-center my-3">
        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100/80 text-slate-500 text-xs border border-slate-200/60 font-medium">
          <Info className="h-3 w-3 text-slate-400" />
          <span>{message.content}</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex gap-3 mb-4 group ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div
        className={`h-8 w-8 rounded-xl flex items-center justify-center flex-shrink-0 text-white shadow-xs transition-transform ${
          isUser
            ? 'bg-slate-900'
            : 'bg-gradient-to-tr from-brand-600 to-indigo-600 ring-1 ring-brand-700/20'
        }`}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>

      {/* Bubble Content */}
      <div className={`max-w-[85%] flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`px-4 py-3 rounded-2xl text-sm leading-relaxed transition-all ${
            isUser
              ? 'bg-slate-900 text-white rounded-tr-xs shadow-xs'
              : 'bg-white text-slate-800 border border-slate-200/90 rounded-tl-xs shadow-xs'
          }`}
        >
          <div className="whitespace-pre-wrap">{message.content}</div>

          {/* Extracted fields indicator badge */}
          {message.extracted_fields && message.extracted_fields.length > 0 && (
            <div className="mt-2.5 pt-2 border-t border-slate-100 flex flex-wrap items-center gap-1.5 text-xs text-emerald-700">
              <CheckCircle2 className="h-3.5 w-3.5 flex-shrink-0 text-emerald-600" />
              <span className="font-semibold text-[11px] text-slate-600">Updated:</span>
              {message.extracted_fields.map((f) => (
                <span
                  key={f}
                  className="bg-emerald-50 text-emerald-800 border border-emerald-200/80 px-1.5 py-0.5 rounded-md text-[11px] font-mono font-medium"
                >
                  {f}
                </span>
              ))}
            </div>
          )}

          {/* Ambiguity / Follow-up banner */}
          {message.ambiguities && message.ambiguities.length > 0 && (
            <div className="mt-2.5 pt-2 border-t border-amber-100 flex flex-col gap-1 text-xs text-amber-900 bg-amber-50/80 p-2.5 rounded-xl border border-amber-200">
              <div className="flex items-center gap-1.5 font-semibold text-[11px] text-amber-900">
                <AlertTriangle className="h-3.5 w-3.5 text-amber-600 flex-shrink-0" />
                <span>Clarification Needed:</span>
              </div>
              <ul className="list-disc pl-4 text-[11px] text-amber-800 space-y-0.5">
                {message.ambiguities.map((amb, i) => (
                  <li key={i}>{amb}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Timestamp */}
        <span className="text-[10px] text-slate-400 mt-1 px-1">
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  );
};
