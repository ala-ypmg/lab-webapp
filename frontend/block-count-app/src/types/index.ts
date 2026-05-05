/**
 * YPB Daily Count Form - Type Definitions
 */

/**
 * Represents a single run entry in the daily count form
 */
export interface RunEntry {
  /** Unique identifier (timestamp) */
  id: number;
  /** Auto-populated facility name based on selected prefixes */
  facility: string;
  /** User-selected case prefixes */
  selectedPrefixes: string[];
  /** Number of tissue blocks (primary count) */
  blocks: string;
  /** Bone marrow case number */
  boneMarrowCase: string;
  /** Bone marrow block count */
  boneMarrowBlocks: string;
  /** Cell button specimen count */
  cellButtons: string;
  /** Autopsy block count (weekly) */
  autopsyBlocks: string;
  /** Time run completed (HH:MM) */
  checkoutTime: string;
  /** UI state for collapse/expand */
  collapsed: boolean;
}

/**
 * Represents the overall form state
 */
export interface FormState {
  /** ISO date string (YYYY-MM-DD) */
  date: string;
  /** Array of run entries */
  entries: RunEntry[];
}

/**
 * Calculated totals across all runs
 */
export interface Totals {
  /** Sum of all entry.blocks */
  blocks: number;
  /** Sum of all entry.boneMarrowBlocks */
  bm: number;
  /** Sum of all entry.autopsyBlocks */
  autopsy: number;
  /** Sum of all entry.cellButtons */
  cells: number;
  /** Grand total: blocks + bm + autopsy + cells */
  total: number;
}

/**
 * Mapping of facility names to their associated prefixes
 */
export interface FacilityPrefixMap {
  [facility: string]: string[];
}

/**
 * Mapping of prefixes to their facility
 */
export interface PrefixToFacilityMap {
  [prefix: string]: string;
}

/**
 * Props for RunEntry component
 */
export interface RunEntryProps {
  /** The run entry data */
  entry: RunEntry;
  /** Index of the run (0-based) */
  index: number;
  /** Total number of runs */
  totalRuns: number;
  /** Callback when entry is updated */
  onUpdate: (id: number, updates: Partial<RunEntry>) => void;
  /** Callback when entry is deleted */
  onDelete: (id: number) => void;
  /** Callback when collapse is toggled */
  onToggleCollapse: (id: number) => void;
}

/**
 * Props for InputField component
 */
export interface InputFieldProps {
  /** Field label */
  label: string;
  /** Field value */
  value: string;
  /** Callback when value changes */
  onChange: (value: string) => void;
  /** Input type */
  type?: 'text' | 'number' | 'time';
  /** Tooltip text */
  tooltip?: string;
  /** Placeholder text */
  placeholder?: string;
  /** Whether field is required */
  required?: boolean;
  /** Additional styling */
  sx?: Record<string, unknown>;
}

/**
 * Props for PrefixChip component
 */
export interface PrefixChipProps {
  /** Prefix label */
  label: string;
  /** Whether chip is selected */
  selected: boolean;
  /** Click handler */
  onClick: () => void;
}

/**
 * Props for InfoTooltip component
 */
export interface InfoTooltipProps {
  /** Tooltip content */
  title: string;
}

/**
 * Props for TotalsDisplay component
 */
export interface TotalsDisplayProps {
  /** Calculated totals */
  totals: Totals;
}

/**
 * Props for Header component
 */
export interface HeaderProps {
  /** Number of runs */
  runCount: number;
  /** Clear session handler */
  onClearSession: () => void;
  /** Change department handler */
  onChangeDepartment: () => void;
}

/**
 * Props for Footer component
 */
export interface FooterProps {
  /** Calculated totals */
  totals: Totals;
  /** Save button handler */
  onSave: () => void;
  /** Whether save is in progress */
  isSaving?: boolean;
  /** Navigate back to login page */
  onBackToLogin?: () => void;
  /** Navigate to Workflow page */
  onGoToWorkflow?: () => void;
  /** Navigate to Notes page */
  onGoToNotes?: () => void;
  /** Logout handler */
  onLogout?: () => void;
}

/**
 * Props for BoneMarrowSection component
 */
export interface BoneMarrowSectionProps {
  /** Bone marrow case number */
  caseNumber: string;
  /** Bone marrow block count */
  blocks: string;
  /** Callback when case number changes */
  onCaseChange: (value: string) => void;
  /** Callback when blocks changes */
  onBlocksChange: (value: string) => void;
}

/**
 * Props for AutopsyAccordion component
 */
export interface AutopsyAccordionProps {
  /** Autopsy blocks value */
  value: string;
  /** Callback when value changes */
  onChange: (value: string) => void;
}

/**
 * Create an empty run entry with defaults
 */
export const createEmptyRunEntry = (): RunEntry => ({
  id: Date.now(),
  facility: '',
  selectedPrefixes: [],
  blocks: '',
  boneMarrowCase: '',
  boneMarrowBlocks: '',
  cellButtons: '',
  autopsyBlocks: '',
  checkoutTime: '',
  collapsed: false,
});
