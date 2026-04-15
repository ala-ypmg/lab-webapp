/**
 * TotalsDisplay Component
 * 
 * Displays running totals in columns: Blocks | BM | Autopsy | Cells | Total
 */

import React from 'react';
import { Box, Typography } from '@mui/material';
import type { TotalsDisplayProps } from '../types';
import { colors } from '../constants/theme';
import { formatNumber } from '../utils';

interface TotalItemProps {
  label: string;
  value: number;
  isTotal?: boolean;
}

const TotalItem: React.FC<TotalItemProps> = ({ label, value, isTotal = false }) => (
  <Box
    sx={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      flex: 1,
      minWidth: 0,
      backgroundColor: isTotal ? colors.primaryLight : '#e8eaeb',
      borderRadius: '6px',
      py: 1.5,
      px: 0.5,
    }}
  >
    <Typography
      variant="caption"
      sx={{
        color: isTotal ? colors.primaryDark : colors.text.secondary,
        fontSize: '10px',
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '0.5px',
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        maxWidth: '100%',
      }}
    >
      {label}
    </Typography>
    <Typography
      variant="h6"
      sx={{
        color: isTotal ? colors.primaryDark : colors.text.primary,
        fontWeight: isTotal ? 700 : 600,
        fontSize: isTotal ? '22px' : '18px',
        lineHeight: 1.2,
        mt: 0.5,
      }}
    >
      {formatNumber(value)}
    </Typography>
  </Box>
);

const TotalsDisplay: React.FC<TotalsDisplayProps> = ({ totals }) => {
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'stretch',
        gap: 1,
      }}
    >
      <TotalItem label="Blocks" value={totals.blocks} />
      <TotalItem label="BM" value={totals.bm} />
      <TotalItem label="Autopsy" value={totals.autopsy} />
      <TotalItem label="Cells" value={totals.cells} />
      <TotalItem label="Total" value={totals.total} isTotal />
    </Box>
  );
};

export default TotalsDisplay;
