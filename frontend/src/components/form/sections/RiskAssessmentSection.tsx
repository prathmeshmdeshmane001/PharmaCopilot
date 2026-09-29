import React from 'react';
import { ReadOnlyField } from '../controls/ReadOnlyField';
import { useComplaintStore } from '../../../store/useComplaintStore';
import { AlertTriangle, CheckSquare, GitFork, ShieldAlert, Info } from 'lucide-react';

export const RiskAssessmentSection: React.FC = () => {
  const risk = useComplaintStore((state) => state.complaint.risk_assessment);

  // Dynamic severity styling
  const getSeverityBadgeClass = (severity: string) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-rose-50 text-rose-800 border-rose-300 font-bold';
      case 'HIGH':
        return 'bg-amber-50 text-amber-800 border-amber-300 font-bold';
      case 'MEDIUM':
        return 'bg-blue-50 text-blue-800 border-blue-300 font-semibold';
      case 'LOW':
        return 'bg-slate-100 text-slate-700 border-slate-300 font-medium';
      default:
        return 'bg-slate-50 text-slate-500 border-slate-200';
    }
  };

  const hasAssessment = risk && risk.severity && risk.severity !== 'Awaiting Assessment';

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-bold text-slate-500 tracking-wider uppercase flex items-center gap-2">
          <span className="w-5 h-5 rounded-full bg-slate-100 text-slate-600 flex items-center justify-center text-[10px] font-bold">4</span>
          <span>ICH Q9–Informed Risk Assessment &amp; Priority</span>
        </h3>
        {hasAssessment && risk.risk_score && (
          <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200">
            RPN: {risk.risk_score} / 125
          </span>
        )}
      </div>

      <div className="space-y-4">
        {/* Severity & Priority Controls */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <ReadOnlyField
            name="severity"
            label="Initial Severity"
            value={risk.severity}
            placeholder="Awaiting AI assessment..."
            type="select"
            severityColor={getSeverityBadgeClass(risk.severity)}
          />
          <ReadOnlyField
            name="priority"
            label="Priority / Risk Level"
            value={risk.priority}
            placeholder="Awaiting AI assessment..."
            type="select"
          />
        </div>

        {/* Regulatory Escalation Warning if Triggered */}
        {risk.requires_regulatory_escalation && (
          <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg flex items-start gap-2.5 text-xs text-rose-800">
            <ShieldAlert className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold">Regulatory Escalation Triggered:</span> Sterility compromise or adverse clinical impact requires expedited notification to Pharmacovigilance &amp; Qualified Person (QP).
            </div>
          </div>
        )}

        {/* Clinical Reasoning Box */}
        {hasAssessment && risk.reasoning ? (
          <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-lg space-y-2.5">
            <div className="flex items-center gap-1.5 text-xs font-bold text-slate-700">
              <Info className="w-3.5 h-3.5 text-blue-600" />
              <span>Risk Rationale &amp; Evaluation Logic</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              {risk.reasoning}
            </p>

            {/* Recommended Actions */}
            {risk.recommended_actions && risk.recommended_actions.length > 0 && (
              <div className="pt-2 border-t border-slate-200/70">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wide flex items-center gap-1.5 mb-1.5">
                  <CheckSquare className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Mandatory Immediate Actions:</span>
                </span>
                <ul className="space-y-1 pl-1">
                  {risk.recommended_actions.map((action, idx) => (
                    <li key={idx} className="text-xs text-slate-600 flex items-start gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-slate-400 mt-1.5 shrink-0" />
                      <span>{action}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Departmental Routing */}
            {risk.target_routing && risk.target_routing.length > 0 && (
              <div className="pt-2 border-t border-slate-200/70 flex items-center gap-2 flex-wrap">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wide flex items-center gap-1 shrink-0">
                  <GitFork className="w-3 h-3 text-indigo-500" />
                  <span>Routing:</span>
                </span>
                {risk.target_routing.map((dept, idx) => (
                  <span
                    key={idx}
                    className="text-[11px] font-medium px-2 py-0.5 rounded-md bg-white border border-slate-200 text-slate-700 shadow-2xs"
                  >
                    {dept}
                  </span>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs text-slate-600 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-slate-400 shrink-0" />
            <span>ICH Q9–informed risk evaluation and routing will generate automatically upon complaint logging or document extraction.</span>
          </div>
        )}
      </div>
    </div>
  );
};
