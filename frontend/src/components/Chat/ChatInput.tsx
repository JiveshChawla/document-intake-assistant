import React, { useState, useRef, useEffect } from 'react';
import { Send, CornerDownLeft, Loader2 } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading }) => {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!isLoading && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isLoading]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (text.trim() && !isLoading) {
      onSendMessage(text.trim());
      setText('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    // Auto-adjust height
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  };

  return (
    <form onSubmit={handleSubmit} className="relative mt-2">
      <div className="flex items-end gap-2 bg-white rounded-2xl border border-slate-200 p-2 shadow-xs focus-within:border-brand-500 focus-within:ring-2 focus-within:ring-brand-500/10 transition-all">
        <textarea
          ref={textareaRef}
          rows={1}
          value={text}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Answer or provide details (e.g., name, address, executor)..."
          disabled={isLoading}
          className="flex-1 max-h-32 resize-none border-0 bg-transparent px-3 py-1.5 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-0 disabled:opacity-50"
        />

        <button
          type="submit"
          disabled={!text.trim() || isLoading}
          className="h-9 w-9 rounded-xl bg-slate-900 text-white flex items-center justify-center hover:bg-brand-600 disabled:bg-slate-100 disabled:text-slate-300 disabled:cursor-not-allowed transition-all flex-shrink-0 shadow-xs"
          title="Send message"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin text-slate-400" />
          ) : (
            <Send className="h-4 w-4" />
          )}
        </button>
      </div>

      <div className="flex justify-between items-center px-1 mt-1.5 text-[11px] text-slate-400">
        <span>Press <kbd className="font-mono bg-slate-100 px-1 py-0.5 rounded text-[10px] text-slate-500 border border-slate-200">Shift</kbd> + <kbd className="font-mono bg-slate-100 px-1 py-0.5 rounded text-[10px] text-slate-500 border border-slate-200">Enter</kbd> for newline</span>
        <span className="flex items-center gap-1">
          <CornerDownLeft className="h-3 w-3 text-slate-400" /> Enter to send
        </span>
      </div>
    </form>
  );
};
