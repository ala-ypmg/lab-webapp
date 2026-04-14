/**
 * T07 — PasteBulkDialog
 *
 * Modal triggered by "Paste Bulk" in any CaseRowTable toolbar.
 * Accepts multi-line / comma-separated case numbers, validates each,
 * and appends valid entries to the parent table.
 */
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Chip,
  Stack,
  Divider,
} from '@mui/material';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import CancelOutlinedIcon from '@mui/icons-material/CancelOutlined';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import { useState, useCallback } from 'react';
import { validateCaseNumber } from '../utils/caseNumber.ts';

interface ParsedEntry {
  raw: string;
  lineIndex: number;
  state: 'valid' | 'invalid' | 'duplicate';
  normalized?: string;
  error?: string;
}

interface PasteBulkDialogProps {
  open: boolean;
  onClose: () => void;
  onAdd: (normalizedCaseNumbers: string[]) => void;
  existingCaseNumbers: string[];
}

function parseEntries(text: string, existing: string[]): ParsedEntry[] {
  // Split on newlines and/or commas
  const tokens = text
    .split(/[\n,]+/)
    .map((t) => t.trim())
    .filter(Boolean);

  const existingSet = new Set(existing.map((n) => n.toUpperCase()));

  return tokens.map((raw, i) => {
    const result = validateCaseNumber(raw);
    if (!result.valid) {
      return { raw, lineIndex: i + 1, state: 'invalid' as const, error: result.error };
    }
    if (existingSet.has(result.normalized)) {
      return { raw, lineIndex: i + 1, state: 'duplicate' as const, normalized: result.normalized };
    }
    return { raw, lineIndex: i + 1, state: 'valid' as const, normalized: result.normalized };
  });
}

export default function PasteBulkDialog({
  open,
  onClose,
  onAdd,
  existingCaseNumbers,
}: PasteBulkDialogProps) {
  const [text, setText] = useState('');
  const [parsed, setParsed] = useState<ParsedEntry[] | null>(null);

  const handleParse = useCallback(() => {
    setParsed(parseEntries(text, existingCaseNumbers));
  }, [text, existingCaseNumbers]);

  const handleBlur = () => {
    if (text.trim()) handleParse();
  };

  const validEntries = parsed?.filter((e) => e.state === 'valid' || e.state === 'duplicate') ?? [];
  const invalidEntries = parsed?.filter((e) => e.state === 'invalid') ?? [];

  const handleAdd = () => {
    const normalized = validEntries.map((e) => e.normalized!);
    onAdd(normalized);

    // Keep only invalid lines in textarea
    const invalidLines = invalidEntries.map((e) => e.raw).join('\n');
    setText(invalidLines);
    setParsed(invalidLines ? parseEntries(invalidLines, existingCaseNumbers) : null);

    if (invalidEntries.length === 0) {
      onClose();
    }
  };

  const handleClose = () => {
    setText('');
    setParsed(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Paste Bulk Case Numbers</DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary" mb={1.5}>
          Enter case numbers one per line or comma-separated.
        </Typography>
        <TextField
          multiline
          rows={6}
          fullWidth
          value={text}
          onChange={(e) => {
            setText(e.target.value);
            setParsed(null);
          }}
          onBlur={handleBlur}
          placeholder={'26CRN-40013\n26KAA-01200\n25RR-15616'}
          size="small"
          inputProps={{ style: { fontFamily: 'monospace' } }}
        />
        <Box mt={1}>
          <Button size="small" variant="outlined" onClick={handleParse} disabled={!text.trim()}>
            Parse
          </Button>
        </Box>

        {parsed && parsed.length > 0 && (
          <Box mt={2}>
            <Divider sx={{ mb: 1.5 }} />
            <Stack spacing={0.75}>
              {parsed.map((entry, idx) => (
                <Box key={idx} display="flex" alignItems="flex-start" gap={1}>
                  {entry.state === 'valid' && (
                    <CheckCircleOutlineIcon color="success" fontSize="small" sx={{ mt: 0.2 }} />
                  )}
                  {entry.state === 'invalid' && (
                    <CancelOutlinedIcon color="error" fontSize="small" sx={{ mt: 0.2 }} />
                  )}
                  {entry.state === 'duplicate' && (
                    <WarningAmberIcon color="warning" fontSize="small" sx={{ mt: 0.2 }} />
                  )}
                  <Box>
                    <Typography variant="body2" component="span" fontWeight={500}>
                      {entry.state === 'valid' || entry.state === 'duplicate'
                        ? entry.normalized
                        : entry.raw}
                    </Typography>
                    {entry.state === 'invalid' && (
                      <Typography variant="caption" color="error" display="block">
                        Line {entry.lineIndex}: {entry.error}
                      </Typography>
                    )}
                    {entry.state === 'duplicate' && (
                      <Typography variant="caption" color="warning.dark" display="block">
                        Already in table — will be added anyway
                      </Typography>
                    )}
                  </Box>
                </Box>
              ))}
            </Stack>
            <Box mt={1.5} display="flex" gap={1} alignItems="center">
              {validEntries.length > 0 && (
                <Chip
                  label={`${validEntries.length} valid`}
                  color="success"
                  size="small"
                  variant="outlined"
                />
              )}
              {invalidEntries.length > 0 && (
                <Chip
                  label={`${invalidEntries.length} invalid`}
                  color="error"
                  size="small"
                  variant="outlined"
                />
              )}
            </Box>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          variant="contained"
          onClick={handleAdd}
          disabled={validEntries.length === 0}
        >
          Add to table ({validEntries.length})
        </Button>
      </DialogActions>
    </Dialog>
  );
}
