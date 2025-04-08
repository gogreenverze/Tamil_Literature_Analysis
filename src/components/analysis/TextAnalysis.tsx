import React from 'react';
import { Card, CardContent, Typography, Divider } from '@mui/material';
import { TextAnalysisData } from '../../types/literature';

interface TextAnalysisProps {
  data: TextAnalysisData;
}

export const TextAnalysis: React.FC<TextAnalysisProps> = ({ data }) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" className="tamil-text">
          {data.originalText}
        </Typography>
        <Divider sx={{ my: 2 }} />
        <Typography variant="body1">
          {data.translation}
        </Typography>
        <Typography variant="h6" sx={{ mt: 2 }}>
          Interpretation
        </Typography>
        <Typography variant="body2">
          <strong>Poetic:</strong> {data.interpretation.poetic}
        </Typography>
        <Typography variant="body2">
          <strong>Cultural:</strong> {data.interpretation.cultural}
        </Typography>
        <Typography variant="body2">
          <strong>Contemporary:</strong> {data.interpretation.contemporary}
        </Typography>
      </CardContent>
    </Card>
  );
};