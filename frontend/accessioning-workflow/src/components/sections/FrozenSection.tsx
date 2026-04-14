/**
 * T11 — Frozen Section for Intraoperative Consultation
 * Columns: case_number, pathologist (all MDs, no free-text), priority
 */
import { Accordion, AccordionSummary, AccordionDetails, Typography, Box } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CaseRowTable from '../CaseRowTable.tsx';
import type { ColumnDef, FrozenSectionRow, RowErrors } from '../../types/index.ts';

const COLUMNS: ColumnDef[] = [
  { key: 'case_number', label: 'Case number',                         type: 'case_number',    required: true },
  { key: 'pathologist', label: 'Pathologist who performed frozen section', type: 'autocomplete', required: false, props: { source: 'all', allowFreetext: false } },
  { key: 'priority',    label: 'Priority',                             type: 'priority_toggle', required: false },
];

interface FrozenSectionProps {
  rows: FrozenSectionRow[];
  onChange: (rows: FrozenSectionRow[]) => void;
  errors?: RowErrors;
}

export default function FrozenSection({ rows, onChange, errors }: FrozenSectionProps) {
  return (
    <Accordion
      defaultExpanded={rows.length > 0}
      sx={{ '&:before': { display: 'none' }, borderLeft: '4px solid', borderColor: 'info.main', mb: 1 }}
    >
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box display="flex" alignItems="center" gap={1.5}>
          <Typography fontWeight={600}>Frozen Section for Intraoperative Consultation</Typography>
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
          onChange={(next) => onChange(next as FrozenSectionRow[])}
          errors={errors}
        />
      </AccordionDetails>
    </Accordion>
  );
}
