import { create } from 'zustand';
import type { ComplaintRecord, FieldHighlight, FieldDiff } from '../types/complaint';

const createEmptyComplaint = (): ComplaintRecord => ({
  id: '',
  complaint_number: 'CMP-2026-TBD',
  status: 'Pending Triage',
  origin_customer: {
    complaint_source: null,
    customer_name: null,
    complaint_type: null,
    complaint_date: null,
    complaint_description: null,
    purchase_location: null,
    rx_number: null,
  },
  product_batch: {
    product_name: null,
    product_grade_strength: null,
    dosage_form: null,
    packaging: null,
    manufacturer: null,
  },
  manufacturing: {
    batch_number: null,
    manufacturing_date: null,
    expiry_date: null,
    affected_quantity: null,
    unit_of_measure: 'units',
  },
  risk_assessment: {
    severity: 'Awaiting Assessment',
    priority: 'Pending Triage',
    risk_score: null,
    reasoning: null,
    recommended_actions: [],
    target_routing: [],
    requires_regulatory_escalation: false,
    assessed_at: null,
  },
  audit_trail: [],
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
});

interface ComplaintState {
  complaint: ComplaintRecord;
  highlights: Record<string, FieldHighlight>;
  isAiProcessing: boolean;
  
  // Actions
  setIsAiProcessing: (loading: boolean) => void;
  setComplaint: (complaint: ComplaintRecord) => void;
  triggerHighlight: (fieldName: string, label?: string, oldValue?: any, newValue?: any) => void;
  syncFromAgentResponse: (data: { complaint: ComplaintRecord; diffs?: Record<string, FieldDiff> }) => void;
  fetchActiveComplaint: () => Promise<void>;
  resetComplaint: () => void;
}

export const useComplaintStore = create<ComplaintState>((set, get) => ({
  complaint: createEmptyComplaint(),
  highlights: {},
  isAiProcessing: false,

  setIsAiProcessing: (isAiProcessing) => set({ isAiProcessing }),

  setComplaint: (complaint) => set({ complaint }),

  triggerHighlight: (fieldName, label = 'AI Updated', oldValue, newValue) => {
    const highlight: FieldHighlight = {
      fieldName,
      label,
      oldValue,
      newValue,
      timestamp: Date.now(),
    };

    set((state) => ({
      highlights: {
        ...state.highlights,
        [fieldName]: highlight,
      },
    }));

    // Auto-remove highlight after 2.5 seconds (2500ms)
    setTimeout(() => {
      set((state) => {
        const nextHighlights = { ...state.highlights };
        delete nextHighlights[fieldName];
        return { highlights: nextHighlights };
      });
    }, 2500);
  },

  syncFromAgentResponse: ({ complaint, diffs }) => {
    set({ complaint, isAiProcessing: false });

    // Trigger visual pulse highlight on all altered fields
    if (diffs && Object.keys(diffs).length > 0) {
      Object.entries(diffs).forEach(([fieldName, diff]) => {
        const isInitial = diff.old === null || diff.old === undefined || diff.old === '';
        get().triggerHighlight(
          fieldName,
          isInitial ? 'AI Populated' : 'AI Updated',
          diff.old,
          diff.new
        );
      });
    }
  },

  fetchActiveComplaint: async () => {
    try {
      const response = await fetch('/api/complaints/active');
      if (response.ok) {
        const data = await response.json();
        set({ complaint: data });
      }
    } catch {
      // Backend might be offline or starting up
    }
  },

  resetComplaint: () => set({
    complaint: createEmptyComplaint(),
    highlights: {},
    isAiProcessing: false,
  }),
}));
