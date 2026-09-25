import React, { useRef, useEffect } from 'react';
import { ChatMessage } from '../../types';
import { ChatMessageItem } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { SuggestedPrompts } from './SuggestedPrompts';
import { Bot } from 'lucide-react';

interface ChatContainerProps {
  messages: ChatMessage[];
  onSendMessage: (text: string) => void;
  isLoading: boolean;
}

export const ChatContainer: React.FC<ChatContainerProps> = ({
  messages,
  onSendMessage,
  isLoading,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const visibleTurns = messages.filter((m) => m.role !== 'system').length;

  return (
    <div className="flex flex-col h-full bg-slate-50/70 border-r border-slate-200/80">
      {/* Chat Sub-header */}
      <div className="px-5 py-3 bg-white border-b border-slate-200/80 flex items-center justify-between shadow-xs">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="font-semibold text-slate-800 text-xs tracking-tight">
              Legal Intake Interview
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2 text-[11px] text-slate-400">
          <span>{visibleTurns} {visibleTurns === 1 ? 'message' : 'messages'}</span>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-5 space-y-1">
        {messages.map((msg) => (
          <ChatMessageItem key={msg.id} message={msg} />
        ))}

        {/* Animated Typing Indicator */}
        {isLoading && (
          <div className="flex gap-3 mb-4 items-start">
            <div className="h-8 w-8 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 text-white flex items-center justify-center flex-shrink-0 shadow-xs ring-1 ring-brand-700/20">
              <Bot className="h-4 w-4" />
            </div>
            <div className="bg-white border border-slate-200/90 shadow-xs rounded-2xl rounded-tl-xs px-4 py-3 text-sm text-slate-600 flex items-center gap-3">
              <span className="text-xs font-medium text-slate-500">Assistant is thinking</span>
              <div className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-brand-600 typing-dot-1" />
                <span className="w-1.5 h-1.5 rounded-full bg-brand-600 typing-dot-2" />
                <span className="w-1.5 h-1.5 rounded-full bg-brand-600 typing-dot-3" />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input & Suggested Prompts Area */}
      <div className="p-4 bg-white border-t border-slate-200/80 shadow-xs">
        <SuggestedPrompts onSelectPrompt={onSendMessage} isLoading={isLoading} />
        <ChatInput onSendMessage={onSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
};
