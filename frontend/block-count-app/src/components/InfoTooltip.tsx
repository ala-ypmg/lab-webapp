/**
 * InfoTooltip Component
 * 
 * A reusable tooltip component with an info icon that reveals tooltip content on tap/hover.
 */

import React from 'react';
import { Tooltip, IconButton } from '@mui/material';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import type { InfoTooltipProps } from '../types';

const InfoTooltip: React.FC<InfoTooltipProps> = ({ title }) => {
  return (
    <Tooltip 
      title={title} 
      arrow
      enterTouchDelay={0}
      leaveTouchDelay={3000}
      placement="top"
    >
      <IconButton
        size="small"
        sx={{
          padding: '2px',
          marginLeft: '4px',
          minWidth: 'auto',
          minHeight: 'auto',
          color: 'secondary.main',
          '&:hover': {
            backgroundColor: 'transparent',
            color: 'primary.main',
          },
        }}
        aria-label="More information"
      >
        <InfoOutlinedIcon sx={{ fontSize: 16 }} />
      </IconButton>
    </Tooltip>
  );
};

export default InfoTooltip;
