import React from 'react';
import { Grid, Paper, Typography, Rating } from '@mui/material';
import { TimelineChart, ComparisonMatrix, SearchPanel } from './charts';
import { LitScoreCard, TextAnalysis, LinguisticPanel } from './analysis';

interface TamilLitDashboardProps {
  selectedEra?: string;
  searchQuery?: string;
}

const TamilLitDashboard: React.FC<TamilLitDashboardProps> = ({ selectedEra, searchQuery }) => {
  return (
    <Grid container spacing={3}>
      {/* Time Period Insight Grid */}
      <Grid item xs={12} md={6}>
        <Paper elevation={3} className="dashboard-card">
          <Typography variant="h6">காலக்கட்ட விவரம் | Time Period Insights</Typography>
          <TimelineChart 
            era={selectedEra || "சங்க காலம்"}
            timeframe="BCE 300 - CE 300"
            authors={[
              "கபிலர்",
              "ஔவையார்",
              "நக்கீரர்"
            ]}
            themes={[
              "அகம் (Love)",
              "புறம் (War/Heroism)",
              "இயற்கை (Nature)"
            ]}
          />
        </Paper>
      </Grid>

      {/* Textual Interpretation Grid */}
      <Grid item xs={12} md={6}>
        <Paper elevation={3} className="dashboard-card">
          <Typography variant="h6">பாடல் விளக்கம் | Text Analysis</Typography>
          <TextAnalysis
            originalText="யாமறிந்த மொழிகளிலே தமிழ்மொழி போல் இனிதாவது எங்கும் காணோம்"
            translation="Among all the languages we know, nowhere do we find one as sweet as Tamil"
            interpretation={{
              poetic: "Metaphorical comparison of language to sweetness",
              cultural: "Pride in linguistic heritage",
              contemporary: "Modern language preservation efforts"
            }}
          />
        </Paper>
      </Grid>

      {/* Linguistic Insight Grid */}
      <Grid item xs={12} md={4}>
        <Paper elevation={3} className="dashboard-card">
          <Typography variant="h6">மொழியியல் ஆய்வு | Linguistic Analysis</Typography>
          <LinguisticPanel
            rareWords={[
              {
                word: "யாம்",
                root: "Proto-Dravidian",
                modern: "நாங்கள்",
                usage: "Classical"
              }
            ]}
          />
        </Paper>
      </Grid>

      {/* AI Literary Rating Grid */}
      <Grid item xs={12} md={4}>
        <Paper elevation={3} className="dashboard-card">
          <Typography variant="h6">AI மதிப்பீடு | AI Evaluation</Typography>
          <LitScoreCard
            scores={{
              emotional: 8.5,
              philosophical: 9.0,
              narrative: 7.5,
              originality: 8.0
            }}
            justification="Deep metaphysical themes combined with sophisticated emotional expression"
          />
        </Paper>
      </Grid>

      {/* Search-Based Insight Grid */}
      <Grid item xs={12}>
        <Paper elevation={3} className="dashboard-card">
          <Typography variant="h6">தேடல் பகுப்பாய்வு | Search Analysis</Typography>
          <SearchPanel
            query={searchQuery}
            results={[]}
            onSearch={(query: string) => {
              // Implement search logic
            }}
          />
        </Paper>
      </Grid>
    </Grid>
  );
};

export default TamilLitDashboard;