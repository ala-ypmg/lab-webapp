/**
 * YPBDailyCountForm Component
 * 
 * Main container component for the YPB Daily Block Count Form.
 * Manages form state and handles all run operations.
 */

import React, { useState, useMemo, useCallback, useRef, useEffect } from 'react';
import { Box, Button, TextField, Typography, Snackbar, Alert } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import Header from './Header';
import Footer from './Footer';
import RunEntry from './RunEntry';
import InfoTooltip from './InfoTooltip';
import type { RunEntry as RunEntryType, Totals } from '../types';
import { createEmptyRunEntry } from '../types';
import { calculateTotals, getTodayDateString } from '../utils';
import { TOOLTIPS } from '../constants/tooltips';
import { colors } from '../constants/theme';

// Retrieve CSRF token from server-rendered window object
const getCSRFToken = (): string => {
  const session = (window as unknown as Record<string, { csrfToken?: string }>).WORKFLOW_SESSION;
  return session?.csrfToken || '';
};

async function postToRoute(route: string): Promise<void> {
  await fetch(route, {
    method: 'POST',
    headers: { 'X-CSRFToken': getCSRFToken() },
    credentials: 'same-origin',
  });
  window.location.href = '/login';
}

const YPBDailyCountForm: React.FC = () => {
  // Form state
  const [date, setDate] = useState<string>(getTodayDateString());
  const [entries, setEntries] = useState<RunEntryType[]>([createEmptyRunEntry()]);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error';
  }>({
    open: false,
    message: '',
    severity: 'success',
  });

  // Ref for scrolling to new runs
  const entriesEndRef = useRef<HTMLDivElement>(null);
  const lastAddedRunRef = useRef<number | null>(null);

  // Calculate totals using useMemo for performance
  const totals: Totals = useMemo(() => calculateTotals(entries), [entries]);

  // Scroll to new run when added
  useEffect(() => {
    if (lastAddedRunRef.current !== null) {
      entriesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      lastAddedRunRef.current = null;
    }
  }, [entries.length]);

  // Handle adding a new run
  const handleAddRun = useCallback(() => {
    // Collapse all existing runs
    const collapsedEntries = entries.map((entry) => ({
      ...entry,
      collapsed: true,
    }));

    // Create new run
    const newEntry = createEmptyRunEntry();
    lastAddedRunRef.current = newEntry.id;

    setEntries([...collapsedEntries, newEntry]);
  }, [entries]);

  // Handle toggling run collapse state
  const handleToggleCollapse = useCallback((id: number) => {
    setEntries((prevEntries) =>
      prevEntries.map((entry) =>
        entry.id === id ? { ...entry, collapsed: !entry.collapsed } : entry
      )
    );
  }, []);

  // Handle updating a run entry
  const handleUpdateEntry = useCallback((id: number, updates: Partial<RunEntryType>) => {
    setEntries((prevEntries) =>
      prevEntries.map((entry) =>
        entry.id === id ? { ...entry, ...updates } : entry
      )
    );
  }, []);

  // Handle deleting a run entry
  const handleDeleteEntry = useCallback((id: number) => {
    setEntries((prevEntries) => {
      if (prevEntries.length <= 1) {
        return prevEntries; // Don't delete the last run
      }
      return prevEntries.filter((entry) => entry.id !== id);
    });
  }, []);

  // Handle save
  const handleSave = useCallback(async () => {
    setIsSaving(true);
    
    try {
      // Prepare data for API
      const formData = {
        date,
        entries: entries.map((entry) => ({
          facility: entry.facility,
          selectedPrefixes: entry.selectedPrefixes,
          blocks: entry.blocks,
          boneMarrowCase: entry.boneMarrowCase,
          boneMarrowBlocks: entry.boneMarrowBlocks,
          cellButtons: entry.cellButtons,
          autopsyBlocks: entry.autopsyBlocks,
          checkoutTime: entry.checkoutTime,
        })),
        totals,
      };

      // POST data to Flask backend
      const response = await fetch('/ypb-daily-count', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify(formData),
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setSnackbar({
          open: true,
          message: 'Daily count saved successfully!',
          severity: 'success',
        });

        // Redirect to next page if provided
        if (result.redirect) {
          setTimeout(() => {
            window.location.href = result.redirect;
          }, 1500);
        }
      } else {
        throw new Error(result.error || 'Failed to save');
      }
    } catch (error) {
      console.error('Save error:', error);
      setSnackbar({
        open: true,
        message: 'Failed to save. Please try again.',
        severity: 'error',
      });
    } finally {
      setIsSaving(false);
    }
  }, [date, entries, totals]);

  // Handle snackbar close
  const handleSnackbarClose = () => {
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  // Navigation handlers
  const handleBackToLogin = useCallback(() => {
    window.location.href = '/login';
  }, []);

  const handleGoToWorkflow = useCallback(() => {
    window.location.href = '/workflow';
  }, []);

  const handleGoToNotes = useCallback(() => {
    window.location.href = '/notes';
  }, []);

  const handleLogout = useCallback(() => {
    const csrfToken = (window as any).WORKFLOW_SESSION?.csrfToken ?? '';
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/logout';
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'csrf_token';
    input.value = csrfToken;
    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();
  }, []);

  return (
    <Box
      sx={{
        minHeight: '100vh',
        backgroundColor: colors.background,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Sticky Header */}
      <Header
        runCount={entries.length}
        onClearSession={() => postToRoute('/clear-session')}
        onChangeDepartment={() => postToRoute('/change-department')}
      />

      {/* Scrollable Content */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          padding: '16px',
          paddingBottom: '200px', // Space for sticky footer
        }}
      >
        {/* Date Field */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Typography
              variant="body2"
              component="label"
              sx={{
                fontWeight: 500,
                color: 'text.secondary',
                fontSize: '13px',
              }}
            >
              Date
            </Typography>
            <InfoTooltip title={TOOLTIPS.date} />
          </Box>
          <TextField
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            size="small"
            fullWidth
            slotProps={{
              input: {
                sx: {
                  fontSize: '16px',
                  backgroundColor: '#ffffff',
                },
              },
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '8px',
              },
            }}
          />
        </Box>

        {/* Run Entries */}
        {entries.map((entry, index) => (
          <RunEntry
            key={entry.id}
            entry={entry}
            index={index}
            totalRuns={entries.length}
            onUpdate={handleUpdateEntry}
            onDelete={handleDeleteEntry}
            onToggleCollapse={handleToggleCollapse}
          />
        ))}

        {/* Scroll target for new runs */}
        <div ref={entriesEndRef} />

        {/* Add Run Button */}
        <Button
          variant="outlined"
          fullWidth
          startIcon={<AddIcon />}
          onClick={handleAddRun}
          sx={{
            borderStyle: 'dashed',
            borderWidth: 2,
            borderColor: colors.primary,
            color: colors.primary,
            fontWeight: 600,
            fontSize: '15px',
            py: 1.5,
            mt: 1,
            backgroundColor: 'rgba(0, 131, 143, 0.04)',
            '&:hover': {
              borderStyle: 'dashed',
              borderWidth: 2,
              backgroundColor: 'rgba(0, 131, 143, 0.08)',
            },
          }}
        >
          Add Run
        </Button>
      </Box>

      {/* Sticky Footer */}
      <Footer
        totals={totals}
        onSave={handleSave}
        isSaving={isSaving}
        onBackToLogin={handleBackToLogin}
        onGoToWorkflow={handleGoToWorkflow}
        onGoToNotes={handleGoToNotes}
        onLogout={handleLogout}
      />

      {/* Success/Error Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert
          onClose={handleSnackbarClose}
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default YPBDailyCountForm;
