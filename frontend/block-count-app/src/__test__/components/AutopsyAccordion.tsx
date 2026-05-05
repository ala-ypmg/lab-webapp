/**
 * AutopsyAccordion Component
 * 
 * A styled card section for autopsy block entry, matching the Bone Marrow
 * card styling with a dark navy header bar and light blue content area.
 */

import React from 'react';
import { Box, Card, Typography } from '@mui/material';
import InputField from './InputField';
import InfoTooltip from './InfoTooltip';
import type { AutopsyAccordionProps } from '../types';
import { TOOLTIPS } from '../constants/tooltips';
import { colors } from '../constants/theme';

const AutopsyAccordion: React.FC<AutopsyAccordionProps> = ({
  value,
  onChange,
}) => {
  return (
    <Card
      sx={{
        backgroundColor: 'rgba(0, 131, 143, 0.04)',
        border: `1px solid ${colors.primaryLight}`,
        borderRadius: '12px',
        boxShadow: 'none',
        overflow: 'hidden',
      }}
    >
      <Box
        sx={{
          backgroundColor: colors.primary,
          padding: '8px 16px',
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <Typography
          variant="subtitle2"
          sx={{
            color: '#ffffff',
            fontWeight: 600,
            fontSize: '14px',
          }}
        >
          Autopsy Blocks
        </Typography>
        <InfoTooltip title={TOOLTIPS.autopsyBlocks} />
      </Box>

      <Box
        sx={{
          padding: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
        }}
      >
        <InputField
          label="# of Autopsy Blocks"
          value={value}
          onChange={onChange}
          type="number"
          placeholder="0"
        />
        <Typography
          variant="caption"
          sx={{
            display: 'block',
            color: 'text.secondary',
            fontStyle: 'italic',
          }}
        >
          Typically recorded weekly
        </Typography>
      </Box>
    </Card>
  );
};

export default AutopsyAccordion;
