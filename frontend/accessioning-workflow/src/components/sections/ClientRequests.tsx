/**
 * T09 — Client Requests section
 * Columns: case_number, requested_pathologist (all MDs, free-text),
 *          send_out_if_positive (toggle), priority
 */
import { Accordion, AccordionSummary, AccordionDetails, Typography, Box } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CaseRowTable from '../CaseRowTable.tsx';
import type { ColumnDef, ClientRequestRow, RowErrors } from '../../types/index.ts';

const COLUMNS: ColumnDef[] = [
  { key: 'case_number',           label: 'Case number',          type: 'case_number',    required: true },
  { key: 'requested_pathologist', label: 'Requested pathologist', type: 'autocomplete',   required: false, props: { source: 'all', allowFreetext: true } },
  { key: 'send_out_if_positive',  label: 'Send out if positive',  type: 'toggle',         required: false },
  { key: 'priority',              label: 'Priority',              type: 'priority_toggle', required: false },
];

interface ClientRequestsProps {
  rows: ClientRequestRow[];
  onChange: (rows: ClientRequestRow[]) => void;
  errors?: RowErrors;
}

export default function ClientRequests({ rows, onChange, errors }: ClientRequestsProps) {
  return (
    <Accordion
      defaultExpanded={rows.length > 0}
      sx={{ '&:before': { display: 'none' }, borderLeft: '4px solid', borderColor: 'primary.main', mb: 1 }}
    >
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box display="flex" alignItems="center" gap={1.5}>
          <Typography fontWeight={600}>Client Requests</Typography>
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
          onChange={(next) => onChange(next as ClientRequestRow[])}
          errors={errors}
        />
      </AccordionDetails>
    </Accordion>
  );
}
