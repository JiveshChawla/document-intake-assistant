import React, { useRef, useEffect } from 'react';
import { ChatMessage } from '../../types';
import { ChatMessageItem } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { SuggestedPrompts } from './SuggestedPrompts';
import { Bot, MessagesSquare } from 'lucide-react';

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
    <div className="flex flex-col h-full bg-slate-50/70 dark:bg-slate-950/70 border-r border-slate-200/80 dark:border-slate-800 transition-colors duration-200">
      {/* Chat Sub-header */}
      <div className="px-6 py-3 bg-white dark:bg-slate-900 border-b border-slate-200/80 dark:border-slate-800 flex items-center justify-between shadow-xs transition-colors">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="font-bold text-slate-800 dark:text-slate-200 text-xs tracking-tight flex items-center gap-1.5">
              <MessagesSquare className="h-3.5 w-3.5 text-brand-600 dark:text-brand-400" />
              <span>Legal Intake Interview</span>
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2 text-[11px] text-slate-400 dark:text-slate-500 font-medium">
          <span>{visibleTurns} {visibleTurns === 1 ? 'message' : 'messages'}</span>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-5 md:p-6 space-y-1">
        {messages.map((msg) => (
          <ChatMessageItem key={msg.id} message={msg} />
        ))}

        {/* Animated Typing Indicator */}
        {isLoading && (
          <div className="flex gap-3 mb-4 items-start">
            <div className="h-8 w-8 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 text-white flex items-center justify-center flex-shrink-0 shadow-xs ring-1 ring-brand-700/20">
              <Bot className="h-4 w-4" />
            </div>
            <div className="bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 shadow-xs rounded-2xl rounded-tl-xs px-4 py-3 text-sm text-slate-600 dark:text-slate-300 flex items-center gap-3">
              <span className="text-xs font-semibold text-slate-600 dark:text-slate-400">Assistant is thinking</span>
              <div className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-brand-600 dark:bg-brand-400 typing-dot-1" />
                <span className="w-1.5 h-1.5 rounded-full bg-brand-600 dark:bg-brand-400 typing-dot-2" />
                <span className="w-1.5 h-1.5 rounded-full bg-brand-600 dark:bg-brand-400 typing-dot-3" />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input & Suggested Prompts Area */}
      <div className="p-4 md:p-5 bg-white dark:bg-slate-900 border-t border-slate-200/80 dark:border-slate-800 shadow-xs transition-colors">
        <SuggestedPrompts onSelectPrompt={onSendMessage} isLoading={isLoading} />
        <ChatInput onSendMessage={onSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
};
