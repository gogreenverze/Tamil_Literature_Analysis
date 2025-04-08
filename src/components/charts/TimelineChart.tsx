import React from 'react';
import { Timeline, TimelineItem, TimelineSeparator, TimelineContent } from '@mui/lab';
import { TimelineData } from '../../types/literature';
import { CircularProgress, Alert } from '@mui/material';

interface TimelineChartProps {
  data?: TimelineData;
  loading?: boolean;
  error?: string;
}

export const TimelineChart: React.FC<TimelineChartProps> = ({ data, loading, error }) => {
  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;
  if (!data) return null;

  return (
    <Timeline>
      <TimelineItem>
        <TimelineSeparator />
        <TimelineContent>
          <h4>{data.era}</h4>
          <p>{data.timeframe}</p>
          <div className="authors-list">
            {data.authors.map((author, index) => (
              <span key={index} className="tamil-text">{author}</span>
            ))}
          </div>
          <div className="themes-list">
            {data.themes.map((theme, index) => (
              <span key={index} className="theme-tag">{theme}</span>
            ))}
          </div>
        </TimelineContent>
      </TimelineItem>
    </Timeline>
  );
};