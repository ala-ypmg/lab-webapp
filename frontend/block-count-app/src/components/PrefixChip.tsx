/**
 * PrefixChip Component
 * 
 * A toggleable chip for prefix selection with proper touch targets.
 */

import React from 'react';
import { Chip } from '@mui/material';
import CheckIcon from '@mui/icons-material/Check';
import type { PrefixChipProps } from '../types';
import { colors } from '../constants/theme';

const PrefixChip: React.FC<PrefixChipProps> = ({ label, selected, onClick }) => {
  return (
    <Chip
      label={label}
      onClick={onClick}
      icon={selected ? <CheckIcon sx={{ fontSize: 16 }} /> : undefined}
      variant={selected ? 'filled' : 'outlined'}
      sx={{
        minHeight: 36,
        minWidth: 56,
        fontSize: '14px',
        fontWeight: selected ? 600 : 400,
        borderRadius: '18px',
        transition: 'all 0.2s ease-in-out',
        backgroundColor: selected ? colors.primary : 'transparent',
        color: selected ? '#ffffff' : colors.secondary,
        borderColor: selected ? colors.primary : colors.border,
        '&:hover': {
          backgroundColor: selected ? colors.primaryLight : 'rgba(0, 131, 143, 0.08)',
          borderColor: colors.primary,
        },
        '&:focus': {
          outline: `2px solid ${colors.primaryLight}`,
          outlineOffset: 2,
        },
        '& .MuiChip-icon': {
          color: '#ffffff',
          marginLeft: '6px',
        },
      }}
      aria-pressed={selected}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
    />
  );
};

export default PrefixChip;
