/**
 * T05 — PriorityToggle
 *
 * A segmented toggle (mutually exclusive) for Routine / Priority / STAT.
 * Pure UI primitive — no business logic.
 */
import { ToggleButton, ToggleButtonGroup } from '@mui/material';
import type { PriorityValue } from '../types/index.ts';

interface PriorityToggleProps {
  value: PriorityValue;
  onChange: (value: PriorityValue) => void;
  disabled?: boolean;
}

const OPTIONS: { value: PriorityValue; label: string }[] = [
  { value: 'routine', label: 'Routine' },
  { value: 'priority', label: 'Priority' },
  { value: 'stat', label: 'STAT' },
];

export default function PriorityToggle({ value, onChange, disabled = false }: PriorityToggleProps) {
  return (
    <ToggleButtonGroup
      value={value}
      exclusive
      onChange={(_e, next: PriorityValue | null) => {
        if (next !== null) onChange(next);
      }}
      size="small"
      disabled={disabled}
      sx={{ flexWrap: 'nowrap' }}
    >
      {OPTIONS.map((opt) => (
        <ToggleButton
          key={opt.value}
          value={opt.value}
          sx={{
            px: 1.5,
            py: 0.5,
            fontSize: '0.75rem',
            fontWeight: 500,
            whiteSpace: 'nowrap',
          }}
        >
          {opt.label}
        </ToggleButton>
      ))}
    </ToggleButtonGroup>
  );
}
