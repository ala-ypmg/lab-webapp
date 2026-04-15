/**
 * YPB Daily Count Form Application
 * 
 * Mobile-first web form for the Yosemite Pathology (YPB) Check Out Department
 * to digitize their daily block count tally sheet.
 */

import { ThemeProvider, CssBaseline } from '@mui/material';
import { theme } from './constants/theme';
import YPBDailyCountForm from './components/YPBDailyCountForm';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <YPBDailyCountForm />
    </ThemeProvider>
  );
}

export default App;
