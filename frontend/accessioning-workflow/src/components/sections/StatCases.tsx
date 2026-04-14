/**
 * T08 — STAT Cases section
 * Single column: case_number only.
 */
import { Accordion, AccordionSummary, AccordionDetails, Typography, Box } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CaseRowTable, { makeBlankRow } from '../CaseRowTable.tsx';
import type { ColumnDef, StatCaseRow, RowErrors } from '../../types/index.ts';

const COLUMNS: ColumnDef[] = [
  { key: 'case_number', label: 'Case number', type: 'case_number', required: true },
];

interface StatCasesProps {
  rows: StatCaseRow[];
  onChange: (rows: StatCaseRow[]) => void;
  errors?: RowErrors;
}

export default function StatCases({ rows, onChange, errors }: StatCasesProps) {
  return (
    <Accordion
      defaultExpanded={rows.length > 0}
      sx={{ '&:before': { display: 'none' }, borderLeft: '4px solid', borderColor: 'error.main', mb: 1 }}
    >
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box display="flex" alignItems="center" gap={1.5}>
          <Typography fontWeight={600}>STAT Cases</Typography>
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
          onChange={(next) => onChange(next as StatCaseRow[])}
          errors={errors}
        />
      </AccordionDetails>
    </Accordion>
  );
}

export { makeBlankRow, COLUMNS as STAT_COLUMNS };
