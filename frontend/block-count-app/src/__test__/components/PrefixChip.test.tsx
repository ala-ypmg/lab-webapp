/**
 * PrefixChip Component Tests
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider } from '@mui/material';
import PrefixChip from '../../components/PrefixChip';
import { theme } from '../../constants/theme';

const renderWithTheme = (component: React.ReactNode) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('PrefixChip', () => {
  it('should render with correct label', () => {
    renderWithTheme(
      <PrefixChip label="KS" selected={false} onClick={() => {}} />
    );
    expect(screen.getByText('KS')).toBeInTheDocument();
  });

  it('should show selected state when selected prop is true', () => {
    renderWithTheme(
      <PrefixChip label="KS" selected={true} onClick={() => {}} />
    );
    const chip = screen.getByRole('button');
    expect(chip).toHaveAttribute('aria-pressed', 'true');
  });

  it('should show unselected state when selected prop is false', () => {
    renderWithTheme(
      <PrefixChip label="KS" selected={false} onClick={() => {}} />
    );
    const chip = screen.getByRole('button');
    expect(chip).toHaveAttribute('aria-pressed', 'false');
  });

  it('should call onClick handler when clicked', () => {
    const handleClick = vi.fn();
    renderWithTheme(
      <PrefixChip label="KS" selected={false} onClick={handleClick} />
    );
    fireEvent.click(screen.getByText('KS'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('should be accessible via keyboard - Enter key triggers click', () => {
    const handleClick = vi.fn();
    renderWithTheme(
      <PrefixChip label="KS" selected={false} onClick={handleClick} />
    );
    const chip = screen.getByRole('button');
    fireEvent.keyDown(chip, { key: 'Enter' });
    // Note: MUI Chip handles Enter key natively, so onClick is called
    expect(handleClick).toHaveBeenCalled();
  });

  it('should be accessible via keyboard - Space key triggers click', () => {
    const handleClick = vi.fn();
    renderWithTheme(
      <PrefixChip label="KS" selected={false} onClick={handleClick} />
    );
    const chip = screen.getByRole('button');
    fireEvent.keyDown(chip, { key: ' ' });
    // Note: MUI Chip handles Space key natively, so onClick is called
    expect(handleClick).toHaveBeenCalled();
  });

  it('should have tabIndex for keyboard navigation', () => {
    renderWithTheme(
      <PrefixChip label="KS" selected={false} onClick={() => {}} />
    );
    const chip = screen.getByRole('button');
    expect(chip).toHaveAttribute('tabindex', '0');
  });

  it('should render different labels correctly', () => {
    const { rerender } = renderWithTheme(
      <PrefixChip label="VVS" selected={false} onClick={() => {}} />
    );
    expect(screen.getByText('VVS')).toBeInTheDocument();

    rerender(
      <ThemeProvider theme={theme}>
        <PrefixChip label="TC-KPO" selected={false} onClick={() => {}} />
      </ThemeProvider>
    );
    expect(screen.getByText('TC-KPO')).toBeInTheDocument();
  });
});
