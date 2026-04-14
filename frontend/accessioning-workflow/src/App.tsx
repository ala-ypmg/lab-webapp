import { ThemeProvider, CssBaseline } from '@mui/material';
import { theme } from './constants/theme.ts';
import AccessioningWorkflow from './components/AccessioningWorkflow.tsx';

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AccessioningWorkflow />
    </ThemeProvider>
  );
}
