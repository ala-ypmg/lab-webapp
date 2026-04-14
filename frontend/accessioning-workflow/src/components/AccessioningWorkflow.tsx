/**
 * T02 + T15 — Root component
 *
 * Owns the complete AppState, renders the current page,
 * handles cross-page validation, and submits to Flask.
 */
import { useState, useCallback } from 'react';
import { Box, Snackbar } from '@mui/material';
import type {
  AppState,
  SectionKey,
  FormData,
  SectionErrors,
  HeldCaseRow,
  AccessionedValue,
} from '../types/index.ts';
import { validateCaseNumber } from '../utils/caseNumber.ts';
import Page1 from './Page1.tsx';
import Page2 from './Page2.tsx';
import Page3 from './Page3.tsx';
import BottomNavBar from './BottomNavBar.tsx';
import SuccessScreen from './SuccessScreen.tsx';
import TopNavBar from './TopNavBar.tsx';

// ---------------------------------------------------------------------------
// Initial state factory
// ---------------------------------------------------------------------------

function makeInitialFormData(): FormData {
  return {
    client_requests: [],
    bone_marrow: [],
    frozen_section: [],
    stat_cases: [],
    held_cases: [],
  };
}

function makeInitialState(): AppState {
  return {
    selected_types: new Set<SectionKey>(),
    form_data: makeInitialFormData(),
    notes: '',
    accessioned: null,
  };
}

// ---------------------------------------------------------------------------
// Validation helpers (T15)
// ---------------------------------------------------------------------------

const SECTION_LABELS: Record<SectionKey, string> = {
  client_requests: 'Client Requests',
  bone_marrow: 'Bakersfield Bone Marrow Cases',
  frozen_section: 'Frozen Section for Intraoperative Consultation',
  stat_cases: 'STAT Cases',
  held_cases: 'Held Cases',
};

function validateFormData(
  selectedTypes: Set<SectionKey>,
  formData: FormData
): SectionErrors {
  const errors: SectionErrors = {};

  for (const key of selectedTypes) {
    const rows = formData[key];
    const rowErrors: Record<number, Record<string, string>> = {};

    rows.forEach((row, idx) => {
      const cellErrors: Record<string, string> = {};

      // case_number required for all sections
      const cnResult = validateCaseNumber(row.case_number || '');
      if (!row.case_number) {
        cellErrors['case_number'] = 'Case number is required';
      } else if (!cnResult.valid) {
        cellErrors['case_number'] = cnResult.error;
      }

      // Held-cases-specific validation
      if (key === 'held_cases') {
        const held = row as HeldCaseRow;
        if (!held.hold_type) {
          cellErrors['hold_type'] = 'Hold type is required';
        }
        if (!held.hold_reasons || held.hold_reasons.length === 0) {
          cellErrors['hold_reasons'] = 'At least one hold reason is required';
        }
      }

      if (Object.keys(cellErrors).length > 0) {
        rowErrors[idx] = cellErrors;
      }
    });

    if (Object.keys(rowErrors).length > 0) {
      errors[key] = rowErrors;
    }
  }

  return errors;
}

/** Returns the lowest page number (1, 2, or 3) that has an error. */
function lowestErrorPage(
  p1Error: boolean,
  p2Error: boolean,
  _p3Error: boolean
): 1 | 2 | 3 {
  if (p1Error) return 1;
  if (p2Error) return 2;
  return 3;
}

function getCSRFToken(): string {
  return window.WORKFLOW_SESSION?.csrfToken ?? '';
}

// ---------------------------------------------------------------------------
// Root component
// ---------------------------------------------------------------------------

