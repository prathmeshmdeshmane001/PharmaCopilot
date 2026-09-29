export interface ProductDetails {
  product_name: string | null;
  product_grade_strength: string | null;
  dosage_form?: string | null;
  packaging?: string | null;
  manufacturer?: string | null;
}

export interface ManufacturingDetails {
  batch_number: string | null;
  manufacturing_date: string | null;
  expiry_date: string | null;
  affected_quantity: number | null;
  unit_of_measure: string;
}

export interface ComplaintDetails {
  complaint_source: string | null;
  customer_name: string | null;
  complaint_type: string | null;
  complaint_date: string | null;
  complaint_description: string | null;
  purchase_location?: string | null;
  rx_number?: string | null;
}

export interface RiskAssessment {
  severity: string;
  priority: string;
  risk_score: number | null;
  reasoning: string | null;
  recommended_actions: string[];
  target_routing: string[];
  requires_regulatory_escalation: boolean;
  assessed_at: string | null;
}

export interface FieldDiff {
  old: any;
  new: any;
}

export interface AuditEntry {
  id: string;
  timestamp: string;
  trigger_source: string;
  user_prompt: string | null;
  field_changes: Record<string, FieldDiff>;
  risk_recalculated: boolean;
}

export interface ComplaintRecord {
  id: string;
  complaint_number: string;
  status: string;
  origin_customer: ComplaintDetails;
  product_batch: ProductDetails;
  manufacturing: ManufacturingDetails;
  risk_assessment: RiskAssessment;
  audit_trail: AuditEntry[];
  created_at: string;
  updated_at: string;
}

export interface FieldHighlight {
  fieldName: string;
  label: string;
  oldValue?: any;
  newValue?: any;
  timestamp: number;
}
