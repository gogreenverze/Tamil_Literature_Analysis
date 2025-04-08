import { useState, useEffect } from 'react';
import { literatureApi } from '../services/api';
import { TimelineData, TextAnalysisData, SearchResult } from '../types/literature';

export const useLiteratureData = (era: string) => {
  const [timelineData, setTimelineData] = useState<TimelineData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await literatureApi.getTimelineData(era);
        setTimelineData(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [era]);

  return { timelineData, loading, error };
};

export const useTextSearch = () => {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const searchText = async (query: string) => {
    try {
      setLoading(true);
      const searchResults = await literatureApi.searchLiterature(query);
      setResults(searchResults);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  return { results, loading, error, searchText };
};