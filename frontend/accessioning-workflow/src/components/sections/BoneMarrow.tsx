/**
 * T10 — Bakersfield Bone Marrow Cases section
 * Columns: case_number, priority, send_out (toggle), assign_pathologist (bone_marrow only)
 *
 * Constraint: when send_out = true, assign_pathologist is disabled and cleared.
 */
import { Accordion, AccordionSummary, AccordionDetails, Typography, Box, Paper, IconButton, Button, Tooltip, Stack } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import AddIcon from '@mui/icons-material/Add';
import ContentPasteIcon from '@mui/icons-material/ContentPaste';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import { useState, useCallback } from 'react';
import PasteBulkDialog from '../PasteBulkDialog.tsx';
import { makeBlankRow } from '../CaseRowTable.tsx';
import type { BoneMarrowRow, RowErrors, ColumnDef } from '../../types/index.ts';
import { validateCaseNumber } from '../../utils/caseNumber.ts';
import { TextField, FormHelperText, FormControlLabel, Switch } from '@mui/material';
import PathologistAutocomplete from '../PathologistAutocomplete.tsx';
import PriorityToggle from '../PriorityToggle.tsx';

const BASE_COLUMNS: ColumnDef[] = [
  { key: 'case_number',       label: 'Case number', type: 'case_number',    required: true },
  { key: 'priority',          label: 'Priority',    type: 'priority_toggle', required: false },
  { key: 'send_out',          label: 'Send out',    type: 'toggle',          required: false },
  { key: 'assign_pathologist', label: 'Assign to pathologist', type: 'autocomplete', required: false,
    props: { source: 'bone_marrow', allowFreetext: false } },
];

function blankBoneMarrowRow(): BoneMarrowRow {
  return {
    ...(makeBlankRow(BASE_COLUMNS) as BoneMarrowRow),
    priority: 'routine',
    send_out: false,
    assign_pathologist: null,
  };
}

// Inline row component that handles mutual-exclusivity logic
interface BoneMarrowRowViewProps {
  row: BoneMarrowRow;
  rowIndex: number;
  rowErr: Record<string, string>;
  onChange: (updated: BoneMarrowRow) => void;
  onDelete: () => void;
}

function BoneMarrowRowView({ row, rowIndex: _rowIndex, rowErr, onChange, onDelete }: BoneMarrowRowViewProps) {
  const [localCaseNum, setLocalCaseNum] = useState(row.case_number);
  const [caseNumErr, setCaseNumErr] = useState('');

  const handleCaseNumBlur = () => {
    if (!localCaseNum) {
      setCaseNumErr('');
      onChange({ ...row, case_number: '' });
      return;
    }
    const result = validateCaseNumber(localCaseNum);
    if (result.valid) {
      setCaseNumErr('');
      setLocalCaseNum(result.normalized);
      onChange({ ...row, case_number: result.normalized });
    } else {
      setCaseNumErr(result.error);
      onChange({ ...row, case_number: localCaseNum });
    }
  };

  const handleSendOutChange = (checked: boolean) => {
    onChange({
      ...row,
      send_out: checked,
      assign_pathologist: checked ? null : row.assign_pathologist,
    });
  };

  return (
    <Paper variant="outlined" sx={{ p: 1.5, mb: 1, display: 'flex', alignItems: 'flex-start', gap: 2, flexWrap: 'wrap' }}>
      {/* Case number */}
      <Box>
        <Typography variant="caption" color="text.secondary" display="block" mb={0.5}>Case number</Typography>
        <Box>
          <TextField
            size="small"
            value={localCaseNum}
            onChange={(e) => setLocalCaseNum(e.target.value)}
            onBlur={handleCaseNumBlur}
            placeholder="26XX-00000"
            error={!!(caseNumErr || rowErr['case_number'])}
            inputProps={{ style: { fontFamily: 'monospace' } }}
            sx={{ minWidth: 150 }}
          />
          {(caseNumErr || rowErr['case_number']) && (
            <FormHelperText error sx={{ mx: 0 }}>{caseNumErr || rowErr['case_number']}</FormHelperText>
          )}
        </Box>
      </Box>

      {/* Priority */}
      <Box>
        <Typography variant="caption" color="text.secondary" display="block" mb={0.5}>Priority</Typography>
        <PriorityToggle value={row.priority} onChange={(v) => onChange({ ...row, priority: v })} />
      </Box>

      {/* Send out toggle */}
      <Box>
        <Typography variant="caption" color="text.secondary" display="block" mb={0.5}>Send out</Typography>
        <FormControlLabel
          control={
            <Switch
              checked={row.send_out}
              onChange={(e) => handleSendOutChange(e.target.checked)}
              size="small"
            />
          }
          label={row.send_out ? 'On' : 'Off'}
          sx={{ ml: 0 }}
        />
      </Box>

      {/* Assign pathologist (disabled when send_out=true) */}
      <Box>
        <Typography variant="caption" color="text.secondary" display="block" mb={0.5}>Assign to pathologist</Typography>
        <PathologistAutocomplete
          source="bone_marrow"
          allowFreetext={false}
          value={row.send_out ? null : row.assign_pathologist}
          onChange={(v) => onChange({ ...row, assign_pathologist: v })}
          disabled={row.send_out}
          label="Pathologist"
        />
      </Box>

      <Box ml="auto" alignSelf="center">
        <Tooltip title="Remove row">
          <IconButton size="small" color="error" onClick={onDelete} aria-label="delete row">
            <DeleteOutlineIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
    </Paper>
  );
}

