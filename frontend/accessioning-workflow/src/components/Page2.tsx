/**
 * T13 — Page 2 shell: conditional section rendering
 *
 * Renders only the sections whose keys are in `selectedTypes`,
 * always in the fixed order defined by SECTION_ORDER.
 */
import { Box, Typography, Alert } from '@mui/material';
import type { SectionKey, FormData, SectionErrors } from '../types/index.ts';
import { useSubmitKey } from '../contexts/SubmitKeyContext.ts';
import { useShake } from '../hooks/useShake.ts';
import ClientRequests from './sections/ClientRequests.tsx';
import BoneMarrow from './sections/BoneMarrow.tsx';
import FrozenSection from './sections/FrozenSection.tsx';
import StatCases from './sections/StatCases.tsx';
import HeldCases from './sections/HeldCases.tsx';

const SECTION_ORDER: SectionKey[] = [
  'client_requests',
  'bone_marrow',
  'frozen_section',
  'stat_cases',
  'held_cases',
];

interface Page2Props {
  selectedTypes: Set<SectionKey>;
  formData: FormData;
  onFormDataChange: (key: SectionKey, rows: FormData[SectionKey]) => void;
  sectionErrors?: SectionErrors;
  pageError?: string;
}

export default function Page2({
  selectedTypes,
  formData,
  onFormDataChange,
  sectionErrors = {},
  pageError,
}: Page2Props) {
  const submitKey = useSubmitKey();
  const pageErrorShakeClass = useShake(!!pageError, submitKey);
  if (selectedTypes.size === 0) {
    return (
      <Box sx={{ maxWidth: 600, mx: 'auto', px: 2, py: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          No case types selected.
        </Typography>
        <Typography variant="body2" color="text.secondary" mt={1}>
          Please go back to Page 1 and select at least one case type.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 900, mx: 'auto', px: 2, py: 3 }}>
      <Typography variant="h5" fontWeight={700} gutterBottom>
        Case Entry
      </Typography>

      {pageError && (
        <div className={pageErrorShakeClass}>
          <Alert severity="error" sx={{ mb: 2 }}>
            {pageError}
          </Alert>
        </div>
      )}

      {SECTION_ORDER.filter((key) => selectedTypes.has(key)).map((key) => {
        switch (key) {
          case 'client_requests':
            return (
              <ClientRequests
                key={key}
                rows={formData.client_requests}
                onChange={(rows) => onFormDataChange('client_requests', rows)}
                errors={sectionErrors['client_requests']}
              />
            );
          case 'bone_marrow':
            return (
              <BoneMarrow
                key={key}
                rows={formData.bone_marrow}
                onChange={(rows) => onFormDataChange('bone_marrow', rows)}
                errors={sectionErrors['bone_marrow']}
              />
            );
          case 'frozen_section':
            return (
              <FrozenSection
                key={key}
                rows={formData.frozen_section}
                onChange={(rows) => onFormDataChange('frozen_section', rows)}
                errors={sectionErrors['frozen_section']}
              />
            );
          case 'stat_cases':
            return (
              <StatCases
                key={key}
                rows={formData.stat_cases}
                onChange={(rows) => onFormDataChange('stat_cases', rows)}
                errors={sectionErrors['stat_cases']}
              />
            );
          case 'held_cases':
            return (
              <HeldCases
                key={key}
                rows={formData.held_cases}
                onChange={(rows) => onFormDataChange('held_cases', rows)}
                errors={sectionErrors['held_cases']}
              />
            );
        }
      })}
    </Box>
  );
}
