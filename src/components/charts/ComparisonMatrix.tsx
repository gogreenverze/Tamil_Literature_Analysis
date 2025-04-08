import React from 'react';
import { Grid, Paper, Typography } from '@mui/material';

interface ComparisonData {
  text1: string;
  text2: string;
  commonalities: string[];
  differences: string[];
  modernContext: string;
}

interface ComparisonMatrixProps {
  data: ComparisonData;
}

export const ComparisonMatrix: React.FC<ComparisonMatrixProps> = ({ data }) => {
  return (
    <Grid container spacing={2}>
      <Grid item xs={6}>
        <Paper className="comparison-cell">
          <Typography variant="h6">{data.text1}</Typography>
          <ul>
            {data.commonalities.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </Paper>
      </Grid>
      <Grid item xs={6}>
        <Paper className="comparison-cell">
          <Typography variant="h6">{data.text2}</Typography>
          <ul>
            {data.differences.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </Paper>
      </Grid>
    </Grid>
  );
};