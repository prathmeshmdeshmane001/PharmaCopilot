import { create } from 'zustand';
import { useComplaintStore } from './useComplaintStore';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  toolBadges?: string[];
  timestamp: string;
}

interface ChatState {
  messages: ChatMessage[];
  uploadProgress: number | null;
  uploadStatusText: string | null;
  error: string | null;
  resetCounter: number;

  // Actions
  sendMessage: (text: string) => Promise<void>;
  uploadFile: (file: File) => Promise<void>;
  pasteText: (text: string) => Promise<void>;
  clearError: () => void;
  resetChat: () => void;
}

const initialWelcomeMessage: ChatMessage = {
  id: 'welcome-1',
  sender: 'assistant',
  text: 'Upload a complaint document or paste text above. I will automatically extract the details, populate the complaint form, and perform an ICH Q9–informed risk assessment for you.',
  timestamp: new Date().toISOString(),
};

export const useChatStore = create<ChatState>((set) => ({
  messages: [initialWelcomeMessage],
  uploadProgress: null,
  uploadStatusText: null,
  error: null,
  resetCounter: 0,

  clearError: () => set({ error: null }),

  resetChat: () => set((state) => ({
    messages: [
      {
        id: `welcome-${Date.now()}`,
        sender: 'assistant',
        text: 'Upload a complaint document or paste text above. I will automatically extract the details, populate the complaint form, and perform an ICH Q9–informed risk assessment for you.',
        timestamp: new Date().toISOString(),
      },
    ],
    uploadProgress: null,
    uploadStatusText: null,
    error: null,
    resetCounter: state.resetCounter + 1,
  })),

  sendMessage: async (text: string) => {
    if (!text.trim()) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: text.trim(),
      timestamp: new Date().toISOString(),
    };

    set((state) => ({
      messages: [...state.messages, userMsg],
      error: null,
    }));

    const { setIsAiProcessing, syncFromAgentResponse } = useComplaintStore.getState();
    setIsAiProcessing(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, session_id: 'default' }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server returned error ${response.status}`);
      }

      const data = await response.json();

      // Sync form and trigger highlights
      syncFromAgentResponse({
        complaint: data.complaint,
        diffs: data.diffs,
      });

      const assistantMsg: ChatMessage = {
        id: `assistant-${Date.now()}`,
        sender: 'assistant',
        text: data.message,
        toolBadges: data.tool_badges || [],
        timestamp: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, assistantMsg],
      }));
    } catch (err: any) {
      console.error('Chat error:', err);
      set({ error: err.message || 'Failed to send message.' });

      const errorMsg: ChatMessage = {
        id: `error-${Date.now()}`,
        sender: 'assistant',
        text: `Error processing request: ${err.message || 'Connection failed'}. Please ensure the backend is running.`,
        timestamp: new Date().toISOString(),
      };
      set((state) => ({ messages: [...state.messages, errorMsg] }));
    } finally {
      setIsAiProcessing(false);
    }
  },

  uploadFile: async (file: File) => {
    const { setIsAiProcessing, syncFromAgentResponse } = useComplaintStore.getState();
    setIsAiProcessing(true);

    set({
      uploadProgress: 15,
      uploadStatusText: `Reading ${file.name}...`,
      error: null,
    });

    try {
      // Simulate progress progression for realistic UX
      const progressTimer1 = setTimeout(() => {
        set({ uploadProgress: 45, uploadStatusText: 'Analyzing document structure & tables...' });
      }, 400);

      const progressTimer2 = setTimeout(() => {
        set({ uploadProgress: 75, uploadStatusText: 'Extracting pharmaceutical entities & evaluating risk...' });
      }, 900);

      const formData = new FormData();
      formData.append('file', file);
      formData.append('session_id', 'default');

      const response = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData,
      });

      clearTimeout(progressTimer1);
      clearTimeout(progressTimer2);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Upload failed with status ${response.status}`);
      }

      const data = await response.json();

      set({ uploadProgress: 100, uploadStatusText: 'Extraction complete! Populating form...' });

      // Sync form and trigger highlights
      syncFromAgentResponse({
        complaint: data.complaint,
        diffs: data.diffs,
      });

      const assistantMsg: ChatMessage = {
        id: `assistant-upload-${Date.now()}`,
        sender: 'assistant',
        text: data.message,
        toolBadges: data.tool_badges || [],
        timestamp: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, assistantMsg],
      }));

      // Hide progress bar after 1.5 seconds
      setTimeout(() => {
        set({ uploadProgress: null, uploadStatusText: null });
      }, 1500);
    } catch (err: any) {
      console.error('Upload error:', err);
      set({
        uploadProgress: null,
        uploadStatusText: null,
        error: err.message || 'Failed to upload document.',
      });
      const errorMsg: ChatMessage = {
        id: `error-${Date.now()}`,
        sender: 'assistant',
        text: `Document upload error: ${err.message || 'Upload failed'}.`,
        timestamp: new Date().toISOString(),
      };
      set((state) => ({ messages: [...state.messages, errorMsg] }));
    } finally {
      setIsAiProcessing(false);
    }
  },

  pasteText: async (text: string) => {
    if (!text.trim()) return;

    const { setIsAiProcessing, syncFromAgentResponse } = useComplaintStore.getState();
    setIsAiProcessing(true);
    set({ error: null });

    try {
      const response = await fetch('/api/documents/paste', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, session_id: 'default' }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Paste processing failed`);
      }

      const data = await response.json();

      syncFromAgentResponse({
        complaint: data.complaint,
        diffs: data.diffs,
      });

      const assistantMsg: ChatMessage = {
        id: `assistant-paste-${Date.now()}`,
        sender: 'assistant',
        text: data.message,
        toolBadges: data.tool_badges || [],
        timestamp: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, assistantMsg],
      }));
    } catch (err: any) {
      console.error('Paste error:', err);
      set({ error: err.message || 'Failed to process pasted text.' });
    } finally {
      setIsAiProcessing(false);
    }
  },
}));
