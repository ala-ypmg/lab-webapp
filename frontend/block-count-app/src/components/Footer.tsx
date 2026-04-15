/**
 * Footer Component
 *
 * Sticky footer with totals, navigation buttons, and save button.
 */

import React from 'react';
import { Box, Button, CircularProgress } from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import AssignmentIcon from '@mui/icons-material/Assignment';
import NotesIcon from '@mui/icons-material/Notes';
import LogoutIcon from '@mui/icons-material/Logout';
import TotalsDisplay from './TotalsDisplay';
import type { FooterProps } from '../types';
import { colors } from '../constants/theme';

const Footer: React.FC<FooterProps> = ({
  totals,
  onSave,
  isSaving = false,
  onBackToLogin,
  onGoToWorkflow,
  onGoToNotes,
  onLogout,
}) => {
  return (
    <Box
      sx={{
        position: 'sticky',
        bottom: 0,
        left: 0,
        right: 0,
        backgroundColor: colors.surface,
        borderTop: `1px solid ${colors.border}`,
        boxShadow: '0 -2px 8px rgba(0, 0, 0, 0.08)',
        zIndex: 100,
      }}
    >
      {/* Totals Row */}
      <Box sx={{ px: 2, pt: 2, pb: 1.5 }}>
        <TotalsDisplay totals={totals} />
      </Box>

      {/* Navigation Buttons */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          gap: 1,
          px: 2,
          pb: 1.5,
        }}
      >
        <Button
          variant="outlined"
          size="small"
          onClick={onBackToLogin}
          startIcon={<ArrowBackIcon />}
          sx={{
            flex: 1,
            fontSize: '12px',
            py: 0.75,
            borderColor: colors.border,
            color: colors.text.secondary,
            '&:hover': {
              borderColor: colors.secondary,
              backgroundColor: 'rgba(84, 110, 122, 0.04)',
            },
          }}
        >
          Login
        </Button>
        <Button
          variant="outlined"
          size="small"
          onClick={onGoToWorkflow}
          startIcon={<AssignmentIcon />}
          sx={{
            flex: 1,
            fontSize: '12px',
            py: 0.75,
            borderColor: colors.border,
            color: colors.text.secondary,
            '&:hover': {
              borderColor: colors.secondary,
              backgroundColor: 'rgba(84, 110, 122, 0.04)',
            },
          }}
        >
          Workflow
        </Button>
        <Button
          variant="outlined"
          size="small"
          onClick={onGoToNotes}
          startIcon={<NotesIcon />}
          sx={{
            flex: 1,
            fontSize: '12px',
            py: 0.75,
            borderColor: colors.border,
            color: colors.text.secondary,
            '&:hover': {
              borderColor: colors.secondary,
              backgroundColor: 'rgba(84, 110, 122, 0.04)',
            },
          }}
        >
          Notes
        </Button>
        <Button
          variant="outlined"
          size="small"
          onClick={onLogout}
          startIcon={<LogoutIcon />}
          sx={{
            flex: 1,
            fontSize: '12px',
            py: 0.75,
            borderColor: colors.error,
            color: colors.error,
            '&:hover': {
              borderColor: colors.error,
              backgroundColor: 'rgba(198, 40, 40, 0.04)',
            },
          }}
        >
          Logout
        </Button>
      </Box>

      {/* Save Button */}
      <Box sx={{ px: 2, pb: 2 }}>
        <Button
          variant="contained"
          fullWidth
          size="large"
          onClick={onSave}
          disabled={isSaving}
          startIcon={
            isSaving ? (
              <CircularProgress size={20} color="inherit" />
            ) : (
              <SaveIcon />
            )
          }
          sx={{
            backgroundColor: colors.primary,
            color: '#ffffff',
            fontWeight: 600,
            fontSize: '16px',
            py: 1.5,
            boxShadow: '0 2px 8px rgba(0, 131, 143, 0.3)',
            '&:hover': {
              backgroundColor: colors.primaryDark,
              boxShadow: '0 4px 12px rgba(0, 131, 143, 0.4)',
            },
            '&:disabled': {
              backgroundColor: colors.border,
              color: colors.text.secondary,
            },
          }}
        >
          {isSaving ? 'Saving...' : 'Save Daily Count'}
        </Button>
      </Box>
    </Box>
  );
};

export default Footer;