interface BoneMarrowProps {
  rows: BoneMarrowRow[];
  onChange: (rows: BoneMarrowRow[]) => void;
  errors?: RowErrors;
}

export default function BoneMarrow({ rows, onChange, errors = {} }: BoneMarrowProps) {
  const [bulkOpen, setBulkOpen] = useState(false);

  const handleAdd = () => onChange([...rows, blankBoneMarrowRow()]);

  const handleRowChange = useCallback(
    (idx: number, updated: BoneMarrowRow) => {
      onChange(rows.map((r, i) => (i === idx ? updated : r)));
    },
    [rows, onChange]
  );

  const handleDelete = useCallback(
    (idx: number) => {
      onChange(rows.filter((_, i) => i !== idx));
    },
    [rows, onChange]
  );

  const handleBulkAdd = (normalizedCaseNumbers: string[]) => {
    const newRows = normalizedCaseNumbers.map((cn) => ({ ...blankBoneMarrowRow(), case_number: cn }));
    onChange([...rows, ...newRows]);
  };

  const existingCaseNumbers = rows.map((r) => r.case_number).filter(Boolean);

  return (
    <Accordion
      defaultExpanded={rows.length > 0}
      sx={{ '&:before': { display: 'none' }, borderLeft: '4px solid', borderColor: 'secondary.main', mb: 1 }}
    >
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box display="flex" alignItems="center" gap={1.5}>
          <Typography fontWeight={600}>Bakersfield Bone Marrow Cases</Typography>
          {rows.length > 0 && (
            <Typography variant="caption" color="text.secondary">
              {rows.length} case{rows.length !== 1 ? 's' : ''}
            </Typography>
          )}
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        <Stack direction="row" spacing={1} mb={1.5}>
          <Button size="small" variant="outlined" startIcon={<AddIcon />} onClick={handleAdd}>Add case</Button>
          <Button size="small" variant="outlined" startIcon={<ContentPasteIcon />} onClick={() => setBulkOpen(true)}>Paste Bulk</Button>
        </Stack>

        {rows.length === 0 && (
          <Paper variant="outlined" sx={{ p: 2.5, textAlign: 'center', bgcolor: 'grey.50' }}>
            <Typography variant="body2" color="text.secondary">
              No cases added yet. Use + Add case or Paste Bulk to begin.
            </Typography>
          </Paper>
        )}

        {rows.map((row, idx) => (
          <BoneMarrowRowView
            key={row.id}
            row={row}
            rowIndex={idx}
            rowErr={errors[idx] ?? {}}
            onChange={(updated) => handleRowChange(idx, updated)}
            onDelete={() => handleDelete(idx)}
          />
        ))}

        <PasteBulkDialog
          open={bulkOpen}
          onClose={() => setBulkOpen(false)}
          onAdd={handleBulkAdd}
          existingCaseNumbers={existingCaseNumbers}
        />
      </AccordionDetails>
    </Accordion>
  );
}
