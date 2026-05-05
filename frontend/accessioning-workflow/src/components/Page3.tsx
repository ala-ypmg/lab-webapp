/**
 * T14 — Page 3: Notes and verification
 *
 * - Free-form session notes textarea
 * - Yes/No accessioning confirmation (neither pre-selected)
 * - Advisory warning banner when "No" is selected
 */
import { useState } from 'react';
import { useSubmitKey } from '../contexts/SubmitKeyContext.ts';
import { useShake } from '../hooks/useShake.ts';
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
  notesError?: string;
  accessioned: AccessionedValue;
  onAccessionedChange: (value: AccessionedValue) => void;
  accessionedError?: string;
}

export default function Page3({
  notes,
  onNotesChange,
  notesError,
  accessioned,
  onAccessionedChange,
  accessionedError,
}: Page3Props) {
  const [phiBannerDismissed, setPhiBannerDismissed] = useState(false);
  const submitKey = useSubmitKey();
  const notesShakeClass = useShake(!!notesError, submitKey);
  const accessionedShakeClass = useShake(!!accessionedError, submitKey);

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
        {!phiBannerDismissed && (
          <Alert severity="info" onClose={() => setPhiBannerDismissed(true)} sx={{ mb: 1.5 }}>
            Do not include case numbers and other PHI in your notes!
          </Alert>
        )}
        <div className={notesShakeClass}>
          <TextField
            multiline
            minRows={4}
            fullWidth
            value={notes}
            onChange={(e) => onNotesChange(e.target.value)}
            placeholder="Discrepancies, exceptions, deferred cases, or anything not captured above..."
            size="small"
            error={!!notesError}
            helperText={notesError}
          />
        </div>
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
          <div className={accessionedShakeClass}>
            <FormHelperText error>{accessionedError}</FormHelperText>
          </div>
        )}

        {accessioned === 'no' && (
          <Alert severity="warning" sx={{ mt: 2 }}>
            Please indicate how many specimens are not yet accessioned. Do not include case numbers
            and other PHI.
          </Alert>
        )}
      </Paper>
    </Box>
  );
}
