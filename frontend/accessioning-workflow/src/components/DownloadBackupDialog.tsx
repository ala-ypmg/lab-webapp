/**
 * Shown when a submission fails due to a DB connection error (503) or a
 * network failure.  Lets the user download their session data as JSON or
 * plain text so nothing is lost while the database is unavailable.
 */
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  Stack,
  Typography,
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import type { AppState, SectionKey } from '../types/index.ts';

// ---------------------------------------------------------------------------
// Shared metadata
// ---------------------------------------------------------------------------

const SECTION_LABELS: Record<SectionKey, string> = {
  client_requests:  'Client Requests',
  bone_marrow:      'Bakersfield Bone Marrow Cases',
  frozen_section:   'Frozen Section for Intraoperative Consultation',
  stat_cases:       'STAT Cases',
  held_cases:       'Held Cases',
};

const SECTION_ORDER: SectionKey[] = [
  'client_requests',
  'bone_marrow',
  'frozen_section',
  'stat_cases',
  'held_cases',
];

function pad(n: number) { return String(n).padStart(2, '0'); }

function formatTimestamp(d: Date): string {
  return (
    `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ` +
    `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
  );
}

function filenameTimestamp(d: Date): string {
  return (
    `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}_` +
    `${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`
  );
}

// ---------------------------------------------------------------------------
// Plain-text formatter
// ---------------------------------------------------------------------------

function buildPlainText(state: AppState, generatedAt: Date): string {
  const session = window.WORKFLOW_SESSION;
  const lines: string[] = [];

  const banner = 'ACCESSIONING END-OF-SHIFT REPORT (OFFLINE BACKUP)';
  lines.push(banner);
  lines.push('='.repeat(banner.length));
  lines.push(`Generated : ${formatTimestamp(generatedAt)}`);
  if (session) {
    lines.push(`User ID   : ${session.userId}`);
    lines.push(`Department: ${session.department}`);
  }
  lines.push('');

  const activeTypes = SECTION_ORDER.filter((k) => state.selected_types.has(k));
  lines.push('SELECTED CASE TYPES');
  lines.push('-'.repeat(19));
  activeTypes.forEach((k) => lines.push(`  • ${SECTION_LABELS[k]}`));
  lines.push('');

  // Per-section rows
  for (const key of activeTypes) {
    const rows = state.form_data[key];
    const heading = `${SECTION_LABELS[key].toUpperCase()} (${rows.length} case${rows.length !== 1 ? 's' : ''})`;
    lines.push(heading);
    lines.push('-'.repeat(Math.min(heading.length, 60)));

    if (rows.length === 0) {
      lines.push('  (no cases entered)');
    } else {
      rows.forEach((row, i) => {
        lines.push(`  ${i + 1}. Case #: ${row.case_number || '(blank)'}`);

        const r = row as unknown as Record<string, unknown>;

        if (key === 'client_requests') {
          lines.push(`     Requested pathologist : ${r['requested_pathologist'] || '—'}`);
          lines.push(`     Send out if positive  : ${r['send_out_if_positive'] ? 'Yes' : 'No'}`);
          lines.push(`     Priority              : ${String(r['priority'] ?? '—')}`);
        } else if (key === 'bone_marrow') {
          lines.push(`     Priority              : ${String(r['priority'] ?? '—')}`);
          lines.push(`     Send out              : ${r['send_out'] ? 'Yes' : 'No'}`);
          lines.push(`     Assign pathologist    : ${r['assign_pathologist'] || '—'}`);
        } else if (key === 'frozen_section') {
          lines.push(`     Pathologist           : ${r['pathologist'] || '—'}`);
          lines.push(`     Priority              : ${String(r['priority'] ?? '—')}`);
        } else if (key === 'held_cases') {
          lines.push(`     Hold type             : ${r['hold_type'] || '—'}`);
          const reasons = Array.isArray(r['hold_reasons'])
            ? (r['hold_reasons'] as string[]).join(', ')
            : '—';
          lines.push(`     Hold reasons          : ${reasons}`);
        }
        // stat_cases: case_number only
      });
    }
    lines.push('');
  }

  // Notes
  lines.push('NOTES');
  lines.push('-'.repeat(5));
  lines.push(state.notes.trim() || '(none)');
  lines.push('');

  // Accessioning confirmation
  const accLabel =
    state.accessioned === 'yes' ? 'Yes'
    : state.accessioned === 'no' ? 'No'
    : '(not answered)';
  lines.push(`ALL CASES ACCESSIONED: ${accLabel}`);
  lines.push('');
  lines.push('--- end of backup ---');

  return lines.join('\n');
}

