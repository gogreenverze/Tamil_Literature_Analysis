"""
Script to generate a complete Thirukkural dataset with all 1330 verses.
This script fetches data from various sources and combines them into a single JSON file.
"""

import json
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

try:
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("Required dependencies not available. Please install them with:")
    print("pip install requests beautifulsoup4 pandas")
    exit(1)

# Define the structure of the Thirukkural
THIRUKKURAL_STRUCTURE = {
    "sections": [
        {
            "name": "அறத்துப்பால்",
            "name_english": "Virtue",
            "chapters": [
                {"name": "கடவுள் வாழ்த்து", "name_english": "Praise of God", "start": 1, "end": 10},
                {"name": "வான்சிறப்பு", "name_english": "The Excellence of Rain", "start": 11, "end": 20},
                # Add all 38 chapters of Virtue section
                {"name": "அன்புடைமை", "name_english": "Possession of Love", "start": 71, "end": 80},
                {"name": "விருந்தோம்பல்", "name_english": "Hospitality", "start": 81, "end": 90},
                # ... more chapters
            ]
        },
        {
            "name": "பொருட்பால்",
            "name_english": "Wealth",
            "chapters": [
                {"name": "அரசியல்", "name_english": "Royalty", "start": 381, "end": 390},
                {"name": "கல்வி", "name_english": "Learning", "start": 391, "end": 400},
                # Add all 70 chapters of Wealth section
                # ... more chapters
            ]
        },
        {
            "name": "காமத்துப்பால்",
            "name_english": "Love",
            "chapters": [
                {"name": "தகையணங்குறுத்தல்", "name_english": "The Beauty of the Lady", "start": 1081, "end": 1090},
                {"name": "குறிப்பறிதல்", "name_english": "Recognition of the Signs", "start": 1091, "end": 1100},
                # Add all 25 chapters of Love section
                {"name": "ஊடலுவகை", "name_english": "The Joy of Reconciliation", "start": 1321, "end": 1330},
            ]
        }
    ]
}

def fetch_kural_from_api(kural_id: int) -> Dict[str, Any]:
    """
    Fetch a Kural from an API.
    
    Args:
        kural_id: The ID of the Kural to fetch.
        
    Returns:
        Dictionary with Kural data.
    """
    try:
        # Try multiple APIs for redundancy
        apis = [
            f"https://api-thirukkural.vercel.app/api?num={kural_id}",
            f"https://api.tamildictionary.org/api/thirukkural/{kural_id}"
        ]
        
        for api_url in apis:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                return data
        
        # If all APIs fail, return a minimal structure
        return {
            "number": kural_id,
            "line1": "",
            "line2": "",
            "translation": "",
            "explanation": ""
        }
    except Exception as e:
        print(f"Error fetching Kural {kural_id} from API: {e}")
        return {
            "number": kural_id,
            "line1": "",
            "line2": "",
            "translation": "",
            "explanation": ""
        }

def scrape_kural_from_web(kural_id: int) -> Dict[str, Any]:
    """
    Scrape a Kural from a website.
    
    Args:
        kural_id: The ID of the Kural to scrape.
        
    Returns:
        Dictionary with Kural data.
    """
    try:
        # Try multiple websites for redundancy
        urls = [
            f"https://www.thirukkural.com/kural/{kural_id}",
            f"https://thirukkural133.com/kural-{kural_id}"
        ]
        
        for url in urls:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Extract data based on the website structure
                # This is a simplified example and would need to be adapted for each website
                tamil_text = soup.find("div", class_="tamil-text").text.strip()
                english_translation = soup.find("div", class_="english-translation").text.strip()
                explanation = soup.find("div", class_="explanation").text.strip()
                
                return {
                    "number": kural_id,
                    "tamil": tamil_text,
                    "english": english_translation,
                    "explanation": explanation
                }
        
        # If all websites fail, return a minimal structure
        return {
            "number": kural_id,
            "tamil": "",
            "english": "",
            "explanation": ""
        }
    except Exception as e:
        print(f"Error scraping Kural {kural_id} from web: {e}")
        return {
            "number": kural_id,
            "tamil": "",
            "english": "",
            "explanation": ""
        }

def get_chapter_info(kural_id: int) -> Dict[str, str]:
    """
    Get the chapter information for a Kural.
    
    Args:
        kural_id: The ID of the Kural.
        
    Returns:
        Dictionary with chapter information.
    """
    for section in THIRUKKURAL_STRUCTURE["sections"]:
        for chapter in section["chapters"]:
            if chapter["start"] <= kural_id <= chapter["end"]:
                return {
                    "section": section["name"],
                    "section_english": section["name_english"],
                    "chapter": chapter["name"],
                    "chapter_english": chapter["name_english"],
                    "number": kural_id - chapter["start"] + 1
                }
    
    # If not found, return default values
    return {
        "section": "",
        "section_english": "",
        "chapter": "",
        "chapter_english": "",
        "number": kural_id
    }

