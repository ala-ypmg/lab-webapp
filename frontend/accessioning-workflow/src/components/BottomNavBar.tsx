/**
 * T02 — Bottom navigation bar
 *
 * Persistent on all 3 pages. Contains:
 *   - Previous button (disabled on page 1)
 *   - Page dots (clickable)
 *   - Next button (pages 1–2) / Submit button (page 3)
 */
import {
  Box,
  Button,
  Paper,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import NavigateBeforeIcon from '@mui/icons-material/NavigateBefore';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import SendIcon from '@mui/icons-material/Send';
import { COLORS } from '../constants/theme.ts';

interface BottomNavBarProps {
  currentPage: 1 | 2 | 3;
  onNavigate: (page: 1 | 2 | 3) => void;
  canProceed: boolean;      // false → Next is disabled on page 1
  proceedTooltip?: string;  // shown when canProceed=false
  isSubmitting?: boolean;
}

export default function BottomNavBar({
  currentPage,
  onNavigate,
  canProceed,
  proceedTooltip,
  isSubmitting = false,
}: BottomNavBarProps) {
  const isFirst = currentPage === 1;
  const isLast = currentPage === 3;

  return (
    <Paper
      elevation={4}
      sx={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: 1200,
        px: 2,
        py: 1.5,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderTop: `1px solid ${COLORS.border}`,
      }}
    >
      {/* Previous */}
      <Button
        variant="outlined"
        startIcon={<NavigateBeforeIcon />}
        disabled={isFirst}
        onClick={() => onNavigate((currentPage - 1) as 1 | 2 | 3)}
      >
        Previous
      </Button>

      {/* Page dots */}
      <Box display="flex" gap={1} alignItems="center">
        {([1, 2, 3] as const).map((p) => (
          <Box
            key={p}
            onClick={() => onNavigate(p)}
            sx={{
              width: 10,
              height: 10,
              borderRadius: '50%',
              cursor: 'pointer',
              bgcolor: p === currentPage ? 'primary.main' : 'grey.300',
              border: p === currentPage ? '2px solid' : '2px solid transparent',
              borderColor: p === currentPage ? 'primary.main' : 'transparent',
              transition: 'background-color 0.2s',
              '&:hover': { bgcolor: p === currentPage ? 'primary.dark' : 'grey.400' },
            }}
            role="button"
            aria-label={`Go to page ${p}`}
          />
        ))}
      </Box>

      {/* Next / Submit */}
      {isLast ? (
        <Button
          variant="contained"
          color="primary"
          endIcon={isSubmitting ? <CircularProgress size={16} color="inherit" /> : <SendIcon />}
          disabled={isSubmitting}
          onClick={() => onNavigate(3)}
          form="accessioning-submit"
        >
          {isSubmitting ? 'Submitting…' : 'Submit'}
        </Button>
      ) : (
        <Tooltip title={!canProceed && proceedTooltip ? proceedTooltip : ''} arrow>
          <span>
            <Button
              variant="contained"
              endIcon={<NavigateNextIcon />}
              disabled={!canProceed}
              onClick={() => onNavigate((currentPage + 1) as 2 | 3)}
            >
              Next
            </Button>
          </span>
        </Tooltip>
      )}
    </Paper>
  );
}
