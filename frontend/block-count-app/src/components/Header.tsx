/**
 * Header Component
 * 
 * Sticky header with title, subtitle, and run counter badge.
 */

import React from 'react';
import { Box, Typography, Chip } from '@mui/material';
import type { HeaderProps } from '../types';
import { colors } from '../constants/theme';

const Header: React.FC<HeaderProps> = ({ runCount }) => {
  return (
    <Box
      sx={{
        position: 'sticky',
        top: 0,
        zIndex: 100,
        backgroundColor: colors.primary,
        padding: '16px 20px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
      }}
    >
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
        }}
      >
        <Box>
          <Typography
            variant="h5"
            component="h1"
            sx={{
              fontWeight: 700,
              color: '#ffffff',
              fontSize: '20px',
              lineHeight: 1.2,
            }}
          >
            YPB Daily Count
          </Typography>
          <Typography
            variant="subtitle2"
            sx={{
              color: 'rgba(255, 255, 255, 0.85)',
              fontSize: '13px',
              mt: 0.5,
            }}
          >
            Check Out Department
          </Typography>
        </Box>
        
        <Chip
          label={`${runCount} ${runCount === 1 ? 'Run' : 'Runs'}`}
          sx={{
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            color: '#ffffff',
            fontWeight: 600,
            fontSize: '13px',
            height: 28,
            '& .MuiChip-label': {
              px: 1.5,
            },
          }}
        />
      </Box>
    </Box>
  );
};

export default Header;
