/**
 * InputField Component
 * 
 * A labeled input field with optional tooltip.
 * Supports text, number, and time input types.
 */

import React from 'react';
import { Box, TextField, Typography } from '@mui/material';
import InfoTooltip from './InfoTooltip';
import type { InputFieldProps } from '../types';

const InputField: React.FC<InputFieldProps> = ({
  label,
  value,
  onChange,
  type = 'text',
  tooltip,
  placeholder,
  required = false,
  sx = {},
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    
    // For number inputs, only allow valid numeric characters
    if (type === 'number') {
      if (newValue === '' || /^\d*$/.test(newValue)) {
        onChange(newValue);
      }
    } else {
      onChange(newValue);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5, ...sx }}>
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <Typography
          variant="body2"
          component="label"
          sx={{
            fontWeight: 500,
            color: 'text.secondary',
            fontSize: '13px',
          }}
        >
          {label}
          {required && (
            <Typography component="span" sx={{ color: 'error.main', ml: 0.5 }}>
              *
            </Typography>
          )}
        </Typography>
        {tooltip && <InfoTooltip title={tooltip} />}
      </Box>
      <TextField
        value={value}
        onChange={handleChange}
        type={type === 'number' ? 'text' : type}
        placeholder={placeholder}
        size="small"
        fullWidth
        slotProps={{
          htmlInput: {
            inputMode: type === 'number' ? 'numeric' : undefined,
            pattern: type === 'number' ? '[0-9]*' : undefined,
            'aria-label': label,
            'aria-required': required,
          },
          input: {
            sx: {
              fontSize: '16px', // Prevent iOS zoom
              '& input': {
                padding: '10px 12px',
              },
            },
          },
        }}
        sx={{
          '& .MuiOutlinedInput-root': {
            borderRadius: '8px',
            backgroundColor: '#ffffff',
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: 'primary.main',
            },
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: 'primary.main',
              borderWidth: 2,
            },
          },
        }}
      />
    </Box>
  );
};

export default InputField;
