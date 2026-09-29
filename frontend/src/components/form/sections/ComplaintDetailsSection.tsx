import React from 'react';
import { ReadOnlyField } from '../controls/ReadOnlyField';
import { useComplaintStore } from '../../../store/useComplaintStore';

export const ComplaintDetailsSection: React.FC = () => {
  const originCustomer = useComplaintStore((state) => state.complaint.origin_customer);

  return (
    <div>
      <h3 className="text-xs font-bold text-slate-500 tracking-wider uppercase mb-3 flex items-center gap-2">
        <span className="w-5 h-5 rounded-full bg-slate-100 text-slate-600 flex items-center justify-center text-[10px] font-bold">3</span>
        <span>Complaint Details</span>
      </h3>
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <ReadOnlyField
            name="complaint_type"
            label="Complaint Type"
            value={originCustomer.complaint_type}
            placeholder="Awaiting AI extraction..."
          />
          <ReadOnlyField
            name="complaint_date"
            label="Complaint Date"
            value={originCustomer.complaint_date}
            placeholder="Awaiting AI extraction..."
            type="date"
          />
        </div>
        <div>
          <ReadOnlyField
            name="complaint_description"
            label="Detailed Complaint Description"
            value={originCustomer.complaint_description}
            placeholder="Awaiting AI extraction..."
            type="textarea"
            rows={3}
          />
        </div>
      </div>
    </div>
  );
};
