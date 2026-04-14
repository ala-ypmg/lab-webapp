/**
 * T04 — PathologistAutocomplete
 *
 * Reusable autocomplete combo box for pathologist selection.
 * Props:
 *   source         — "all" | "bone_marrow"  (which list to use)
 *   allowFreetext  — when true, unrecognized input is accepted as-is
 *   value          — controlled string | null
 *   onChange       — (value: string | null) => void
 *   disabled       — optional disable flag
 *   label          — field label
 */
import { Autocomplete, TextField } from '@mui/material';
import { useMemo } from 'react';
import { MD_LIST, BONE_MARROW_ELIGIBLE } from '../data/mdList.ts';
import type { MdEntry } from '../types/index.ts';

interface PathologistAutocompleteProps {
  source: 'all' | 'bone_marrow';
  allowFreetext?: boolean;
  value: string | null;
  onChange: (value: string | null) => void;
  disabled?: boolean;
  label?: string;
  error?: boolean;
  helperText?: string;
}

export default function PathologistAutocomplete({
  source,
  allowFreetext = false,
  value,
  onChange,
  disabled = false,
  label = 'Pathologist',
  error = false,
  helperText,
}: PathologistAutocompleteProps) {
  const options: MdEntry[] = useMemo(
    () => (source === 'bone_marrow' ? BONE_MARROW_ELIGIBLE : MD_LIST),
    [source]
  );

  const optionLabels = useMemo(() => options.map((o) => o.display_name), [options]);

  return (
    <Autocomplete
      freeSolo={allowFreetext}
      options={optionLabels}
      value={value ?? ''}
      disabled={disabled}
      filterOptions={(opts, state) => {
        const q = state.inputValue.toLowerCase();
        return opts.filter((o) => o.toLowerCase().includes(q));
      }}
      onChange={(_e, newVal) => {
        onChange(newVal || null);
      }}
      onInputChange={(_e, _newInput, reason) => {
        if (reason === 'clear') onChange(null);
      }}
      onBlur={(e) => {
        if (!allowFreetext) return;
        const inputVal = (e.target as HTMLInputElement).value.trim() || null;
        onChange(inputVal);
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          label={label}
          size="small"
          error={error}
          helperText={helperText}
          placeholder="Search…"
        />
      )}
      size="small"
      sx={{ minWidth: 180 }}
    />
  );
}
