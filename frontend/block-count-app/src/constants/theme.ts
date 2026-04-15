/**
 * MUI Theme Configuration with YPMG Brand Colors
 */

import { createTheme, type ThemeOptions } from '@mui/material/styles';

/**
 * YPMG Brand Color Palette
 */
export const colors = {
  /** Navy Blue - primary actions, headers */
  primary: '#17406a',
  /** Hover states */
  primaryLight: '#3d6a99',
  /** Emphasis, grand total */
  primaryDark: '#0f2d4a',
  /** Blue Grey 600 - secondary text, icons */
  secondary: '#546e7a',
  /** Page background */
  background: '#f5f7f8',
  /** Cards */
  surface: '#ffffff',
  /** Delete actions */
  error: '#c62828',
  /** Completed states, checkmarks */
  success: '#2e7d32',
  /** Dividers, input borders */
  border: '#e0e0e0',
  /** Text colors */
  text: {
    primary: '#212121',
    secondary: '#757575',
  },
} as const;

/**
 * Theme options configuration
 */
const themeOptions: ThemeOptions = {
  palette: {
    primary: {
      main: colors.primary,
      light: colors.primaryLight,
      dark: colors.primaryDark,
    },
    secondary: {
      main: colors.secondary,
    },
    error: {
      main: colors.error,
    },
    success: {
      main: colors.success,
    },
    background: {
      default: colors.background,
      paper: colors.surface,
    },
    divider: colors.border,
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    // Prevent iOS zoom on input focus
    body1: {
      fontSize: '16px',
    },
    body2: {
      fontSize: '14px',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          minHeight: 48, // Touch target minimum
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          minHeight: 36,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiInputBase-input': {
            fontSize: '16px', // Prevent iOS zoom
          },
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          minWidth: 48, // Touch target minimum
          minHeight: 48,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
        },
      },
    },
    MuiAccordion: {
      styleOverrides: {
        root: {
          borderRadius: '8px !important',
          '&:before': {
            display: 'none',
          },
          boxShadow: 'none',
          border: `1px solid ${colors.border}`,
        },
      },
    },
    MuiAccordionSummary: {
      styleOverrides: {
        root: {
          minHeight: 48,
          '&.Mui-expanded': {
            minHeight: 48,
          },
        },
      },
    },
  },
  shape: {
    borderRadius: 8,
  },
};

/**
 * MUI Theme with YPMG brand customizations
 */
export const theme = createTheme(themeOptions);

export default theme;
