import { create } from "zustand";

const sessionId = localStorage.getItem("docuchat-session-id") || crypto.randomUUID();
localStorage.setItem("docuchat-session-id", sessionId);

export const useAppStore = create((set) => ({
  sessionId,
  documents: [],
  messages: [],
  activeDocIds: [],
  loadingChat: false,
  uploading: false,
  setUploading: (uploading) => set({ uploading }),
  setLoadingChat: (loadingChat) => set({ loadingChat }),
  setMessages: (messages) => set({ messages }),
  appendMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  upsertDocument: (document) =>
    set((state) => {
      const existing = state.documents.find((item) => item.doc_id === document.doc_id);
      const documents = existing
        ? state.documents.map((item) => (item.doc_id === document.doc_id ? { ...item, ...document } : item))
        : [document, ...state.documents];

      const activeDocIds = state.activeDocIds.includes(document.doc_id)
        ? state.activeDocIds
        : document.status === "completed"
          ? [document.doc_id, ...state.activeDocIds]
          : state.activeDocIds;

      return { documents, activeDocIds };
    }),
  toggleDocumentSelection: (docId) =>
    set((state) => ({
      activeDocIds: state.activeDocIds.includes(docId)
        ? state.activeDocIds.filter((item) => item !== docId)
        : [...state.activeDocIds, docId],
    })),
}));
