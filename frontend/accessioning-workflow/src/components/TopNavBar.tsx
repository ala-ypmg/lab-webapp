/**
 * TopNavBar — persistent header for the Accessioning Workflow.
 *
 * Contains:
 *   - App title
 *   - "Clear Session" button — resets all form state (with confirmation dialog)
 *   - "Logout" button — POSTs to Flask /logout
 */
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
} from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';
import DeleteSweepIcon from '@mui/icons-material/DeleteSweep';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import { useState } from 'react';

interface TopNavBarProps {
  onClearSession: () => void;
}

function getCSRFToken(): string {
  return window.WORKFLOW_SESSION?.csrfToken ?? '';
}

async function postLogout() {
  await fetch('/logout', {
    method: 'POST',
    headers: { 'X-CSRFToken': getCSRFToken() },
    credentials: 'same-origin',
  });
  window.location.href = '/login';
}

async function postChangeDepartment() {
  await fetch('/change-department', {
    method: 'POST',
    headers: { 'X-CSRFToken': getCSRFToken() },
    credentials: 'same-origin',
  });
  window.location.href = '/login';
}

export default function TopNavBar({ onClearSession }: TopNavBarProps) {
  const [clearOpen, setClearOpen] = useState(false);
  const [changeDeptOpen, setChangeDeptOpen] = useState(false);
  const [logoutOpen, setLogoutOpen] = useState(false);

  const handleConfirmClear = () => {
    onClearSession();
    setClearOpen(false);
  };

  const handleConfirmChangeDept = () => {
    setChangeDeptOpen(false);
    postChangeDepartment();
  };

  const handleConfirmLogout = () => {
    setLogoutOpen(false);
    postLogout();
  };

  return (
    <>
      <AppBar position="sticky" elevation={1}>
        <Toolbar variant="dense">
          <Typography variant="h6" fontWeight={700} sx={{ flexGrow: 1, fontSize: '1rem' }}>
            Accessioning Workflow
          </Typography>

          <Box display="flex" gap={1}>
            <Button
              color="inherit"
              size="small"
              startIcon={<DeleteSweepIcon />}
              onClick={() => setClearOpen(true)}
              sx={{ textTransform: 'none' }}
            >
              Clear Session
            </Button>
            <Button
              color="inherit"
              size="small"
              startIcon={<SwapHorizIcon />}
              onClick={() => setChangeDeptOpen(true)}
              sx={{ textTransform: 'none' }}
            >
              Change Department
            </Button>
            <Button
              color="inherit"
              size="small"
              startIcon={<LogoutIcon />}
              onClick={() => setLogoutOpen(true)}
              sx={{ textTransform: 'none' }}
            >
              Logout
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Clear session confirmation */}
      <Dialog open={clearOpen} onClose={() => setClearOpen(false)}>
        <DialogTitle>Clear session?</DialogTitle>
        <DialogContent>
          <Typography>
            All entered case data will be lost and the form will reset to page 1.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setClearOpen(false)}>Cancel</Button>
          <Button color="error" variant="contained" onClick={handleConfirmClear}>
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
          <Button color="warning" variant="contained" onClick={handleConfirmChangeDept}>
            Change Department
          </Button>
        </DialogActions>
      </Dialog>

      {/* Logout confirmation */}
      <Dialog open={logoutOpen} onClose={() => setLogoutOpen(false)}>
        <DialogTitle>Log out?</DialogTitle>
        <DialogContent>
          <Typography>Any unsaved data will be lost.</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLogoutOpen(false)}>Cancel</Button>
          <Button color="primary" variant="contained" onClick={handleConfirmLogout}>
            Log out
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
