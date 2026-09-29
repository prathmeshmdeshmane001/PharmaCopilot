import React from 'react';
import { ReadOnlyField } from '../controls/ReadOnlyField';
import { useComplaintStore } from '../../../store/useComplaintStore';

export const ProductBatchSection: React.FC = () => {
  const productBatch = useComplaintStore((state) => state.complaint.product_batch);
  const manufacturing = useComplaintStore((state) => state.complaint.manufacturing);

  return (
    <div>
      <h3 className="text-xs font-bold text-slate-500 tracking-wider uppercase mb-3 flex items-center gap-2">
        <span className="w-5 h-5 rounded-full bg-slate-100 text-slate-600 flex items-center justify-center text-[10px] font-bold">2</span>
        <span>Product &amp; Batch Identification</span>
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <ReadOnlyField
          name="product_name"
          label="Product Name"
          value={productBatch.product_name}
          placeholder="Awaiting AI extraction..."
        />
        <ReadOnlyField
          name="product_grade_strength"
          label="Product Strength / Grade"
          value={productBatch.product_grade_strength}
          placeholder="Awaiting AI extraction..."
        />
        <ReadOnlyField
          name="dosage_form"
          label="Dosage Form"
          value={productBatch.dosage_form}
          placeholder="Awaiting AI extraction..."
        />
        <ReadOnlyField
          name="packaging"
          label="Packaging"
          value={productBatch.packaging}
          placeholder="Awaiting AI extraction..."
        />
        <ReadOnlyField
          name="manufacturer"
          label="Manufacturer"
          value={productBatch.manufacturer}
          placeholder="Awaiting AI extraction..."
        />
        <ReadOnlyField
          name="batch_number"
          label="Batch / Lot Number"
          value={manufacturing.batch_number}
          placeholder="Awaiting AI extraction..."
          isMonospace
        />
        <ReadOnlyField
          name="manufacturing_date"
          label="Manufacturing Date"
          value={manufacturing.manufacturing_date}
          placeholder="Awaiting AI extraction..."
          type="date"
        />
        <ReadOnlyField
          name="expiry_date"
          label="Expiry Date"
          value={manufacturing.expiry_date}
          placeholder="Awaiting AI extraction..."
          type="date"
        />
        <ReadOnlyField
          name="affected_quantity"
          label="Quantity Affected"
          value={manufacturing.affected_quantity}
          placeholder="Awaiting AI extraction..."
          unit={manufacturing.unit_of_measure || 'units'}
        />
      </div>
    </div>
  );
};
