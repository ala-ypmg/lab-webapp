/**
 * Header Component
 *
 * Sticky header with title, subtitle, run counter badge, and nav action buttons.
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import DeleteSweepIcon from '@mui/icons-material/DeleteSweep';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import type { HeaderProps } from '../types';
import { colors } from '../constants/theme';

const Header: React.FC<HeaderProps> = ({ runCount, onClearSession, onChangeDepartment }) => {
  const [clearOpen, setClearOpen] = useState(false);
  const [changeDeptOpen, setChangeDeptOpen] = useState(false);

  return (
    <>
      <Box
        sx={{
          position: 'sticky',
          top: 0,
          zIndex: 100,
          backgroundColor: colors.primary,
          padding: '12px 20px',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
        }}
      >
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
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

          <Box display="flex" alignItems="center" gap={1}>
            <Chip
              label={`${runCount} ${runCount === 1 ? 'Run' : 'Runs'}`}
              sx={{
                backgroundColor: 'rgba(255, 255, 255, 0.2)',
                color: '#ffffff',
                fontWeight: 600,
                fontSize: '13px',
                height: 28,
                '& .MuiChip-label': { px: 1.5 },
              }}
            />
            <Button
              size="small"
              startIcon={<DeleteSweepIcon />}
              onClick={() => setClearOpen(true)}
              sx={{
                color: '#ffffff',
                textTransform: 'none',
                fontSize: '13px',
                '&:hover': { backgroundColor: 'rgba(255,255,255,0.15)' },
              }}
            >
              Clear Session
            </Button>
            <Button
              size="small"
              startIcon={<SwapHorizIcon />}
              onClick={() => setChangeDeptOpen(true)}
              sx={{
                color: '#ffffff',
                textTransform: 'none',
                fontSize: '13px',
                '&:hover': { backgroundColor: 'rgba(255,255,255,0.15)' },
              }}
            >
              Change Department
            </Button>
          </Box>
        </Box>
      </Box>

      {/* Clear session confirmation */}
      <Dialog open={clearOpen} onClose={() => setClearOpen(false)}>
        <DialogTitle>Clear session?</DialogTitle>
        <DialogContent>
          <Typography>
            All entered data will be lost and the session will be reset. You will be returned to the login page.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setClearOpen(false)}>Cancel</Button>
          <Button
            color="error"
            variant="contained"
            onClick={() => {
              setClearOpen(false);
              onClearSession();
            }}
          >
            Clear
          </Button>
        </DialogActions>
      </Dialog>

      {/* Change department confirmation */}
      <Dialog open={changeDeptOpen} onClose={() => setChangeDeptOpen(false)}>
        <DialogTitle>Change department?</DialogTitle>
        <DialogContent>
          <Typography>
            Your current session will be abandoned. You will be returned to the login page to select a different department.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setChangeDeptOpen(false)}>Cancel</Button>
          <Button
            color="warning"
            variant="contained"
            onClick={() => {
              setChangeDeptOpen(false);
              onChangeDepartment();
            }}
          >
            Change Department
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default Header;
