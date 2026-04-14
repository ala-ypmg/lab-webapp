/**
 * T15 — Success screen shown after a clean submission.
 */
import { useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import confetti from 'canvas-confetti';
import type { FormData, SectionKey } from '../types/index.ts';

const SECTION_LABELS: Record<SectionKey, string> = {
  client_requests: 'Client Requests',
  bone_marrow: 'Bakersfield Bone Marrow Cases',
  frozen_section: 'Frozen Section for Intraoperative Consultation',
  stat_cases: 'STAT Cases',
  held_cases: 'Held Cases',
};

const SECTION_ORDER: SectionKey[] = [
  'client_requests',
  'bone_marrow',
  'frozen_section',
  'stat_cases',
  'held_cases',
];

function formatTimestamp(d: Date): string {
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

interface SuccessScreenProps {
  submittedAt: Date;
  submittedTypes: Set<SectionKey>;
  formData: FormData;
  onReset: () => void;
}

export default function SuccessScreen({
  submittedAt,
  submittedTypes,
  formData,
  onReset,
}: SuccessScreenProps) {
  useEffect(() => {
    function randomInRange(min: number, max: number) {
      return Math.random() * (max - min) + min;
    }
    confetti({
      angle: randomInRange(55, 125),
      spread: randomInRange(50, 70),
      particleCount: randomInRange(50, 100),
      origin: { y: 0.6 },
    });
  }, []);

  return (
    <Box
      sx={{
        maxWidth: 600,
        mx: 'auto',
        px: 2,
        py: 6,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
      }}
    >
      <CheckCircleIcon sx={{ fontSize: 72, color: 'success.main', mb: 2 }} />

      <Typography variant="h5" fontWeight={700} gutterBottom>
        Accessioning session submitted
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={3}>
        {formatTimestamp(submittedAt)}
      </Typography>

      <Paper variant="outlined" sx={{ width: '100%', mb: 4, textAlign: 'left' }}>
        <List dense disablePadding>
          {SECTION_ORDER.filter((k) => submittedTypes.has(k)).map((key, i, arr) => {
            const count = formData[key].length;
            return (
              <Box key={key}>
                <ListItem>
                  <ListItemText
                    primary={SECTION_LABELS[key]}
                    secondary={`${count} case${count !== 1 ? 's' : ''}`}
                    primaryTypographyProps={{ fontWeight: 500 }}
                  />
                </ListItem>
                {i < arr.length - 1 && <Divider />}
              </Box>
            );
          })}
        </List>
      </Paper>

      <Button variant="contained" size="large" onClick={onReset}>
        Start new session
      </Button>
    </Box>
  );
}
