"""
Kural Matcher - Finds relevant Thirukkural verses based on keywords.
"""

import json
import os
import re
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional
import random

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class KuralMatcher:
    """
    Matches keywords to relevant Thirukkural verses using semantic search.
    """
    
    def __init__(self, kural_data_path: Optional[str] = None):
        """
        Initialize the KuralMatcher.
        
        Args:
            kural_data_path: Path to the Kural data JSON file. If None, uses the default path.
        """
        if kural_data_path is None:
            # Get the directory of the current file
            current_dir = Path(__file__).parent.parent
            kural_data_path = current_dir / "kural_data" / "kural_1330.json"
        
        self.kurals = self._load_kurals(kural_data_path)
        self.vectorizer = None
        self.tfidf_matrix = None
        
        # Initialize the TF-IDF vectorizer if sklearn is available
        if SKLEARN_AVAILABLE:
            self._initialize_tfidf()
    
    def _load_kurals(self, kural_data_path: str) -> List[Dict[str, Any]]:
        """
        Load Kural data from JSON file.
        
        Args:
            kural_data_path: Path to the Kural data JSON file.
            
        Returns:
            List of Kural dictionaries.
        """
        try:
            with open(kural_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data["kurals"]
        except Exception as e:
            print(f"Error loading Kural data: {e}")
            # Return a minimal set of Kurals for fallback
            return [
                {
                    "id": 155,
                    "tamil": "இன்மையுள் இன்மை விருந்தொரால் வன்மையுள்\nவன்மை மடவார்ப் பொறை.",
                    "english": "Who with the strength of patience decked can bear with those who revile is head of all.",
                    "keywords": ["forgiveness", "patience", "strength", "tolerance", "பொறுமை", "மன்னிப்பு", "வலிமை", "பொறுத்துக்கொள்ளுதல்"]
                }
            ]
    
    def _initialize_tfidf(self):
        """Initialize the TF-IDF vectorizer with the Kural keywords."""
        if not SKLEARN_AVAILABLE:
            return
        
        # Create a corpus of keywords for each Kural
        corpus = []
        for kural in self.kurals:
            # Combine all keywords and text for better matching
            keywords = " ".join(kural.get("keywords", []))
            english = kural.get("english", "")
            tamil = kural.get("tamil", "")
            explanation_english = kural.get("explanation_english", "")
            explanation_tamil = kural.get("explanation_tamil", "")
            
            # Combine all text
            all_text = f"{keywords} {english} {tamil} {explanation_english} {explanation_tamil}"
            corpus.append(all_text)
        
        # Create TF-IDF matrix
        self.vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
    
    def find_kural(self, keyword: str) -> Tuple[int, str, str]:
        """
        Find the most relevant Kural for a given keyword.
        
        Args:
            keyword: The keyword to search for (in English or Tamil).
            
        Returns:
            Tuple of (kural_id, kural_text, kural_translation).
        """
        if SKLEARN_AVAILABLE and self.vectorizer and self.tfidf_matrix is not None:
            return self._find_kural_tfidf(keyword)
        else:
            return self._find_kural_simple(keyword)
    
    def _find_kural_tfidf(self, keyword: str) -> Tuple[int, str, str]:
        """
        Find the most relevant Kural using TF-IDF and cosine similarity.
        
        Args:
            keyword: The keyword to search for.
            
        Returns:
            Tuple of (kural_id, kural_text, kural_translation).
        """
        # Transform the keyword into the TF-IDF space
        keyword_vector = self.vectorizer.transform([keyword])
        
        # Calculate cosine similarity between the keyword and all Kurals
        similarities = cosine_similarity(keyword_vector, self.tfidf_matrix).flatten()
        
        # Get the index of the most similar Kural
        best_match_idx = np.argmax(similarities)
        best_match = self.kurals[best_match_idx]
        
        return best_match["id"], best_match["tamil"], best_match["english"]
    
    def _find_kural_simple(self, keyword: str) -> Tuple[int, str, str]:
        """
        Find the most relevant Kural using simple keyword matching.
        
        Args:
            keyword: The keyword to search for.
            
        Returns:
            Tuple of (kural_id, kural_text, kural_translation).
        """
        keyword = keyword.lower()
        matches = []
        
        for kural in self.kurals:
            # Check if the keyword is in the Kural's keywords
            kural_keywords = [k.lower() for k in kural.get("keywords", [])]
            if any(keyword in k for k in kural_keywords) or any(k in keyword for k in kural_keywords):
                matches.append(kural)
            
            # Check if the keyword is in the Kural's text or translation
            if (keyword in kural.get("english", "").lower() or 
                keyword in kural.get("tamil", "").lower() or
                keyword in kural.get("explanation_english", "").lower() or
                keyword in kural.get("explanation_tamil", "").lower()):
                matches.append(kural)
        
        # If no matches found, return a random Kural
        if not matches:
            random_kural = random.choice(self.kurals)
            return random_kural["id"], random_kural["tamil"], random_kural["english"]
        
        # Return the first match
        best_match = matches[0]
        return best_match["id"], best_match["tamil"], best_match["english"]
