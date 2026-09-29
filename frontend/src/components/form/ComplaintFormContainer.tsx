import React, { useState, useEffect } from 'react';
import { Lock, History, ChevronRight } from 'lucide-react';
import { useComplaintStore } from '../../store/useComplaintStore';
import { useChatStore } from '../../store/useChatStore';
import { OriginCustomerSection } from './sections/OriginCustomerSection';
import { ProductBatchSection } from './sections/ProductBatchSection';
import { ComplaintDetailsSection } from './sections/ComplaintDetailsSection';
import { RiskAssessmentSection } from './sections/RiskAssessmentSection';

export const ComplaintFormContainer: React.FC = () => {
  const complaint = useComplaintStore((state) => state.complaint);
  const resetCounter = useChatStore((state) => state.resetCounter);
  const [showAuditTrail, setShowAuditTrail] = useState(false);

  useEffect(() => {
    setShowAuditTrail(false);
  }, [resetCounter]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Under QA Review':
        return 'bg-rose-50 text-rose-800 border-rose-200';
      case 'Escalated':
        return 'bg-purple-50 text-purple-800 border-purple-200';
      default:
        return 'bg-amber-50 text-amber-800 border-amber-200';
    }
  };

  return (
    <section className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden flex flex-col">
      {/* Form Header */}
      <div className="p-6 border-b border-slate-100 flex items-start justify-between bg-white">
        <div>
          <div className="flex items-center gap-2.5 flex-wrap">
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">Log Customer Complaint</h2>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getStatusBadge(complaint.status)}`}>
              {complaint.status}
            </span>
            {complaint.complaint_number && (
              <span className="text-xs font-mono font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded-md">
                {complaint.complaint_number}
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-1 font-medium">API &amp; FDF Quality Assurance Module</p>
        </div>

        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 border border-slate-200 text-slate-700 text-xs font-semibold shadow-2xs select-none">
          <Lock className="w-3.5 h-3.5 text-slate-500" />
          <span>🔒 AI Managed Form (Read-Only)</span>
        </div>
      </div>

      {/* Main 4 Form Sections */}
      <div className="p-6 space-y-7 flex-1">
        <OriginCustomerSection />
        <div className="border-t border-slate-100" />
        <ProductBatchSection />
        <div className="border-t border-slate-100" />
        <ComplaintDetailsSection />
        <div className="border-t border-slate-100" />
        <RiskAssessmentSection />
      </div>

      {/* Audit Trail Drawer (Collapsible) */}
      {showAuditTrail && (
        <div className="border-t border-slate-200 bg-slate-50 p-5 space-y-3 animate-in fade-in duration-200">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
              <History className="w-3.5 h-3.5 text-slate-500" />
              <span>Audit Trail (Designed with principles inspired by 21 CFR Part 11)</span>
            </span>
            <button
              type="button"
              onClick={() => setShowAuditTrail(false)}
              className="text-xs text-slate-500 hover:text-slate-800 underline"
            >
              Close
            </button>
          </div>
          {complaint.audit_trail && complaint.audit_trail.length > 0 ? (
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {complaint.audit_trail.map((entry, idx) => (
                <div key={idx} className="p-2.5 bg-white rounded-lg border border-slate-200 text-xs space-y-1">
                  <div className="flex items-center justify-between text-slate-500 text-[11px]">
                    <span className="font-semibold text-slate-700 uppercase">{entry.trigger_source}</span>
                    <span>{new Date(entry.timestamp).toLocaleTimeString()}</span>
                  </div>
                  {entry.user_prompt && (
                    <p className="text-slate-600 italic">"{entry.user_prompt}"</p>
                  )}
                  {entry.field_changes && Object.keys(entry.field_changes).length > 0 && (
                    <div className="text-[11px] text-slate-500 font-mono pt-1">
                      Deltas: {Object.entries(entry.field_changes).map(([k, d]) => `${k} (${d.old ?? 'null'} → ${d.new})`).join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 italic">No modifications recorded yet.</p>
          )}
        </div>
      )}

      {/* Form Footer */}
      <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>Synchronized with AI Copilot</span>
        </div>
        <button
          type="button"
          onClick={() => setShowAuditTrail(!showAuditTrail)}
          className="flex items-center gap-1 font-semibold text-indigo-600 hover:text-indigo-800 transition-colors"
        >
          <History className="w-3.5 h-3.5" />
          <span>View Audit Trail ({complaint.audit_trail?.length || 0})</span>
          <ChevronRight className={`w-3 h-3 transition-transform ${showAuditTrail ? 'rotate-90' : ''}`} />
        </button>
      </div>
    </section>
  );
};
