/**
 * RunEntry Component
 * 
 * Main run card component with collapsible header and form fields.
 * Displays run information in collapsed state and full form in expanded state.
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  Collapse,
  Divider,
} from '@mui/material';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import InputField from './InputField';
import PrefixChip from './PrefixChip';
import BoneMarrowSection from './BoneMarrowSection';
import AutopsyAccordion from './AutopsyAccordion';
import InfoTooltip from './InfoTooltip';
import type { RunEntryProps } from '../types';
import { TOOLTIPS } from '../constants/tooltips';
import { ALL_PREFIXES } from '../constants/facilities';
import { colors } from '../constants/theme';
import { calculateRunSubtotal, getFacilityFromPrefixes, formatTime } from '../utils';

const RunEntry: React.FC<RunEntryProps> = ({
  entry,
  index,
  totalRuns,
  onUpdate,
  onDelete,
  onToggleCollapse,
}) => {
  const runNumber = index + 1;
  const subtotal = calculateRunSubtotal(entry);
  const hasData = subtotal > 0;

  // Handle prefix toggle
  const handlePrefixToggle = (prefix: string) => {
    const newPrefixes = entry.selectedPrefixes.includes(prefix)
      ? entry.selectedPrefixes.filter((p) => p !== prefix)
      : [...entry.selectedPrefixes, prefix];
    
    const newFacility = getFacilityFromPrefixes(newPrefixes);
    onUpdate(entry.id, { selectedPrefixes: newPrefixes, facility: newFacility });
  };

  // Handle field changes
  const handleFieldChange = (field: string) => (value: string) => {
    onUpdate(entry.id, { [field]: value });
  };

  // Handle header click
  const handleHeaderClick = () => {
    onToggleCollapse(entry.id);
  };

  // Handle delete button click
  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete(entry.id);
  };

  return (
    <Card
      sx={{
        mb: 2,
        border: entry.collapsed ? `1px solid ${colors.border}` : `2px solid ${colors.primary}`,
        transition: 'all 0.2s ease-in-out',
        overflow: 'hidden',
      }}
    >
      {/* Collapsible Header */}
      <Box
        onClick={handleHeaderClick}
        sx={{
          display: 'flex',
          alignItems: 'center',
          padding: '12px 16px',
          backgroundColor: entry.collapsed ? colors.background : colors.primary,
          cursor: 'pointer',
          minHeight: 64,
          transition: 'background-color 0.2s ease-in-out',
          '&:hover': {
            backgroundColor: entry.collapsed ? colors.border : colors.primaryLight,
          },
        }}
        role="button"
        aria-expanded={!entry.collapsed}
        aria-label={entry.collapsed ? `Run #${runNumber}: ${subtotal}` : `Run ${runNumber}`}
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleHeaderClick();
          }
        }}
      >
        {/* Left side: Badge/Checkmark + Run info */}
        <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
          {entry.collapsed ? (
            // Collapsed: Show checkmark if has data
            <>
              {hasData && (
                <CheckCircleIcon
                  data-testid="CheckCircleIcon"
                  sx={{
                    color: colors.success,
                    fontSize: 24,
                    mr: 1,
                  }}
                />
              )}
              <Box sx={{ ml: hasData ? 0 : 0 }}>
                <Typography
                  variant="subtitle1"
                  sx={{
                    fontWeight: 600,
                    color: colors.text.primary,
                    fontSize: '15px',
                  }}
                >
                  Run #{runNumber}: {subtotal}
                </Typography>
                {entry.facility && (
                  <Typography
                    variant="caption"
                    sx={{
                      color: colors.text.secondary,
                      display: 'block',
                      fontSize: '12px',
                    }}
                  >
                    {entry.facility}
                  </Typography>
                )}
              </Box>
            </>
          ) : (
            // Expanded: Show circular badge with run number
            <>
              <Box
                sx={{
                  width: 32,
                  height: 32,
                  borderRadius: '50%',
                  backgroundColor: '#ffffff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mr: 1.5,
                }}
              >
                <Typography
                  variant="subtitle2"
                  sx={{
                    fontWeight: 700,
                    color: colors.primary,
                    fontSize: '14px',
                  }}
                >
                  {runNumber}
                </Typography>
              </Box>
              <Box>
                <Typography
                  variant="subtitle1"
                  sx={{
                    fontWeight: 600,
                    color: '#ffffff',
                    fontSize: '15px',
                  }}
                >
                  Run {runNumber}
                </Typography>
                {entry.facility && (
                  <Typography
                    variant="caption"
                    sx={{
                      color: 'rgba(255, 255, 255, 0.8)',
                      display: 'block',
                      fontSize: '12px',
                    }}
                  >
                    {entry.facility}
                  </Typography>
                )}
              </Box>
            </>
          )}
        </Box>

        {/* Right side: Time (when collapsed) + Chevron + Delete */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {entry.collapsed && entry.checkoutTime && (
            <Typography
              variant="body2"
              sx={{
                color: colors.text.secondary,
                fontSize: '13px',
                mr: 1,
              }}
            >
              {formatTime(entry.checkoutTime)}
            </Typography>
          )}
          
          {/* Collapse/Expand Icon */}
          {entry.collapsed ? (
            <ChevronRightIcon
              sx={{ color: entry.collapsed ? colors.secondary : '#ffffff', fontSize: 24 }}
            />
          ) : (
            <ExpandLessIcon
              sx={{ color: entry.collapsed ? colors.secondary : '#ffffff', fontSize: 24 }}
            />
          )}
          
          {/* Delete Button */}
          <IconButton
            onClick={handleDeleteClick}
            disabled={totalRuns <= 1}
            size="small"
            sx={{
              color: entry.collapsed ? colors.error : 'rgba(255, 255, 255, 0.8)',
              opacity: totalRuns <= 1 ? 0.3 : 1,
              ml: 0.5,
              '&:hover': {
                backgroundColor: entry.collapsed
                  ? 'rgba(198, 40, 40, 0.08)'
                  : 'rgba(255, 255, 255, 0.1)',
              },
            }}
            aria-label={`Delete Run ${runNumber}`}
          >
            <DeleteOutlineIcon fontSize="small" />
          </IconButton>
        </Box>
      </Box>

      {/* Collapsible Content */}
      <Collapse in={!entry.collapsed} timeout={200}>
        <CardContent sx={{ padding: '16px !important' }}>
          {/* Prefix Chip Group */}
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
              <Typography
                variant="body2"
                sx={{
                  fontWeight: 500,
                  color: 'text.secondary',
                  fontSize: '13px',
                }}
              >
                Case Prefixes
              </Typography>
              <InfoTooltip title={TOOLTIPS.prefix} />
            </Box>
            <Box
              sx={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: 1,
              }}
            >
              {ALL_PREFIXES.map((prefix) => (
                <PrefixChip
                  key={prefix}
                  label={prefix}
                  selected={entry.selectedPrefixes.includes(prefix)}
                  onClick={() => handlePrefixToggle(prefix)}
                />
              ))}
            </Box>
          </Box>

          <Divider sx={{ mb: 2.5 }} />

          {/* Blocks + Cell Buttons Row */}
          <Box sx={{ display: 'flex', gap: 2, mb: 2.5 }}>
            <Box sx={{ flex: 1 }}>
              <InputField
                label="# of Blocks"
                value={entry.blocks}
                onChange={handleFieldChange('blocks')}
                type="number"
                placeholder="0"
                tooltip={TOOLTIPS.blocks}
              />
            </Box>
            <Box sx={{ flex: 1 }}>
              <InputField
                label="Cell Buttons"
                value={entry.cellButtons}
                onChange={handleFieldChange('cellButtons')}
                type="number"
                placeholder="0"
                tooltip={TOOLTIPS.cellButtons}
              />
            </Box>
          </Box>

          {/* Bone Marrow Section */}
          <Box sx={{ mb: 2.5 }}>
            <BoneMarrowSection
              caseNumber={entry.boneMarrowCase}
              blocks={entry.boneMarrowBlocks}
              onCaseChange={handleFieldChange('boneMarrowCase')}
              onBlocksChange={handleFieldChange('boneMarrowBlocks')}
            />
          </Box>

          {/* Autopsy Section */}
          <Box sx={{ mb: 2.5 }}>
            <AutopsyAccordion
              value={entry.autopsyBlocks}
              onChange={handleFieldChange('autopsyBlocks')}
            />
          </Box>

          {/* Checkout Time */}
          <InputField
            label="Checkout Time"
            value={entry.checkoutTime}
            onChange={handleFieldChange('checkoutTime')}
            type="time"
            tooltip={TOOLTIPS.checkoutTime}
          />
        </CardContent>
      </Collapse>
    </Card>
  );
};

export default RunEntry;
