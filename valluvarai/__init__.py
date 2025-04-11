"""
ValluvarAI - An AI-powered storytelling & literary companion for Tamil ethics, emotions, and culture.
"""

from valluvarai.agents.kural_matcher import KuralMatcher
from valluvarai.agents.story_generator import StoryGenerator
from valluvarai.agents.image_prompt_builder import ImagePromptBuilder
from valluvarai.agents.narration_engine import NarrationEngine
from valluvarai.services.image_generator import ImageGenerator
from valluvarai.services.video_builder import VideoBuilder
from valluvarai.services.insight_engine import InsightEngine

class KuralAgent:
    """Main agent class that orchestrates the ValluvarAI functionality."""

    def __init__(self):
        self.kural_matcher = KuralMatcher()
        self.story_generator = StoryGenerator()
        self.image_prompt_builder = ImagePromptBuilder()
        self.narration_engine = NarrationEngine()
        self.image_generator = ImageGenerator()
        self.video_builder = VideoBuilder()
        self.insight_engine = InsightEngine()

    def tell_story(self, keyword, include_images=True, include_video=False, language="both"):
        """
        Generate a story based on a keyword.

        Args:
            keyword (str): The keyword to search for (in English or Tamil)
            include_images (bool): Whether to generate images for the story
            include_video (bool): Whether to generate a video for the story
            language (str): Language for the story ("tamil", "english", or "both")

        Returns:
            dict: A dictionary containing the generated content
        """
        # Find relevant Kural
        kural_id, kural_text, kural_translation = self.kural_matcher.find_kural(keyword)

        # Generate story
        tamil_story, english_story = self.story_generator.generate_story(
            kural_id, kural_text, kural_translation, language
        )

        # Generate literary analysis
        analysis_result = self.insight_engine.analyze(kural_id, kural_text, kural_translation)

        # Extract the analysis from the result
        analysis = analysis_result.get("analysis", {
            "historical_context": "Analysis not available. Please check your API configuration.",
            "linguistic_analysis": "Analysis not available. Please check your API configuration.",
            "philosophical_depth": "Analysis not available. Please check your API configuration.",
            "contemporary_relevance": "Analysis not available. Please check your API configuration.",
            "emotional_resonance": "Analysis not available. Please check your API configuration."
        })

        result = {
            "kural_id": kural_id,
            "kural_text": kural_text,
            "kural_translation": kural_translation,
            "tamil_story": tamil_story,
            "english_story": english_story,
            "analysis": analysis,
            "images": [],
            "audio": {},
            "video": None
        }

        # Generate images if requested
        if include_images:
            image_prompts = self.image_prompt_builder.build_prompts(
                tamil_story, english_story, kural_text, kural_translation
            )
            result["images"] = self.image_generator.generate_images(image_prompts)

        # Generate audio narration
        if tamil_story:
            result["audio"]["tamil"] = self.narration_engine.generate_audio(tamil_story, "tamil")
        if english_story:
            result["audio"]["english"] = self.narration_engine.generate_audio(english_story, "english")

        # Generate video if requested
        if include_video and include_images:
            result["video"] = self.video_builder.create_video(
                result["images"],
                result["audio"],
                tamil_story if "tamil" in language else None,
                english_story if "english" in language else None
            )

        return result

__version__ = "0.1.0"
