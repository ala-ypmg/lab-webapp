/**
 * T12 — Held Cases section
 * Columns: case_number, hold_type (segment_toggle, no default), hold_reasons (multi_select)
 */
import { Accordion, AccordionSummary, AccordionDetails, Typography, Box } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CaseRowTable, { HOLD_REASONS } from '../CaseRowTable.tsx';
import type { ColumnDef, HeldCaseRow, RowErrors } from '../../types/index.ts';

const COLUMNS: ColumnDef[] = [
  { key: 'case_number',  label: 'Case number',       type: 'case_number',    required: true },
  { key: 'hold_type',    label: 'Hold type',          type: 'segment_toggle', required: true,
    props: { options: ['Breast', 'Miscellaneous'] } },
  { key: 'hold_reasons', label: 'Reason(s) for hold', type: 'multi_select',   required: true,
    props: { options: HOLD_REASONS } },
];

interface HeldCasesProps {
  rows: HeldCaseRow[];
  onChange: (rows: HeldCaseRow[]) => void;
  errors?: RowErrors;
}

export default function HeldCases({ rows, onChange, errors }: HeldCasesProps) {
  return (
    <Accordion
      defaultExpanded={rows.length > 0}
      sx={{ '&:before': { display: 'none' }, borderLeft: '4px solid', borderColor: 'warning.main', mb: 1 }}
    >
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box display="flex" alignItems="center" gap={1.5}>
          <Typography fontWeight={600}>Held Cases</Typography>
          {rows.length > 0 && (
            <Typography variant="caption" color="text.secondary">
              {rows.length} case{rows.length !== 1 ? 's' : ''}
            </Typography>
          )}
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        <CaseRowTable
          columns={COLUMNS}
          rows={rows}
          onChange={(next) => onChange(next as HeldCaseRow[])}
          errors={errors}
        />
      </AccordionDetails>
    </Accordion>
  );
}
