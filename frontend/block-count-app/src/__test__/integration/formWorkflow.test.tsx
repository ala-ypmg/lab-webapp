/**
 * Form Workflow Integration Tests
 */

import { describe, it, expect, vi } from 'vitest';
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

describe('Form Workflow Integration', () => {
  it('should complete a typical 3-run day workflow', async () => {
    const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
    renderWithTheme();

    // 1. Fill in Run 1 data
    // Select prefixes - use exact text match
    const ksChip = screen.getByRole('button', { name: /^KS$/ });
    fireEvent.click(ksChip);
    
    // Enter blocks (first blocks input is the main one)
    let blocksInputs = screen.getAllByRole('textbox', { name: '# of Blocks' });
    fireEvent.change(blocksInputs[0], { target: { value: '45' } });
    
    // Enter cell buttons
    let cellButtonsInput = screen.getByRole('textbox', { name: 'Cell Buttons' });
    fireEvent.change(cellButtonsInput, { target: { value: '5' } });

    // 2. Click Add Run (verify Run 1 collapses)
    let addButton = screen.getByRole('button', { name: /Add Run/i });
    fireEvent.click(addButton);
    
    await waitFor(() => {
      expect(screen.getByText('Run #1: 50')).toBeInTheDocument(); // 45 + 5
      expect(screen.getByText('2 Runs')).toBeInTheDocument();
    });

    // Verify facility was auto-filled
    expect(screen.getByText('Bakersfield OP')).toBeInTheDocument();

    // 3. Click Save
    const saveButton = screen.getByRole('button', { name: /Save Daily Count/i });
    fireEvent.click(saveButton);

    // 4. Verify success feedback
    await waitFor(() => {
      expect(screen.getByText('Daily count saved successfully!')).toBeInTheDocument();
    }, { timeout: 2000 });

    consoleSpy.mockRestore();
  });

  it('should preserve data when collapsing/expanding runs', async () => {
    renderWithTheme();

    // Fill in Run 1 data
    const ksChip = screen.getByRole('button', { name: /^KS$/ });
    fireEvent.click(ksChip);
    const blocksInputs = screen.getAllByRole('textbox', { name: '# of Blocks' });
    fireEvent.change(blocksInputs[0], { target: { value: '75' } });

    // Add new run (collapses Run 1)
    const addButton = screen.getByRole('button', { name: /Add Run/i });
    fireEvent.click(addButton);

    // Verify Run 1 shows correct subtotal
    await waitFor(() => {
      expect(screen.getByText('Run #1: 75')).toBeInTheDocument();
    });

    // Expand Run 1 by clicking on it
    fireEvent.click(screen.getByText('Run #1: 75'));

    // Verify data is preserved
    await waitFor(() => {
      const allBlocksInputs = screen.getAllByRole('textbox', { name: '# of Blocks' });
      // Run 1 should still have 75
      expect(allBlocksInputs[0]).toHaveValue('75');
    });
  });

  it('should handle a heavy day (5+ runs) without performance issues', async () => {
    renderWithTheme();

    const startTime = performance.now();

    // Add 5 runs total (1 initial + 4 more)
    for (let i = 0; i < 4; i++) {
      const addButton = screen.getByRole('button', { name: /Add Run/i });
      fireEvent.click(addButton);
    }

    await waitFor(() => {
      expect(screen.getByText('5 Runs')).toBeInTheDocument();
    });

    const endTime = performance.now();
    const duration = endTime - startTime;

    // Should complete in under 5 seconds (allowing for CI environment variability)
    expect(duration).toBeLessThan(5000);

    // All runs should be accessible
    expect(screen.getByText('Run #1: 0')).toBeInTheDocument();
    expect(screen.getByText('Run #2: 0')).toBeInTheDocument();
    expect(screen.getByText('Run #3: 0')).toBeInTheDocument();
    expect(screen.getByText('Run #4: 0')).toBeInTheDocument();
    expect(screen.getByText('Run 5')).toBeInTheDocument(); // Active run is expanded
  });

  it('should correctly calculate totals across many runs', async () => {
    renderWithTheme();

    // Fill first run with 20 blocks
    let blocksInputs = screen.getAllByRole('textbox', { name: '# of Blocks' });
    fireEvent.change(blocksInputs[0], { target: { value: '20' } });

    // Add second run
    const addButton = screen.getByRole('button', { name: /Add Run/i });
    fireEvent.click(addButton);
    
    // Wait for new run to be added
    await waitFor(() => {
      expect(screen.getByText('2 Runs')).toBeInTheDocument();
      expect(screen.getByText('Run #1: 20')).toBeInTheDocument();
    });

    // Verify total still shows 20 from first run (preserved data)
    await waitFor(() => {
      const totalElements = screen.getAllByText('20');
      expect(totalElements.length).toBeGreaterThan(0);
    });
  });

  it('should handle bone marrow entries correctly', async () => {
    renderWithTheme();

    // Enter bone marrow data
    const bmCaseInput = screen.getByRole('textbox', { name: 'Case #' });
    fireEvent.change(bmCaseInput, { target: { value: 'BM-2024-001' } });

    const allBlockInputs = screen.getAllByRole('textbox', { name: '# of Blocks' });
    // Find the bone marrow blocks input (second one in the form)
    fireEvent.change(allBlockInputs[1], { target: { value: '3' } });

    // BM total should show 3
    await waitFor(() => {
      const bmTotals = screen.getAllByText('3');
      expect(bmTotals.length).toBeGreaterThan(0);
    });
  });

  it('should handle autopsy entries via card section', async () => {
    renderWithTheme();

    // Autopsy section is now always visible as a card (no accordion expand needed)
    const autopsyInput = screen.getByRole('textbox', { name: '# of Autopsy Blocks' });
    fireEvent.change(autopsyInput, { target: { value: '5' } });

    // Autopsy total should show 5
    await waitFor(() => {
      const autopsyTotals = screen.getAllByText('5');
      expect(autopsyTotals.length).toBeGreaterThan(0);
    });
  });

  it('should handle multiple facilities correctly', async () => {
    renderWithTheme();

    // Select prefixes from different facilities using exact matches
    const ksChip = screen.getByRole('button', { name: /^KS$/ });
    fireEvent.click(ksChip);
    
    const vvsChip = screen.getByRole('button', { name: /^VVS$/ });
    fireEvent.click(vvsChip);

    // Should show "Multiple Facilities"
    await waitFor(() => {
      expect(screen.getByText('Multiple Facilities')).toBeInTheDocument();
    });
  });

  it('should allow deleting runs except the last one', async () => {
    renderWithTheme();

    // Add two more runs
    const addButton = screen.getByRole('button', { name: /Add Run/i });
    fireEvent.click(addButton);
    fireEvent.click(addButton);

    expect(screen.getByText('3 Runs')).toBeInTheDocument();

    // Delete runs until only one left
    const deleteButtons = screen.getAllByLabelText(/Delete Run/i);
    fireEvent.click(deleteButtons[2]); // Delete Run 3
    
    await waitFor(() => {
      expect(screen.getByText('2 Runs')).toBeInTheDocument();
    });

    const remainingDeleteButtons = screen.getAllByLabelText(/Delete Run/i);
    fireEvent.click(remainingDeleteButtons[1]); // Delete Run 2

    await waitFor(() => {
      expect(screen.getByText('1 Run')).toBeInTheDocument();
    });

    // Last delete button should be disabled
    const lastDeleteButton = screen.getByLabelText('Delete Run 1');
    expect(lastDeleteButton).toBeDisabled();
  });
});
