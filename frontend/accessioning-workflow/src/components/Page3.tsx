/**
 * T14 — Page 3: Notes and verification
 *
 * - Free-form session notes textarea
 * - Yes/No accessioning confirmation (neither pre-selected)
 * - Advisory warning banner when "No" is selected
 */
import {
  Box,
  Typography,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Alert,
  Paper,
  FormHelperText,
} from '@mui/material';
import type { AccessionedValue } from '../types/index.ts';

interface Page3Props {
  notes: string;
  onNotesChange: (notes: string) => void;
  accessioned: AccessionedValue;
  onAccessionedChange: (value: AccessionedValue) => void;
  accessionedError?: string;
}

export default function Page3({
  notes,
  onNotesChange,
  accessioned,
  onAccessionedChange,
  accessionedError,
}: Page3Props) {
  return (
    <Box sx={{ maxWidth: 700, mx: 'auto', px: 2, py: 3 }}>
      <Typography variant="h5" fontWeight={700} gutterBottom>
        Notes &amp; Verification
      </Typography>

      {/* Session notes */}
      <Paper variant="outlined" sx={{ p: 2.5, mb: 3 }}>
        <Typography variant="subtitle1" gutterBottom>
          Session notes
        </Typography>
        <TextField
          multiline
          minRows={4}
          fullWidth
          value={notes}
          onChange={(e) => onNotesChange(e.target.value)}
          placeholder="Discrepancies, exceptions, deferred cases, or anything not captured above..."
          size="small"
        />
      </Paper>

      {/* Accessioning confirmation */}
      <Paper variant="outlined" sx={{ p: 2.5 }}>
        <Typography variant="subtitle1" gutterBottom>
          All cases received have been accessioned?
        </Typography>
        <ToggleButtonGroup
          value={accessioned}
          exclusive
          onChange={(_e, next: AccessionedValue) => {
            if (next !== null) onAccessionedChange(next);
          }}
          sx={{ mb: 1 }}
        >
          <ToggleButton
            value="yes"
            sx={{
              px: 3,
              fontWeight: 600,
              '&.Mui-selected': { bgcolor: 'success.light', color: 'success.contrastText' },
            }}
          >
            Yes
          </ToggleButton>
          <ToggleButton
            value="no"
            sx={{
              px: 3,
              fontWeight: 600,
              '&.Mui-selected': { bgcolor: 'error.light', color: 'error.contrastText' },
            }}
          >
            No
          </ToggleButton>
        </ToggleButtonGroup>

        {accessionedError && (
          <FormHelperText error>{accessionedError}</FormHelperText>
        )}

        {accessioned === 'no' && (
          <Alert severity="warning" sx={{ mt: 2 }}>
            Incomplete accessioning noted. Document outstanding cases in the session notes above
            before submitting.
          </Alert>
        )}
      </Paper>
    </Box>
  );
}
