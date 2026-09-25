import { useState, useEffect } from 'react';
import { api } from './services/api';
import { SessionResponse, PersonalWishesState } from './types';
import { Header } from './components/Header';
import { ChatContainer } from './components/Chat/ChatContainer';
import { PreviewContainer } from './components/Preview/PreviewContainer';
import { StateEditModal } from './components/UI/StateEditModal';
import { AlertCircle, RefreshCw } from 'lucide-react';

export function App() {
  const [session, setSession] = useState<SessionResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  // Load session on startup
  useEffect(() => {
    loadSession();
  }, []);

  const loadSession = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await api.getSession();
      setSession(data);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to the intake backend service.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isSending) return;

    try {
      setIsSending(true);
      setError(null);
      const res = await api.sendMessage(text);
      setSession((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          messages: [...prev.messages, { id: 'temp-u', role: 'user', content: text, timestamp: new Date().toISOString() }, res.message],
          state: res.state,
          document_markdown: res.document_markdown,
          document_html: res.document_html,
          completion_percentage: res.completion_percentage,
          missing_fields: res.missing_fields,
          active_provider: res.active_provider,
        };
      });
      // Refresh cleanly
      const refreshed = await api.getSession();
      setSession(refreshed);
    } catch (err: any) {
      setError(err.message || 'Error processing your message. Please try again.');
    } finally {
      setIsSending(false);
    }
  };

  const handleReset = async () => {
    if (window.confirm('Are you sure you want to reset the interview? All gathered information will be cleared.')) {
      try {
        setIsLoading(true);
        const res = await api.resetSession();
        setSession(res);
      } catch (err: any) {
        setError(err.message || 'Failed to reset session.');
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleSaveStateDirectly = async (newState: PersonalWishesState) => {
    try {
      const res = await api.updateStateDirectly(newState);
      setSession(res);
    } catch (err: any) {
      throw new Error(err.message || 'Validation failed for direct state edit.');
    }
  };

  if (isLoading && !session) {
    return (
      <div className="h-screen w-screen flex flex-col items-center justify-center bg-slate-50 gap-4">
        <div className="h-10 w-10 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-600 font-medium text-sm">
          Initializing Document Intake Assistant...
        </p>
      </div>
    );
  }

  if (error && !session) {
    return (
      <div className="h-screen w-screen flex flex-col items-center justify-center bg-slate-50 p-6 text-center">
        <div className="h-14 w-14 rounded-full bg-red-100 text-red-600 flex items-center justify-center mb-4">
          <AlertCircle className="h-7 w-7" />
        </div>
        <h2 className="text-xl font-bold text-slate-800 mb-2">Backend Connection Error</h2>
        <p className="text-slate-600 text-sm max-w-md mb-6">{error}</p>
        <button
          onClick={loadSession}
          className="flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-lg text-sm font-medium hover:bg-brand-600 transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          <span>Retry Connection</span>
        </button>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-slate-100 overflow-hidden">
      {/* Top Header */}
      <Header
        activeProvider={session?.active_provider || 'mock'}
        completionPercentage={session?.completion_percentage || 0}
        onReset={handleReset}
        onOpenStateEditor={() => setIsEditModalOpen(true)}
        isLoading={isSending}
      />

      {/* Global Error Banner */}
      {error && (
        <div className="bg-red-50 border-b border-red-200 px-6 py-2 text-xs text-red-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-red-600 flex-shrink-0" />
            <span>{error}</span>
          </div>
          <button
            onClick={() => setError(null)}
            className="text-xs font-semibold text-red-800 hover:underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Split-screen Main Layout */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 overflow-hidden">
        {/* Left Side: Interactive Conversational Interview (5 cols on lg) */}
        <div className="lg:col-span-5 h-full overflow-hidden">
          <ChatContainer
            messages={session?.messages || []}
            onSendMessage={handleSendMessage}
            isLoading={isSending}
          />
        </div>

        {/* Right Side: Live Preview (Document & Structured State) (7 cols on lg) */}
        <div className="lg:col-span-7 h-full overflow-hidden">
          <PreviewContainer
            state={session?.state || ({} as PersonalWishesState)}
            documentMarkdown={session?.document_markdown || ''}
            documentHtml={session?.document_html || ''}
            completionPercentage={session?.completion_percentage || 0}
            onOpenEditModal={() => setIsEditModalOpen(true)}
          />
        </div>
      </div>

      {/* Manual State Override / Inspector Modal */}
      {session && (
        <StateEditModal
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          currentState={session.state}
          onSaveState={handleSaveStateDirectly}
        />
      )}
    </div>
  );
}

export default App;
