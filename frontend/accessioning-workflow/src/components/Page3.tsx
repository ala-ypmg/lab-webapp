/**
 * T03 — Page 1: Case type selection
 *
 * Five checkboxes. Live count badge. "Next" blocked when nothing is selected.
 */
import {
  Box,
  Typography,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Chip,
  Paper,
} from '@mui/material';
import type { SectionKey } from '../types/index.ts';
import { useSubmitKey } from '../contexts/SubmitKeyContext.ts';
import { useShake } from '../hooks/useShake.ts';

const CASE_TYPES: { key: SectionKey; label: string }[] = [
  { key: 'client_requests', label: 'Client Requests' },
  { key: 'bone_marrow',     label: 'Bakersfield Bone Marrow Cases' },
  { key: 'frozen_section',  label: 'Frozen Section for Intraoperative Consultation' },
  { key: 'stat_cases',      label: 'STAT Cases' },
  { key: 'held_cases',      label: 'Held Cases' },
];

interface Page1Props {
  selectedTypes: Set<SectionKey>;
  onToggle: (key: SectionKey) => void;
  showValidationError: boolean;
}

export default function Page1({ selectedTypes, onToggle, showValidationError }: Page1Props) {
  const count = selectedTypes.size;
  const submitKey = useSubmitKey();
  const errorShakeClass = useShake(showValidationError && count === 0, submitKey);

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', px: 2, py: 3 }}>
      <Typography variant="h5" fontWeight={700} gutterBottom>
        Select Case Types
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={3}>
        Select all case types present in this session. Only selected types will appear on the next page.
      </Typography>

      <Paper variant="outlined" sx={{ p: 2.5 }}>
        <FormGroup>
          {CASE_TYPES.map(({ key, label }) => (
            <FormControlLabel
              key={key}
              control={
                <Checkbox
                  checked={selectedTypes.has(key)}
                  onChange={() => onToggle(key)}
                  size="medium"
                />
              }
              label={<Typography variant="body1">{label}</Typography>}
              sx={{ py: 0.5 }}
            />
          ))}
        </FormGroup>
      </Paper>

      {count > 0 && (
        <Box mt={2} display="flex" alignItems="center" gap={1}>
          <Chip
            label={`${count} type${count !== 1 ? 's' : ''} selected`}
            color="primary"
            size="small"
            variant="outlined"
          />
        </Box>
      )}

      {showValidationError && count === 0 && (
        <div className={errorShakeClass}>
          <Typography color="error" variant="body2" mt={2}>
            Please select at least one case type to continue.
          </Typography>
        </div>
      )}
    </Box>
  );
}
