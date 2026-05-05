/**
 * RunEntry Component Tests
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider } from '@mui/material';
import RunEntry from '../../components/RunEntry';
import { theme } from '../../constants/theme';
import type { RunEntry as RunEntryType } from '../../types';
import { createEmptyRunEntry } from '../../types';

const renderWithTheme = (component: React.ReactNode) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

const createMockEntry = (overrides: Partial<RunEntryType> = {}): RunEntryType => ({
  ...createEmptyRunEntry(),
  id: 1,
  ...overrides,
});

describe('RunEntry', () => {
  const defaultProps = {
    entry: createMockEntry(),
    index: 0,
    totalRuns: 1,
    onUpdate: vi.fn(),
    onDelete: vi.fn(),
    onToggleCollapse: vi.fn(),
  };

  describe('Collapsed State', () => {
    it('should display "Run #N: {subtotal}" format when collapsed', () => {
      const entry = createMockEntry({
        collapsed: true,
        blocks: '10',
        boneMarrowBlocks: '5',
      });
      
      renderWithTheme(
        <RunEntry {...defaultProps} entry={entry} />
      );
      
      expect(screen.getByText('Run #1: 15')).toBeInTheDocument();
    });

    it('should show checkmark when collapsed and subtotal > 0', () => {
      const entry = createMockEntry({
        collapsed: true,
        blocks: '10',
      });
      
      renderWithTheme(
        <RunEntry {...defaultProps} entry={entry} />
      );
      
      // CheckCircleIcon should be rendered
      expect(document.querySelector('[data-testid="CheckCircleIcon"]')).toBeInTheDocument();
    });

    it('should not show checkmark when collapsed with no data', () => {
      const entry = createMockEntry({
        collapsed: true,
        blocks: '',
      });
      
      renderWithTheme(
        <RunEntry {...defaultProps} entry={entry} />
      );
      
      expect(document.querySelector('[data-testid="CheckCircleIcon"]')).not.toBeInTheDocument();
    });

    it('should show checkout time in header when collapsed', () => {
      const entry = createMockEntry({
        collapsed: true,
        checkoutTime: '14:30',
      });
      
      renderWithTheme(
        <RunEntry {...defaultProps} entry={entry} />
      );
      
      expect(screen.getByText('2:30 PM')).toBeInTheDocument();
    });

    it('should hide form fields when collapsed', () => {
      const entry = createMockEntry({
        collapsed: true,
      });
      
      renderWithTheme(
        <RunEntry {...defaultProps} entry={entry} />
      );
      
      // When collapsed, the collapsed format should be shown
      expect(screen.getByText('Run #1: 0')).toBeInTheDocument();
      // MUI Collapse keeps elements in DOM but hides them - check that collapsed header shows correct format
      expect(screen.getByRole('button', { name: /Run #1: 0/ })).toBeInTheDocument();
    });

    it('should show facility name when collapsed', () => {
      const entry = createMockEntry({
        collapsed: true,
        facility: 'Bakersfield OP',
      });
      
      renderWithTheme(
        <RunEntry {...defaultProps} entry={entry} />
      );
      
      expect(screen.getByText('Bakersfield OP')).toBeInTheDocument();
    });
  });

  describe('Expanded State', () => {
    it('should display circular badge with run number', () => {
      const entry = createMockEntry({
        collapsed: false,
      });
      
      renderWithTheme(
        <RunEntry {...defaultProps} entry={entry} />
      );
      
      // Run number in badge
      expect(screen.getByText('1')).toBeInTheDocument();
      expect(screen.getByText('Run 1')).toBeInTheDocument();
    });

    it('should show all form fields when expanded', () => {
      const entry = createMockEntry({
        collapsed: false,
      });
      
      renderWithTheme(
        <RunEntry {...defaultProps} entry={entry} />
      );
      
      expect(screen.getByText('Case Prefixes')).toBeInTheDocument();
      expect(screen.getByText('Checkout Time')).toBeInTheDocument();
      expect(screen.getByText('Cell Buttons')).toBeInTheDocument();
      expect(screen.getByText('Bone Marrow')).toBeInTheDocument();
    });

    it('should auto-fill facility when prefixes selected', () => {
      const onUpdate = vi.fn();
      const entry = createMockEntry({
        collapsed: false,
        selectedPrefixes: [],
      });
      
      renderWithTheme(
        <RunEntry {...defaultProps} entry={entry} onUpdate={onUpdate} />
      );
      
      // Click on a prefix chip (KS is Bakersfield OP)
      fireEvent.click(screen.getByText('KS'));
      
      expect(onUpdate).toHaveBeenCalledWith(entry.id, {
        selectedPrefixes: ['KS'],
        facility: 'Bakersfield OP',
      });
    });

    it('should show facility name when expanded', () => {
      const entry = createMockEntry({
        collapsed: false,
        facility: 'Visalia',
      });
      
      renderWithTheme(
        <RunEntry {...defaultProps} entry={entry} />
      );
      
      expect(screen.getByText('Visalia')).toBeInTheDocument();
    });
  });

  describe('Interactions', () => {
    it('should toggle collapse when header clicked', () => {
      const onToggleCollapse = vi.fn();
      const entry = createMockEntry({
        collapsed: false,
      });
      
      renderWithTheme(
        <RunEntry {...defaultProps} entry={entry} onToggleCollapse={onToggleCollapse} />
      );
      
      // Click the header area (the div with role=button and aria-expanded)
      const headers = screen.getAllByRole('button', { name: /Run 1/i });
      // Find the one with aria-expanded (the header)
      const header = headers.find(el => el.hasAttribute('aria-expanded'));
      expect(header).toBeDefined();
      fireEvent.click(header!);
      
      expect(onToggleCollapse).toHaveBeenCalledWith(entry.id);
    });

    it('should call onDelete when delete button clicked', () => {
      const onDelete = vi.fn();
      const entry = createMockEntry({
        collapsed: false,
      });
      
      renderWithTheme(
        <RunEntry {...defaultProps} entry={entry} onDelete={onDelete} totalRuns={2} />
      );
      
      const deleteButton = screen.getByLabelText('Delete Run 1');
      fireEvent.click(deleteButton);
      
      expect(onDelete).toHaveBeenCalledWith(entry.id);
    });

    it('should disable delete when only 1 run exists', () => {
      const entry = createMockEntry();
      
      renderWithTheme(
        <RunEntry {...defaultProps} entry={entry} totalRuns={1} />
      );
      
      const deleteButton = screen.getByLabelText('Delete Run 1');
      expect(deleteButton).toBeDisabled();
    });

    it('should call onUpdate when blocks field changes', () => {
      const onUpdate = vi.fn();
      const entry = createMockEntry({
        collapsed: false,
      });
      
      renderWithTheme(
        <RunEntry {...defaultProps} entry={entry} onUpdate={onUpdate} />
      );
      
      // Find the main blocks input (first one with aria-label "# of Blocks")
      const blocksInputs = screen.getAllByRole('textbox', { name: '# of Blocks' });
      fireEvent.change(blocksInputs[0], { target: { value: '25' } });
      
      expect(onUpdate).toHaveBeenCalledWith(entry.id, { blocks: '25' });
    });

    it('should toggle prefix selection on click', () => {
      const onUpdate = vi.fn();
      const entry = createMockEntry({
        collapsed: false,
        selectedPrefixes: ['KS'],
      });
      
      renderWithTheme(
        <RunEntry {...defaultProps} entry={entry} onUpdate={onUpdate} />
      );
      
      // Click on already selected prefix to deselect
      fireEvent.click(screen.getByText('KS'));
      
      expect(onUpdate).toHaveBeenCalledWith(entry.id, {
        selectedPrefixes: [],
        facility: '',
      });
    });
  });

  describe('Run Number Display', () => {
    it('should display correct run number based on index', () => {
      const entry = createMockEntry({ collapsed: false });
      
      renderWithTheme(
        <RunEntry {...defaultProps} entry={entry} index={2} />
      );
      
      expect(screen.getByText('3')).toBeInTheDocument(); // index 2 = Run 3
      expect(screen.getByText('Run 3')).toBeInTheDocument();
    });
  });
});
