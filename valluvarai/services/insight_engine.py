"""
Insight Engine - Provides literary analysis of Thirukkural verses.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class InsightEngine:
    """
    Provides literary analysis of Thirukkural verses.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the InsightEngine.

        Args:
            api_key: OpenAI API key. If None, uses the OPENAI_API_KEY environment variable.
            model: The OpenAI model to use for analysis.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.client = None

        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def _get_kural_details(self, kural_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a Kural from the dataset.

        Args:
            kural_id: The ID of the Kural.

        Returns:
            Dictionary with Kural details.
        """
        # Get the directory of the current file
        current_dir = Path(__file__).parent.parent
        kural_data_path = current_dir / "kural_data" / "kural_1330.json"

        try:
            with open(kural_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for kural in data["kurals"]:
                    if kural["id"] == kural_id:
                        return kural
        except Exception as e:
            print(f"Error loading Kural data: {e}")

        # Return a default Kural if not found
        return {
            "id": kural_id,
            "section": "Unknown",
            "section_english": "Unknown",
            "chapter": "Unknown",
            "chapter_english": "Unknown",
            "tamil": "",
            "english": "",
            "explanation_tamil": "",
            "explanation_english": ""
        }

    def analyze(
        self,
        kural_id: int,
        kural_text: str,
        kural_translation: str
    ) -> Dict[str, Any]:
        """
        Analyze a Thirukkural verse.

        Args:
            kural_id: The ID of the Kural.
            kural_text: The Tamil text of the Kural.
            kural_translation: The English translation of the Kural.

        Returns:
            Dictionary with analysis results.
        """
        # Get additional details about the Kural
        kural_details = self._get_kural_details(kural_id)

        # Add the text and translation to the details
        kural_details["tamil"] = kural_text
        kural_details["english"] = kural_translation

        # If OpenAI is available, use it for analysis
        if OPENAI_AVAILABLE and self.client:
            return self._analyze_with_openai(kural_details)

        # Otherwise, use a template-based approach
        return self._analyze_template(kural_details)

    def _analyze_with_openai(self, kural_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a Kural using OpenAI's API.

        Args:
            kural_details: Dictionary with Kural details.

        Returns:
            Dictionary with analysis results.
        """
        try:
            system_prompt = """
            You are a Tamil literature expert specializing in Thirukkural analysis.
            Provide a comprehensive analysis of the given Thirukkural verse in the following format:

            1. Historical Context: Explain when this concept was important in Tamil culture and history
            2. Linguistic Analysis: Analyze the poetic devices, word choices, and structure
            3. Philosophical Depth: Explain the philosophical underpinnings and ethical principles
            4. Contemporary Relevance: How this Kural applies to modern life and current issues
            5. Emotional Resonance: The emotional impact and psychological insights of this Kural

            Keep each section concise (2-3 sentences) but insightful.
            """

            user_prompt = f"""
            Thirukkural Details:
            - ID: {kural_details['id']}
            - Section: {kural_details.get('section', '')} ({kural_details.get('section_english', '')})
            - Chapter: {kural_details.get('chapter', '')} ({kural_details.get('chapter_english', '')})
            - Tamil Text: {kural_details.get('tamil', '')}
            - English Translation: {kural_details.get('english', '')}
            - Tamil Explanation: {kural_details.get('explanation_tamil', '')}
            - English Explanation: {kural_details.get('explanation_english', '')}

            Please provide a comprehensive analysis of this Thirukkural verse.
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )

            analysis_text = response.choices[0].message.content.strip()

            # Parse the analysis text into sections
            sections = {}
            current_section = None

            for line in analysis_text.split("\n"):
                line = line.strip()
                if not line:
                    continue

                # Check if this is a section header
                if line.startswith("1. Historical Context:"):
                    current_section = "historical_context"
                    sections[current_section] = line.replace("1. Historical Context:", "").strip()
                elif line.startswith("2. Linguistic Analysis:"):
                    current_section = "linguistic_analysis"
                    sections[current_section] = line.replace("2. Linguistic Analysis:", "").strip()
                elif line.startswith("3. Philosophical Depth:"):
                    current_section = "philosophical_depth"
                    sections[current_section] = line.replace("3. Philosophical Depth:", "").strip()
                elif line.startswith("4. Contemporary Relevance:"):
                    current_section = "contemporary_relevance"
                    sections[current_section] = line.replace("4. Contemporary Relevance:", "").strip()
                elif line.startswith("5. Emotional Resonance:"):
                    current_section = "emotional_resonance"
                    sections[current_section] = line.replace("5. Emotional Resonance:", "").strip()
                elif current_section:
                    sections[current_section] += " " + line

            # If parsing failed, use the raw text
            if not sections:
                sections = {
                    "raw_analysis": analysis_text
                }

            return {
                "kural_id": kural_details["id"],
                "analysis": sections
            }

        except Exception as e:
            print(f"Error analyzing with OpenAI: {e}")
            # Fall back to template-based analysis
            return self._analyze_template(kural_details)

    def _analyze_template(self, kural_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide a template-based analysis when OpenAI is not available.

        Args:
            kural_details: Dictionary with Kural details.

        Returns:
            Dictionary with analysis results.
        """
        # Get the chapter in English
        chapter_english = kural_details.get("chapter_english", "").lower()

        # Template analyses based on the chapter
        if "forgiveness" in chapter_english or "patience" in chapter_english:
            analysis = {
                "historical_context": "Forgiveness was a cornerstone virtue in ancient Tamil society, especially during the Sangam period (300 BCE to 300 CE) when conflicts between kingdoms were common. Thiruvalluvar emphasized forgiveness as a path to peace in an era of frequent warfare.",
                "linguistic_analysis": "This Kural uses contrasting imagery of strength and weakness, employing a paradox to convey that true power lies in restraint rather than retaliation. The Tamil word 'பொறை' (porai) carries deeper connotations than the English 'forgiveness,' suggesting both patience and emotional fortitude.",
                "philosophical_depth": "The verse reflects the influence of both Jain and Buddhist philosophies on Tamil ethics, particularly the concept of ahimsa (non-violence). It presents forgiveness not as passive submission but as an active choice requiring greater inner strength than revenge.",
                "contemporary_relevance": "In today's conflict-ridden world, this Kural offers wisdom for both personal relationships and international diplomacy. The principle that true strength lies in forgiveness rather than retaliation remains revolutionary in contexts from social media disputes to geopolitical tensions.",
                "emotional_resonance": "The Kural speaks to the universal human struggle between the immediate emotional satisfaction of revenge and the deeper peace that comes from letting go. It acknowledges the difficulty of forgiveness while affirming its ultimate reward of inner freedom."
            }
        elif "love" in chapter_english:
            analysis = {
                "historical_context": "The concept of selfless love was central to Tamil culture during the Sangam period, influencing both personal relationships and community structures. Thiruvalluvar's teachings on love emerged during a time when Tamil society was developing sophisticated ethical frameworks for human connections.",
                "linguistic_analysis": "This Kural employs powerful contrasting imagery between the self-centered and the loving person. The Tamil original uses the word 'எலும்பு' (elumbu/bone) metaphorically to suggest that even one's most fundamental physical structure belongs to others when one truly loves.",
                "philosophical_depth": "The verse reflects the Tamil philosophical concept of 'அன்பு' (anbu), which transcends Western notions of love to encompass a universal compassion and selflessness. It suggests that true identity is found not in self-preservation but in giving oneself to others.",
                "contemporary_relevance": "In an age of increasing individualism and self-focus, this Kural challenges modern assumptions about personal boundaries and self-care. It offers a radical alternative to consumer culture by suggesting that fulfillment comes through giving rather than acquiring.",
                "emotional_resonance": "The Kural touches on the paradoxical human experience that our greatest joy often comes when we forget ourselves in service to others. It validates the emotional truth that love expands rather than diminishes our sense of self."
            }
        elif "learning" in chapter_english or "education" in chapter_english:
            analysis = {
                "historical_context": "Education was highly valued in ancient Tamil society, with centers of learning established throughout the Tamil region during the Sangam period. Thiruvalluvar emphasized the practical application of knowledge at a time when formal education was becoming more structured.",
                "linguistic_analysis": "This Kural employs a concise, imperative structure that emphasizes both the acquisition and application of knowledge. The repetition of 'கற்க' (karka/learn) creates a rhythmic emphasis that underscores the importance of thorough learning.",
                "philosophical_depth": "The verse reflects the pragmatic orientation of Tamil ethics, which valued knowledge not for its own sake but for its transformative potential. It suggests a holistic view of education that encompasses both intellectual understanding and moral character.",
                "contemporary_relevance": "In today's information-saturated world, this Kural reminds us that true education goes beyond accumulating facts to living in accordance with what we've learned. It speaks to current educational debates about the purpose of learning and the gap between knowledge and wisdom.",
                "emotional_resonance": "The Kural addresses the universal human tendency to separate knowing from doing, challenging us to integrate our understanding into our character. It suggests that the emotional satisfaction of learning comes not from what we know but from how we live."
            }
        else:
            analysis = {
                "historical_context": f"This Kural from the chapter on {kural_details.get('chapter_english', '')} reflects the ethical priorities of Tamil society during the Sangam period (300 BCE to 300 CE). Thiruvalluvar's teachings on this subject would have provided practical guidance for daily life in ancient Tamil Nadu.",
                "linguistic_analysis": "The verse demonstrates Thiruvalluvar's characteristic economy of language, conveying profound meaning in just seven words per line. The Tamil original employs poetic devices including assonance and balanced structure to enhance memorability and impact.",
                "philosophical_depth": "This Kural reflects the practical wisdom tradition of Tamil philosophy, which sought to integrate ethical principles into everyday life. It shows influences from various philosophical traditions including indigenous Tamil thought, Jainism, and Buddhism.",
                "contemporary_relevance": "Despite being written nearly two millennia ago, this teaching remains remarkably applicable to modern challenges and ethical dilemmas. Its wisdom transcends cultural and temporal boundaries to speak to universal human experiences.",
                "emotional_resonance": "The Kural addresses fundamental human emotions and psychological insights that remain constant across generations. Its emotional impact comes from recognizing timeless human struggles and aspirations reflected in ancient wisdom."
            }

        return {
            "kural_id": kural_details["id"],
            "analysis": analysis
        }
