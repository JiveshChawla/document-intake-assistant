import React, { useRef, useEffect } from 'react';
import { ChatMessage } from '../../types';
import { ChatMessageItem } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { SuggestedPrompts } from './SuggestedPrompts';
import { MessagesSquare } from 'lucide-react';

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

  return (
    <div className="flex flex-col h-full bg-slate-50 border-r border-slate-200">
      {/* Chat Sub-header */}
      <div className="px-5 py-3 bg-white border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center gap-2 text-slate-800 font-semibold text-sm">
          <MessagesSquare className="h-4 w-4 text-brand-600" />
          <span>Interactive Legal Interview</span>
        </div>
        <span className="text-xs text-slate-400">
          {messages.filter((m) => m.role !== 'system').length} turns
        </span>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-5 space-y-1">
        {messages.map((msg) => (
          <ChatMessageItem key={msg.id} message={msg} />
        ))}

        {isLoading && (
          <div className="flex gap-3 items-center text-slate-400 text-xs py-2">
            <div className="h-7 w-7 rounded-full bg-brand-100 flex items-center justify-center text-brand-600">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-600"></span>
              </span>
            </div>
            <span className="italic">Assistant is analyzing input and updating structured state...</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input & Suggested Prompts Area */}
      <div className="p-4 bg-white border-t border-slate-200">
        <SuggestedPrompts onSelectPrompt={onSendMessage} isLoading={isLoading} />
        <ChatInput onSendMessage={onSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
};
