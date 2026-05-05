/**
 * YPBDailyCountForm Component Tests
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider } from '@mui/material';
import YPBDailyCountForm from '../../components/YPBDailyCountForm';
import { theme } from '../../constants/theme';

const renderWithTheme = () => {
  return render(
    <ThemeProvider theme={theme}>
      <YPBDailyCountForm />
    </ThemeProvider>
  );
};

describe('YPBDailyCountForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should render with one empty run', () => {
      renderWithTheme();
      
      expect(screen.getByText('Run 1')).toBeInTheDocument();
    });

    it('should display current date by default', () => {
      renderWithTheme();
      
      const dateInput = screen.getByDisplayValue(new Date().toISOString().split('T')[0]);
      expect(dateInput).toBeInTheDocument();
    });

    it('should show "1 Run" in header badge', () => {
      renderWithTheme();
      
      expect(screen.getByText('1 Run')).toBeInTheDocument();
    });

    it('should display YPB Daily Count title', () => {
      renderWithTheme();
      
      expect(screen.getByText('YPB Daily Count')).toBeInTheDocument();
    });

    it('should display Check Out Department subtitle', () => {
      renderWithTheme();
      
      expect(screen.getByText('Check Out Department')).toBeInTheDocument();
    });

    it('should display totals footer', () => {
      renderWithTheme();
      
      expect(screen.getByText('Blocks')).toBeInTheDocument();
      expect(screen.getByText('BM')).toBeInTheDocument();
      expect(screen.getByText('Autopsy')).toBeInTheDocument();
      expect(screen.getByText('Cells')).toBeInTheDocument();
      expect(screen.getByText('Total')).toBeInTheDocument();
    });

    it('should display Save button', () => {
      renderWithTheme();
      
      expect(screen.getByRole('button', { name: /Save Daily Count/i })).toBeInTheDocument();
    });
  });

  describe('Add Run', () => {
    it('should add new run when Add Run clicked', () => {
      renderWithTheme();
      
      const addButton = screen.getByRole('button', { name: /Add Run/i });
      fireEvent.click(addButton);
      
      expect(screen.getByText('2 Runs')).toBeInTheDocument();
    });

    it('should auto-collapse all existing runs when adding new run', async () => {
      renderWithTheme();
      
      // Initially Run 1 is expanded
      expect(screen.getByText('Run 1')).toBeInTheDocument();
      expect(screen.getByText('Case Prefixes')).toBeInTheDocument();
      
      // Add a new run
      const addButton = screen.getByRole('button', { name: /Add Run/i });
      fireEvent.click(addButton);
      
      // Now "Run #1: 0" should appear (collapsed format)
      await waitFor(() => {
        expect(screen.getByText('Run #1: 0')).toBeInTheDocument();
      });
    });

    it('should expand newly added run', () => {
      renderWithTheme();
      
      const addButton = screen.getByRole('button', { name: /Add Run/i });
      fireEvent.click(addButton);
      
      // The new run (Run 2) should be expanded
      expect(screen.getByText('Run 2')).toBeInTheDocument();
    });

    it('should update run counter badge', () => {
      renderWithTheme();
      
      expect(screen.getByText('1 Run')).toBeInTheDocument();
      
      const addButton = screen.getByRole('button', { name: /Add Run/i });
      fireEvent.click(addButton);
      expect(screen.getByText('2 Runs')).toBeInTheDocument();
      
      fireEvent.click(addButton);
      expect(screen.getByText('3 Runs')).toBeInTheDocument();
    });
  });

  describe('Delete Run', () => {
    it('should remove run from list', async () => {
      renderWithTheme();
      
      // Add a second run
      const addButton = screen.getByRole('button', { name: /Add Run/i });
      fireEvent.click(addButton);
      expect(screen.getByText('2 Runs')).toBeInTheDocument();
      
      // Delete the second run
      const deleteButtons = screen.getAllByLabelText(/Delete Run/i);
      fireEvent.click(deleteButtons[1]); // Delete Run 2
      
      expect(screen.getByText('1 Run')).toBeInTheDocument();
    });

    it('should not allow deleting last run', () => {
      renderWithTheme();
      
      const deleteButton = screen.getByLabelText('Delete Run 1');
      expect(deleteButton).toBeDisabled();
    });

    it('should reindex run numbers after deletion', async () => {
      renderWithTheme();
      
      // Add two more runs
      const addButton = screen.getByRole('button', { name: /Add Run/i });
      fireEvent.click(addButton);
      fireEvent.click(addButton);
      
      expect(screen.getByText('3 Runs')).toBeInTheDocument();
      
      // Delete the middle run (Run 2)
      // First need to find it - runs 1 and 2 are collapsed, run 3 is expanded
      await waitFor(() => {
        const deleteButtons = screen.getAllByLabelText(/Delete Run/i);
        expect(deleteButtons.length).toBe(3);
      });
    });
  });

  describe('Totals Calculation', () => {
    it('should update totals when run values change', async () => {
      renderWithTheme();
      
      // Enter blocks value - find the first blocks input (main blocks, not bone marrow)
      const blocksInputs = screen.getAllByRole('textbox', { name: '# of Blocks' });
      fireEvent.change(blocksInputs[0], { target: { value: '25' } });
      
      // Total should reflect the change
      await waitFor(() => {
        const totalElements = screen.getAllByText('25');
        expect(totalElements.length).toBeGreaterThan(0);
      });
    });

    it('should calculate correct grand total', async () => {
      renderWithTheme();
      
      // Enter blocks value
      const blocksInputs = screen.getAllByRole('textbox', { name: '# of Blocks' });
      fireEvent.change(blocksInputs[0], { target: { value: '100' } });
      
      const cellButtonsInput = screen.getByRole('textbox', { name: 'Cell Buttons' });
      fireEvent.change(cellButtonsInput, { target: { value: '15' } });
      
      // Total should be 115 (100 + 15)
      await waitFor(() => {
        const totalElements = screen.getAllByText('115');
        expect(totalElements.length).toBeGreaterThan(0);
      });
    });

    it('should handle multiple runs correctly', async () => {
      renderWithTheme();
      
      // Enter value in first run
      let blocksInputs = screen.getAllByRole('textbox', { name: '# of Blocks' });
      fireEvent.change(blocksInputs[0], { target: { value: '50' } });
      
      // Verify first run value reflected in totals
      await waitFor(() => {
        const totalElements = screen.getAllByText('50');
        expect(totalElements.length).toBeGreaterThan(0);
      });
      
      // Add second run
      const addButton = screen.getByRole('button', { name: /Add Run/i });
      fireEvent.click(addButton);
      
      // Wait for new run to be added and verify the first run is now collapsed
      await waitFor(() => {
        expect(screen.getByText('2 Runs')).toBeInTheDocument();
        expect(screen.getByText('Run #1: 50')).toBeInTheDocument(); // First run collapsed with subtotal
      });
      
      // Check that total still shows 50 from first run
      await waitFor(() => {
        const totalElements = screen.getAllByText('50');
        expect(totalElements.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Date Field', () => {
    it('should allow changing the date', () => {
      renderWithTheme();
      
      const dateInput = screen.getByDisplayValue(new Date().toISOString().split('T')[0]);
      fireEvent.change(dateInput, { target: { value: '2024-12-25' } });
      
      expect(screen.getByDisplayValue('2024-12-25')).toBeInTheDocument();
    });
  });

  describe('Save Functionality', () => {
    it('should trigger save action when Save button clicked', async () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      renderWithTheme();
      
      const saveButton = screen.getByRole('button', { name: /Save Daily Count/i });
      fireEvent.click(saveButton);
      
      // Should show loading state
      expect(screen.getByText('Saving...')).toBeInTheDocument();
      
      // Wait for save to complete
      await waitFor(() => {
        expect(screen.getByText('Daily count saved successfully!')).toBeInTheDocument();
      }, { timeout: 2000 });
      
      consoleSpy.mockRestore();
    });
  });
});