def generate_keywords(kural: Dict[str, Any]) -> List[str]:
    """
    Generate keywords for a Kural based on its content.
    
    Args:
        kural: Dictionary with Kural data.
        
    Returns:
        List of keywords.
    """
    # Extract words from the English translation and explanation
    english_text = f"{kural.get('english', '')} {kural.get('explanation_english', '')}"
    
    # Remove punctuation and convert to lowercase
    english_text = re.sub(r'[^\w\s]', ' ', english_text.lower())
    
    # Split into words and filter out common words and short words
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'of', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'shall', 'should', 'can', 'could', 'may', 'might', 'must', 'that', 'this', 'these', 'those', 'it', 'its', 'they', 'them', 'their', 'he', 'him', 'his', 'she', 'her', 'hers', 'we', 'us', 'our', 'you', 'your', 'yours', 'who', 'whom', 'whose', 'which', 'what', 'when', 'where', 'why', 'how'}
    
    words = [word for word in english_text.split() if word not in common_words and len(word) > 3]
    
    # Get the most frequent words
    word_counts = {}
    for word in words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    # Sort by frequency and take the top 10
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    keywords = [word for word, count in sorted_words[:10]]
    
    # Add Tamil keywords if available
    tamil_text = f"{kural.get('tamil', '')} {kural.get('explanation_tamil', '')}"
    tamil_words = re.findall(r'[\u0B80-\u0BFF]+', tamil_text)
    tamil_keywords = [word for word in tamil_words if len(word) > 2][:5]
    
    # Combine English and Tamil keywords
    all_keywords = keywords + tamil_keywords
    
    # Add chapter-related keywords
    chapter_english = kural.get("chapter_english", "").lower()
    if chapter_english:
        all_keywords.append(chapter_english)
        # Add synonyms for common chapter themes
        if "love" in chapter_english:
            all_keywords.extend(["affection", "compassion", "அன்பு"])
        elif "friendship" in chapter_english:
            all_keywords.extend(["friend", "companion", "நட்பு"])
        elif "virtue" in chapter_english or "good" in chapter_english:
            all_keywords.extend(["ethics", "moral", "அறம்"])
        # Add more theme-based keywords as needed
    
    # Remove duplicates and return
    return list(set(all_keywords))

def create_complete_kural_dataset(output_path: str, use_api: bool = True, use_web: bool = True):
    """
    Create a complete Thirukkural dataset with all 1330 verses.
    
    Args:
        output_path: Path to save the output JSON file.
        use_api: Whether to use API sources.
        use_web: Whether to use web scraping.
    """
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Initialize the dataset
    dataset = {
        "metadata": {
            "total_kurals": 1330,
            "sections": 3,
            "chapters": 133,
            "kurals_per_chapter": 10
        },
        "kurals": []
    }
    
    # Check if an existing dataset is available to use as a base
    existing_kurals = {}
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                for kural in existing_data.get("kurals", []):
                    existing_kurals[kural.get("id")] = kural
        except Exception as e:
            print(f"Error loading existing dataset: {e}")
    
    # Generate data for all 1330 Kurals
    for kural_id in range(1, 1331):
        print(f"Processing Kural {kural_id}...")
        
        # Check if we already have this Kural in the existing dataset
        if kural_id in existing_kurals:
            dataset["kurals"].append(existing_kurals[kural_id])
            continue
        
        # Get chapter information
        chapter_info = get_chapter_info(kural_id)
        
        # Initialize Kural data
        kural_data = {
            "id": kural_id,
            "section": chapter_info["section"],
            "section_english": chapter_info["section_english"],
            "chapter": chapter_info["chapter"],
            "chapter_english": chapter_info["chapter_english"],
            "number": chapter_info["number"],
            "tamil": "",
            "english": "",
            "explanation_tamil": "",
            "explanation_english": ""
        }
        
        # Fetch data from API if enabled
        if use_api:
            api_data = fetch_kural_from_api(kural_id)
            if api_data:
                # Map API data to our structure
                kural_data["tamil"] = f"{api_data.get('line1', '')}\n{api_data.get('line2', '')}"
                kural_data["english"] = api_data.get('translation', '')
                kural_data["explanation_english"] = api_data.get('explanation', '')
        
        # Scrape data from web if enabled and API data is incomplete
        if use_web and (not kural_data["tamil"] or not kural_data["english"]):
            web_data = scrape_kural_from_web(kural_id)
            if web_data:
                # Map web data to our structure
                if not kural_data["tamil"]:
                    kural_data["tamil"] = web_data.get('tamil', '')
                if not kural_data["english"]:
                    kural_data["english"] = web_data.get('english', '')
                if not kural_data["explanation_english"]:
                    kural_data["explanation_english"] = web_data.get('explanation', '')
        
        # Generate keywords
        kural_data["keywords"] = generate_keywords(kural_data)
        
        # Add to dataset
        dataset["kurals"].append(kural_data)
        
        # Save the dataset after every 10 Kurals to avoid losing progress
        if kural_id % 10 == 0:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(dataset, f, ensure_ascii=False, indent=2)
            
            # Add a small delay to avoid overwhelming the APIs
            time.sleep(1)
    
    # Final save
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    print(f"Complete Thirukkural dataset saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Generate a complete Thirukkural dataset.')
    parser.add_argument('--output', type=str, default='valluvarai/kural_data/kural_1330.json',
                        help='Path to save the output JSON file')
    parser.add_argument('--no-api', action='store_true',
                        help='Disable API sources')
    parser.add_argument('--no-web', action='store_true',
                        help='Disable web scraping')
    
    args = parser.parse_args()
    
    create_complete_kural_dataset(args.output, not args.no_api, not args.no_web)

if __name__ == "__main__":
    main()