export default function AccessioningWorkflow() {
  const [state, setState] = useState<AppState>(makeInitialState());
  const [currentPage, setCurrentPage] = useState<1 | 2 | 3>(1);
  const [sectionErrors, setSectionErrors] = useState<SectionErrors>({});
  const [page3AccessionedError, setPage3AccessionedError] = useState('');
  const [page1ValidationError, setPage1ValidationError] = useState(false);
  const [page2ErrorMsg, setPage2ErrorMsg] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [submittedAt, setSubmittedAt] = useState<Date | null>(null);
  const [snackbar, setSnackbar] = useState('');

  // ---------------------------------------------------------------------------
  // State updaters
  // ---------------------------------------------------------------------------

  const toggleType = useCallback((key: SectionKey) => {
    setState((prev) => {
      const next = new Set(prev.selected_types);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return { ...prev, selected_types: next };
    });
    setPage1ValidationError(false);
  }, []);

  const handleFormDataChange = useCallback(
    (key: SectionKey, rows: FormData[SectionKey]) => {
      setState((prev) => ({
        ...prev,
        form_data: { ...prev.form_data, [key]: rows },
      }));
      // Clear errors for updated section
      setSectionErrors((prev) => {
        const next = { ...prev };
        delete next[key];
        return next;
      });
    },
    []
  );

  // ---------------------------------------------------------------------------
  // Navigation (T02)
  // ---------------------------------------------------------------------------

  const handleNavigate = useCallback(
    (target: 1 | 2 | 3) => {
      // Going forward from page 1 — enforce at least one type selected
      if (currentPage === 1 && target > 1 && state.selected_types.size === 0) {
        setPage1ValidationError(true);
        return;
      }

      // Going to page 3 (submit) — run full validation
      if (target === 3 && currentPage === 3) {
        handleSubmit();
        return;
      }

      setCurrentPage(target);
    },
    [currentPage, state.selected_types]
  );

  // ---------------------------------------------------------------------------
  // Submit (T15)
  // ---------------------------------------------------------------------------

  const handleSubmit = useCallback(async () => {
    const { selected_types, form_data, accessioned } = state;

    // Page 1 check
    const p1Error = selected_types.size === 0;

    // Page 2 validation
    const formErrors = validateFormData(selected_types, form_data);
    const p2Error = Object.keys(formErrors).length > 0;

    // Page 3 check
    const p3AccessionError = accessioned === null;

    if (p1Error || p2Error || p3AccessionError) {
      setSectionErrors(formErrors);

      // Build page 2 error message
      if (p2Error) {
        const errorSections = Object.keys(formErrors)
          .map((k) => SECTION_LABELS[k as SectionKey])
          .join(', ');
        setPage2ErrorMsg(`Please fix errors in: ${errorSections}`);
      } else {
        setPage2ErrorMsg('');
      }

      if (p3AccessionError) {
        setPage3AccessionedError('Please answer the accessioning confirmation before submitting.');
      }

      const targetPage = lowestErrorPage(p1Error, p2Error, p3AccessionError);
      setCurrentPage(targetPage);
      return;
    }

    // Clean — submit
    setIsSubmitting(true);
    try {
      const payload = {
        selected_types: [...selected_types],
        form_data: {
          client_requests: form_data.client_requests.map(({ id: _id, ...r }) => r),
          bone_marrow: form_data.bone_marrow.map(({ id: _id, ...r }) => r),
          frozen_section: form_data.frozen_section.map(({ id: _id, ...r }) => r),
          stat_cases: form_data.stat_cases.map(({ id: _id, ...r }) => r),
          held_cases: form_data.held_cases.map(({ id: _id, ...r }) => r),
        },
        notes: state.notes,
        accessioned: state.accessioned,
      };

      const res = await fetch('/accessioning-workflow/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        setSnackbar((err as { error?: string }).error ?? 'Submission failed. Please try again.');
        return;
      }

      setSubmittedAt(new Date());
      setSubmitted(true);
    } catch {
      setSnackbar('Network error. Please check your connection and try again.');
    } finally {
      setIsSubmitting(false);
    }
  }, [state]);

  // ---------------------------------------------------------------------------
  // Reset
  // ---------------------------------------------------------------------------

  const handleReset = () => {
    setState(makeInitialState());
    setCurrentPage(1);
    setSectionErrors({});
    setPage3AccessionedError('');
    setPage1ValidationError(false);
    setPage2ErrorMsg('');
    setSubmitted(false);
    setSubmittedAt(null);
  };

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  if (submitted && submittedAt) {
    return (
      <>
        <TopNavBar onClearSession={handleReset} />
        <SuccessScreen
          submittedAt={submittedAt}
          submittedTypes={state.selected_types}
          formData={state.form_data}
          onReset={handleReset}
        />
      </>
    );
  }

  const canProceedPage1 = state.selected_types.size > 0;

  return (
    <Box sx={{ pb: '80px' /* room for fixed bottom nav bar */ }}>
      <TopNavBar onClearSession={handleReset} />
      {currentPage === 1 && (
        <Page1
          selectedTypes={state.selected_types}
          onToggle={toggleType}
          showValidationError={page1ValidationError}
        />
      )}
      {currentPage === 2 && (
        <Page2
          selectedTypes={state.selected_types}
          formData={state.form_data}
          onFormDataChange={handleFormDataChange}
          sectionErrors={sectionErrors}
          pageError={page2ErrorMsg}
        />
      )}
      {currentPage === 3 && (
        <Page3
          notes={state.notes}
          onNotesChange={(notes) => setState((prev) => ({ ...prev, notes }))}
          accessioned={state.accessioned}
          onAccessionedChange={(value: AccessionedValue) => {
            setState((prev) => ({ ...prev, accessioned: value }));
            setPage3AccessionedError('');
          }}
          accessionedError={page3AccessionedError}
        />
      )}

      <BottomNavBar
        currentPage={currentPage}
        onNavigate={handleNavigate}
        canProceed={currentPage === 1 ? canProceedPage1 : true}
        proceedTooltip={
          currentPage === 1 && !canProceedPage1
            ? 'Select at least one case type to continue'
            : undefined
        }
        isSubmitting={isSubmitting}
      />

      <Snackbar
        open={!!snackbar}
        autoHideDuration={6000}
        onClose={() => setSnackbar('')}
        message={snackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
    </Box>
  );
}
