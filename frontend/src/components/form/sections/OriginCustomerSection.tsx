import React from 'react';
import { ReadOnlyField } from '../controls/ReadOnlyField';
import { useComplaintStore } from '../../../store/useComplaintStore';

export const OriginCustomerSection: React.FC = () => {
  const originCustomer = useComplaintStore((state) => state.complaint.origin_customer);

  return (
    <div>
      <h3 className="text-xs font-bold text-slate-500 tracking-wider uppercase mb-3 flex items-center gap-2">
        <span className="w-5 h-5 rounded-full bg-slate-100 text-slate-600 flex items-center justify-center text-[10px] font-bold">1</span>
        <span>Origin &amp; Customer Details</span>
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <ReadOnlyField
          name="complaint_source"
          label="Complaint Source"
          value={originCustomer.complaint_source}
          placeholder="Awaiting AI extraction..."
        />
        <ReadOnlyField
          name="customer_name"
          label="Customer Name"
          value={originCustomer.customer_name}
          placeholder="Awaiting AI extraction..."
        />
        <ReadOnlyField
          name="purchase_location"
          label="Purchase Location"
          value={originCustomer.purchase_location}
          placeholder="Awaiting AI extraction..."
        />
        <ReadOnlyField
          name="rx_number"
          label="Rx Number"
          value={originCustomer.rx_number}
          placeholder="Awaiting AI extraction..."
          isMonospace
        />
      </div>
    </div>
  );
};
