/**
 * BoneMarrowSection Component
 * 
 * A highlighted card section for bone marrow case entry fields.
 */

import React from 'react';
import { Box, Card, Typography } from '@mui/material';
import InputField from './InputField';
import InfoTooltip from './InfoTooltip';
import type { BoneMarrowSectionProps } from '../types';
import { TOOLTIPS } from '../constants/tooltips';
import { colors } from '../constants/theme';

const BoneMarrowSection: React.FC<BoneMarrowSectionProps> = ({
  caseNumber,
  blocks,
  onCaseChange,
  onBlocksChange,
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
          Bone Marrow
        </Typography>
        <InfoTooltip title="Bone marrow case information for this run" />
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
          label="Case #"
          value={caseNumber}
          onChange={onCaseChange}
          type="text"
          placeholder="Enter case number"
          tooltip={TOOLTIPS.boneMarrowCase}
        />
        
        <InputField
          label="# of Blocks"
          value={blocks}
          onChange={onBlocksChange}
          type="number"
          placeholder="0"
          tooltip={TOOLTIPS.boneMarrowBlocks}
        />
      </Box>
    </Card>
  );
};

export default BoneMarrowSection;