// ---------------------------------------------------------------------------
// JSON payload builder (strips internal React IDs, adds metadata)
// ---------------------------------------------------------------------------

function buildJSON(state: AppState, generatedAt: Date): string {
  const session = window.WORKFLOW_SESSION;

  const payload = {
    meta: {
      generated_at: formatTimestamp(generatedAt),
      user_id:      session?.userId ?? null,
      department:   session?.department ?? null,
      note:         'Offline backup — database was unavailable at time of submission.',
    },
    selected_types: [...state.selected_types],
    form_data: {
      client_requests: state.form_data.client_requests.map(
        ({ id: _id, ...r }) => r
      ),
      bone_marrow: state.form_data.bone_marrow.map(
        ({ id: _id, ...r }) => r
      ),
      frozen_section: state.form_data.frozen_section.map(
        ({ id: _id, ...r }) => r
      ),
      stat_cases: state.form_data.stat_cases.map(
        ({ id: _id, ...r }) => r
      ),
      held_cases: state.form_data.held_cases.map(
        ({ id: _id, ...r }) => r
      ),
    },
    notes:       state.notes,
    accessioned: state.accessioned,
  };

  return JSON.stringify(payload, null, 2);
}

// ---------------------------------------------------------------------------
// Download helper
// ---------------------------------------------------------------------------

function triggerDownload(content: string, filename: string, mime: string) {
  const blob = new Blob([content], { type: mime });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface DownloadBackupDialogProps {
  open: boolean;
  onClose: () => void;
  errorMessage: string;
  state: AppState;
}

export default function DownloadBackupDialog({
  open,
  onClose,
  errorMessage,
  state,
}: DownloadBackupDialogProps) {
  const now = new Date();
  const ts  = filenameTimestamp(now);
  const uid = window.WORKFLOW_SESSION?.userId ?? 'unknown';

  function downloadJSON() {
    triggerDownload(
      buildJSON(state, now),
      `accessioning_backup_${uid}_${ts}.json`,
      'application/json',
    );
  }

  function downloadText() {
    triggerDownload(
      buildPlainText(state, now),
      `accessioning_backup_${uid}_${ts}.txt`,
      'text/plain',
    );
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ fontWeight: 700 }}>
        Database Unavailable — Download Your Data
      </DialogTitle>

      <DialogContent>
        <Typography variant="body2" color="error.main" sx={{ mb: 2 }}>
          {errorMessage}
        </Typography>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Your session data has <strong>not</strong> been lost. Download a backup
          now so you can resubmit or hand it off once the connection is restored.
        </Typography>

        <Divider sx={{ my: 2 }} />

        <Typography variant="subtitle2" gutterBottom>
          Choose a format:
        </Typography>

        <Stack direction="row" spacing={2} sx={{ mt: 1 }}>
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={downloadJSON}
          >
            Download JSON
          </Button>

          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={downloadText}
          >
            Download plain text
          </Button>
        </Stack>

        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
          JSON preserves all field values for programmatic resubmission. Plain
          text is human-readable and suitable for printing or emailing.
        </Typography>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} color="inherit">
          Dismiss
        </Button>
      </DialogActions>
    </Dialog>
  );
}
