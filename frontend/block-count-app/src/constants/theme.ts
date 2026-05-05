import { createTheme, type ThemeOptions } from '@mui/material/styles';

export const colors = {
  primary: '#17406a',
  primaryLight: '#1e5183',
  primaryDark: '#102d4a',
  accent: '#e8912c',
  accentLight: '#f0a94d',
  secondary: '#5a6a7a',
  background: '#f5f7fa',
  surface: '#ffffff',
  error: '#d32f2f',
  success: '#2e7d32',
  warning: '#ed6c02',
  border: '#dde3ea',
  text: {
    primary: '#1a2332',
    secondary: '#5a6a7a',
  },
} as const;

const themeOptions: ThemeOptions = {
  palette: {
    primary: {
      main: colors.primary,
      light: colors.primaryLight,
      dark: colors.primaryDark,
    },
    secondary: {
      main: colors.accent,
    },
    error: {
      main: colors.error,
    },
    success: {
      main: colors.success,
    },
    warning: {
      main: colors.warning,
    },
    background: {
      default: colors.background,
      paper: colors.surface,
    },
    divider: colors.border,
    text: {
      primary: colors.text.primary,
      secondary: colors.text.secondary,
    },
  },
  typography: {
    fontFamily: "'Lato', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
    subtitle1: { fontWeight: 500 },
    body1: { fontSize: '16px' },
    body2: { fontSize: '14px' },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: 8,
          minHeight: 48,
        },
      },
    },
    MuiToggleButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500,
          minHeight: 36,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiInputBase-input': {
            fontSize: '16px',
          },
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          minWidth: 48,
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
};

export const theme = createTheme(themeOptions);

export default theme;
