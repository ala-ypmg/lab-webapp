/**
 * T06 — CaseRowTable
 *
 * Generic dynamic row table. Driven by a `columns` prop.
 * Renders each column type by switching on `ColumnDef.type`.
 * Supports inline error display, delete confirmation, and PasteBulkDialog.
 */
import {
  Box,
  Button,
  IconButton,
  Typography,
  TextField,
  Switch,
  FormControlLabel,
  FormHelperText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  ToggleButton,
  ToggleButtonGroup,
  Checkbox,
  FormGroup,
  FormControl,
  FormLabel,
  Tooltip,
  Paper,
  Stack,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import ContentPasteIcon from '@mui/icons-material/ContentPaste';
import { useState, useCallback } from 'react';
import type { ColumnDef, CaseRow, RowErrors } from '../types/index.ts';
import { validateCaseNumber } from '../utils/caseNumber.ts';
import PriorityToggle from './PriorityToggle.tsx';
import PathologistAutocomplete from './PathologistAutocomplete.tsx';
import PasteBulkDialog from './PasteBulkDialog.tsx';
import type { PriorityValue } from '../types/index.ts';

// Hold reasons used by HeldCases section
export const HOLD_REASONS = [
  'Fixation',
  'Pending additional tissue',
  'Client verification',
  'Grossing verification',
  'OR verification',
  'Adequacy evaluation',
  'Decalcification',
  'Split cytology case',
];

function isRowBlank(row: CaseRow): boolean {
  return Object.entries(row).every(([key, val]) => {
    if (key === 'id') return true;
    if (val === '' || val === null || val === false) return true;
    if (Array.isArray(val) && val.length === 0) return true;
    if (val === 'routine') return true; // default priority
    return false;
  });
}

interface CaseRowTableProps {
  columns: ColumnDef[];
  rows: CaseRow[];
  onChange: (rows: CaseRow[]) => void;
  errors?: RowErrors;
  /** Override to handle send_out→pathologist mutual exclusivity from outside */
  renderRowExtra?: (row: CaseRow, rowIndex: number) => React.ReactNode;
}

export function makeBlankRow(columns: ColumnDef[]): CaseRow {
  const row: { id: string; case_number: string; [key: string]: unknown } = {
    id: crypto.randomUUID(),
    case_number: '',
  };
  for (const col of columns) {
    if (col.key === 'id' || col.key === 'case_number') continue;
    switch (col.type) {
      case 'priority_toggle':
        row[col.key] = 'routine';
        break;
      case 'toggle':
        row[col.key] = false;
        break;
      case 'autocomplete':
        row[col.key] = null;
        break;
      case 'multi_select':
        row[col.key] = [];
        break;
      case 'segment_toggle':
        row[col.key] = null;
        break;
      default:
        row[col.key] = '';
    }
  }
  return row;
}

// ---------------------------------------------------------------------------
// Sub-components for each cell type (hooks used at top-level per component)
// ---------------------------------------------------------------------------

interface CaseNumberCellProps {
  colKey: string;
  rowIndex: number;
  initialValue: string;
  externalError?: string;
  onFieldChange: (rowIndex: number, key: string, value: unknown) => void;
}

function CaseNumberCell({ colKey, rowIndex, initialValue, externalError, onFieldChange }: CaseNumberCellProps) {
  const [localVal, setLocalVal] = useState(initialValue);
  const [localErr, setLocalErr] = useState('');

  const handleBlur = () => {
    if (!localVal) {
      setLocalErr('');
      onFieldChange(rowIndex, colKey, '');
      return;
    }
    const result = validateCaseNumber(localVal);
    if (result.valid) {
      setLocalErr('');
      setLocalVal(result.normalized);
      onFieldChange(rowIndex, colKey, result.normalized);
    } else {
      setLocalErr(result.error);
      onFieldChange(rowIndex, colKey, localVal);
    }
  };

  const displayErr = localErr || externalError;
  return (
    <Box>
      <TextField
        size="small"
        value={localVal}
        onChange={(e) => setLocalVal(e.target.value)}
        onBlur={handleBlur}
        placeholder="26XX-00000"
        error={!!displayErr}
        inputProps={{ style: { fontFamily: 'monospace', minWidth: 130 } }}
        sx={{ minWidth: 150 }}
      />
      {displayErr && (
        <FormHelperText error sx={{ mx: 0 }}>
          {displayErr}
        </FormHelperText>
      )}
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Unified cell dispatcher
// ---------------------------------------------------------------------------

interface CellProps {
  col: ColumnDef;
  row: CaseRow;
  rowIndex: number;
  error?: string;
  onFieldChange: (rowIndex: number, key: string, value: unknown) => void;
}

function CaseCell({ col, row, rowIndex, error, onFieldChange }: CellProps) {
  const val = (row as unknown as Record<string, unknown>)[col.key];
  const colProps = col.props ?? {};

  if (col.type === 'case_number') {
    return (
      <CaseNumberCell
        colKey={col.key}
        rowIndex={rowIndex}
        initialValue={String(val ?? '')}
        externalError={error}
        onFieldChange={onFieldChange}
      />
    );
  }

  if (col.type === 'autocomplete') {
    return (
      <PathologistAutocomplete
        source={(colProps['source'] as 'all' | 'bone_marrow') ?? 'all'}
        allowFreetext={(colProps['allowFreetext'] as boolean) ?? false}
        value={(val as string | null) ?? null}
        onChange={(v) => onFieldChange(rowIndex, col.key, v)}
        disabled={(colProps['disabled'] as boolean) ?? false}
        label={col.label}
        error={!!error}
        helperText={error}
      />
    );
  }

  if (col.type === 'priority_toggle') {
    return (
      <PriorityToggle
        value={(val as PriorityValue) ?? 'routine'}
        onChange={(v) => onFieldChange(rowIndex, col.key, v)}
      />
    );
  }

  if (col.type === 'toggle') {
    return (
      <FormControlLabel
        control={
          <Switch
            checked={Boolean(val)}
            onChange={(e) => onFieldChange(rowIndex, col.key, e.target.checked)}
            size="small"
          />
        }
        label={Boolean(val) ? 'On' : 'Off'}
        sx={{ ml: 0 }}
      />
    );
  }

  if (col.type === 'segment_toggle') {
    const options = (colProps['options'] as string[]) ?? ['Breast', 'Miscellaneous'];
    return (
      <Box>
        <ToggleButtonGroup
          value={val ?? null}
          exclusive
          onChange={(_e, next) => {
            if (next !== null) onFieldChange(rowIndex, col.key, next);
          }}
          size="small"
        >
          {options.map((opt) => (
            <ToggleButton
              key={opt}
              value={opt.toLowerCase()}
              sx={{ px: 1.5, py: 0.5, fontSize: '0.75rem', textTransform: 'none' }}
            >
              {opt}
            </ToggleButton>
          ))}
        </ToggleButtonGroup>
        {error && (
          <FormHelperText error sx={{ mx: 0 }}>
            {error}
          </FormHelperText>
        )}
      </Box>
    );
  }

  if (col.type === 'multi_select') {
    const selected = (val as string[]) ?? [];
    const options = (colProps['options'] as string[]) ?? HOLD_REASONS;
    return (
      <FormControl error={!!error} component="fieldset">
        <FormLabel component="legend" sx={{ fontSize: '0.75rem', mb: 0.5 }}>
          {col.label}
        </FormLabel>
        <FormGroup row sx={{ gap: 0.5 }}>
          {options.map((opt) => (
            <FormControlLabel
              key={opt}
              control={
                <Checkbox
                  checked={selected.includes(opt)}
                  onChange={(e) => {
                    const next = e.target.checked
                      ? [...selected, opt]
                      : selected.filter((s) => s !== opt);
                    onFieldChange(rowIndex, col.key, next);
                  }}
                  size="small"
                />
              }
              label={<Typography variant="caption">{opt}</Typography>}
              sx={{ m: 0 }}
            />
          ))}
        </FormGroup>
        {error && <FormHelperText>{error}</FormHelperText>}
      </FormControl>
    );
  }

  return null;
}

export default function CaseRowTable({ columns, rows, onChange, errors = {} }: CaseRowTableProps) {
  const [deleteIdx, setDeleteIdx] = useState<number | null>(null);
  const [bulkOpen, setBulkOpen] = useState(false);

  const handleAdd = useCallback(() => {
    onChange([...rows, makeBlankRow(columns)]);
  }, [rows, columns, onChange]);

  const handleDeleteRequest = (idx: number) => {
    if (isRowBlank(rows[idx])) {
      const next = rows.filter((_, i) => i !== idx);
      onChange(next);
    } else {
      setDeleteIdx(idx);
    }
  };

  const confirmDelete = () => {
    if (deleteIdx !== null) {
      onChange(rows.filter((_, i) => i !== deleteIdx));
      setDeleteIdx(null);
    }
  };

  const handleFieldChange = useCallback(
    (rowIndex: number, key: string, value: unknown) => {
      const next = rows.map((row, i) =>
        i === rowIndex ? { ...row, [key]: value } : row
      );
      onChange(next);
    },
    [rows, onChange]
  );

  const handleBulkAdd = (normalizedCaseNumbers: string[]) => {
    const newRows = normalizedCaseNumbers.map((cn) => ({
      ...makeBlankRow(columns),
      case_number: cn,
    }));
    onChange([...rows, ...newRows]);
  };

  const existingCaseNumbers = rows.map((r) => r.case_number).filter(Boolean);

  return (
    <Box>
      {/* Toolbar */}
      <Stack direction="row" spacing={1} mb={1.5}>
        <Button
          size="small"
          variant="outlined"
          startIcon={<AddIcon />}
          onClick={handleAdd}
        >
          Add case
        </Button>
        <Button
          size="small"
          variant="outlined"
          startIcon={<ContentPasteIcon />}
          onClick={() => setBulkOpen(true)}
        >
          Paste Bulk
        </Button>
      </Stack>

      {/* Empty state */}
      {rows.length === 0 && (
        <Paper variant="outlined" sx={{ p: 2.5, textAlign: 'center', bgcolor: 'grey.50' }}>
          <Typography variant="body2" color="text.secondary">
            No cases added yet. Use + Add case or Paste Bulk to begin.
          </Typography>
        </Paper>
      )}

      {/* Rows */}
      {rows.map((row, rowIdx) => {
        const rowErr = errors[rowIdx] ?? {};
        return (
          <Paper
            key={row.id}
            variant="outlined"
            sx={{ p: 1.5, mb: 1, display: 'flex', alignItems: 'flex-start', gap: 2, flexWrap: 'wrap' }}
          >
            {columns.map((col) => (
              <Box key={col.key} sx={{ minWidth: 0 }}>
                {col.type !== 'multi_select' && col.type !== 'segment_toggle' && (
                  <Typography variant="caption" color="text.secondary" display="block" mb={0.5}>
                    {col.label}
                  </Typography>
                )}
                <CaseCell
                  col={col}
                  row={row}
                  rowIndex={rowIdx}
                  error={rowErr[col.key]}
                  onFieldChange={handleFieldChange}
                />
              </Box>
            ))}
            <Box ml="auto" alignSelf="center">
              <Tooltip title="Remove row">
                <IconButton
                  size="small"
                  color="error"
                  onClick={() => handleDeleteRequest(rowIdx)}
                  aria-label="delete row"
                >
                  <DeleteOutlineIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </Paper>
        );
      })}

      {/* Delete confirmation dialog */}
      <Dialog open={deleteIdx !== null} onClose={() => setDeleteIdx(null)}>
        <DialogTitle>Remove this row?</DialogTitle>
        <DialogContent>
          <Typography>This row has data entered. Remove it?</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteIdx(null)}>Cancel</Button>
          <Button color="error" variant="contained" onClick={confirmDelete}>
            Remove
          </Button>
        </DialogActions>
      </Dialog>

      {/* Paste bulk dialog */}
      <PasteBulkDialog
        open={bulkOpen}
        onClose={() => setBulkOpen(false)}
        onAdd={handleBulkAdd}
        existingCaseNumbers={existingCaseNumbers}
      />
    </Box>
  );
}
