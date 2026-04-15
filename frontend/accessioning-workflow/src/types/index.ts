// ---------------------------------------------------------------------------
// Shared value types
// ---------------------------------------------------------------------------

export type PriorityValue = 'routine' | 'priority' | 'stat';
export type AccessionedValue = 'yes' | 'no' | null;
export type HoldType = 'breast' | 'miscellaneous' | null;

export type SectionKey =
  | 'client_requests'
  | 'bone_marrow'
  | 'frozen_section'
  | 'stat_cases'
  | 'held_cases';

// ---------------------------------------------------------------------------
// Row shapes (one per table section)
// ---------------------------------------------------------------------------

export interface CaseRow {
  id: string;          // crypto.randomUUID() — React key only, not submitted
  case_number: string;
}

export interface ClientRequestRow extends CaseRow {
  requested_pathologist: string | null;
  send_out_if_positive: boolean;
  priority: PriorityValue;
}

export interface BoneMarrowRow extends CaseRow {
  priority: PriorityValue;
  send_out: boolean;
  assign_pathologist: string | null;
}

export interface FrozenSectionRow extends CaseRow {
  pathologist: string | null;
  priority: PriorityValue;
}

export type StatCaseRow = CaseRow;

export interface HeldCaseRow extends CaseRow {
  hold_type: HoldType;
  hold_reasons: string[];
}

// ---------------------------------------------------------------------------
// Form-level data (page 2)
// ---------------------------------------------------------------------------

export interface FormData {
  client_requests: ClientRequestRow[];
  bone_marrow: BoneMarrowRow[];
  frozen_section: FrozenSectionRow[];
  stat_cases: StatCaseRow[];
  held_cases: HeldCaseRow[];
}

// ---------------------------------------------------------------------------
// Root application state
// ---------------------------------------------------------------------------

export interface AppState {
  selected_types: Set<SectionKey>;
  form_data: FormData;
  notes: string;
  accessioned: AccessionedValue;
}

// ---------------------------------------------------------------------------
// Error maps (passed to CaseRowTable via sections)
// ---------------------------------------------------------------------------

/** { [rowIndex]: { [columnKey]: errorMessage } } */
export type RowErrors = Record<number, Record<string, string>>;

/** { [sectionKey]: RowErrors } */
export type SectionErrors = Partial<Record<SectionKey, RowErrors>>;

// ---------------------------------------------------------------------------
// CaseRowTable column definition
// ---------------------------------------------------------------------------

export type ColumnType =
  | 'case_number'
  | 'autocomplete'
  | 'priority_toggle'
  | 'toggle'
  | 'multi_select'
  | 'segment_toggle';

export interface ColumnDef {
  key: string;
  label: string;
  type: ColumnType;
  required: boolean;
  props?: Record<string, unknown>;
}

// ---------------------------------------------------------------------------
// PathologistAutocomplete
// ---------------------------------------------------------------------------

export interface MdEntry {
  last: string;
  first: string;
  middle: string | null;
  display_name: string;
}

// ---------------------------------------------------------------------------
// Window globals injected by Flask template
// ---------------------------------------------------------------------------

export interface WorkflowSession {
  sessionId: string;
  department: string;
  userId: string;
  csrfToken: string;
}

declare global {
  interface Window {
    WORKFLOW_SESSION?: WorkflowSession;
  }
}
