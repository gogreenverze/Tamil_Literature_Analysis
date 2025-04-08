import axios from 'axios';
import { TimelineData, TextAnalysisData, SearchResult } from '../types/literature';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:3000/api';

export const literatureApi = {
  async getTimelineData(era: string): Promise<TimelineData> {
    try {
      const response = await axios.get(`${API_BASE_URL}/timeline/${era}`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch timeline data');
    }
  },

  async searchLiterature(query: string): Promise<SearchResult[]> {
    try {
      const response = await axios.get(`${API_BASE_URL}/search`, {
        params: { q: query }
      });
      return response.data;
    } catch (error) {
      throw new Error('Search failed');
    }
  },

  async getTextAnalysis(textId: string): Promise<TextAnalysisData> {
    try {
      const response = await axios.get(`${API_BASE_URL}/analysis/${textId}`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch text analysis');
    }
  }
};