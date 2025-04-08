import React, { useState } from 'react';
import { TextField, Button, CircularProgress, List, ListItem } from '@mui/material';
import { useTextSearch } from '../hooks/useLiteratureData';

interface SearchPanelProps {
  initialQuery?: string;
}

export const SearchPanel: React.FC<SearchPanelProps> = ({ initialQuery = '' }) => {
  const [query, setQuery] = useState(initialQuery);
  const { results, loading, error, searchText } = useTextSearch();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    searchText(query);
  };

  return (
    <div className="search-panel">
      <form onSubmit={handleSearch}>
        <TextField
          fullWidth
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search Tamil Literature..."
          variant="outlined"
        />
        <Button 
          type="submit" 
          variant="contained" 
          disabled={loading}
          sx={{ mt: 2 }}
        >
          {loading ? <CircularProgress size={24} /> : 'Search'}
        </Button>
      </form>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <List>
        {results.map((result, index) => (
          <ListItem key={index} divider>
            <div className="search-result">
              <div className="tamil-text">{result.text}</div>
              <div className="translation">{result.translation}</div>
              <div className="source">{result.source}</div>
            </div>
          </ListItem>
        ))}
      </List>
    </div>
  );
};