import { useEffect } from 'react';
import { 
  ShieldCheck, 
  Lock
} from 'lucide-react';
import { ComplaintFormContainer } from './components/form/ComplaintFormContainer';
import { CopilotContainer } from './components/copilot/CopilotContainer';
import { useComplaintStore } from './store/useComplaintStore';

export default function App() {
  const fetchActiveComplaint = useComplaintStore((state) => state.fetchActiveComplaint);

  useEffect(() => {
    fetchActiveComplaint();
  }, [fetchActiveComplaint]);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-800">
      {/* Top Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 px-6 py-3.5 flex items-center justify-between shadow-xs">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold shadow-sm">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold text-slate-900 tracking-tight">PharmaCopilot</h1>
              <span className="text-[11px] font-semibold tracking-wide uppercase px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                QA &amp; Pharmacovigilance
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium">Customer Complaint Management System • API &amp; FDF Module</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200 text-slate-600 text-xs font-medium">
            <Lock className="w-3.5 h-3.5 text-slate-500" />
            <span>21 CFR Part 11 Audit Principles</span>
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>API Online</span>
          </div>
        </div>
      </header>

      {/* Main Two-Column Split Screen */}
      <main className="flex-1 max-w-[1600px] w-full mx-auto p-5 grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        
        {/* Left Column (~60% / 7 cols): Customer Complaint Form */}
        <div className="lg:col-span-7">
          <ComplaintFormContainer />
        </div>

        {/* Right Column (~40% / 5 cols): AI Complaint Copilot */}
        <div className="lg:col-span-5">
          <CopilotContainer />
        </div>

      </main>
    </div>
  );
}
