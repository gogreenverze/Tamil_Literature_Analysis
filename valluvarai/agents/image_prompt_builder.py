"""
Image Prompt Builder - Creates prompts for AI image generation based on stories.
"""

import re
import os
from typing import List, Optional, Dict, Any, Tuple, Union
import json

from valluvarai.config import config
from valluvarai.utils.cache import cache

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class ImagePromptBuilder:
    """
    Builds prompts for AI image generation based on stories.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the ImagePromptBuilder.

        Args:
            api_key: OpenAI API key. If None, uses the key from config.
            model: The model to use for prompt generation. If None, uses the model from config.
        """
        # Get configuration
        text_gen_config = config.get_service_config("text_generation")

        self.api_key = api_key or config.get_api_key("openai")
        self.model = model or text_gen_config.get("model", "gpt-3.5-turbo")
        self.provider = text_gen_config.get("provider", "openai")
        self.temperature = text_gen_config.get("temperature", 0.7)
        self.max_tokens = text_gen_config.get("max_tokens", 1000)
        self.fallback_to_template = text_gen_config.get("fallback_to_template", True)

        # Initialize client if possible
        self.client = None
        if OPENAI_AVAILABLE and self.api_key and self.provider == "openai":
            self.client = OpenAI(api_key=self.api_key)

        # Load additional prompt templates
        self.load_prompt_templates()

    def load_prompt_templates(self):
        """
        Load additional prompt templates from files or add more built-in templates.
        """
        # Add more theme-specific prompt templates
        self.additional_themes = {
            "gratitude": [
                "A Tamil farmer offering the first harvest to village elders as a gesture of gratitude. The scene is set in a lush green field with the golden glow of sunset. Villagers gather around with expressions of appreciation and respect. Tamil literature, photorealistic, detailed, cinematic lighting",
                "A young person touching the feet of an elderly teacher in a traditional Tamil gurukul setting. The teacher's face shows blessing while the student shows deep gratitude. Ancient manuscripts and oil lamps surround them. Tamil literature, photorealistic, detailed, cinematic lighting"
            ],
            "honesty": [
                "A Tamil merchant refusing a large bag of gold coins, choosing honesty over wealth. The scene shows a busy marketplace with onlookers watching the moral decision with admiration. Tamil literature, photorealistic, detailed, cinematic lighting",
                "A child confessing truth to parents in a humble Tamil home. The parents' faces show a mixture of pride and understanding. Warm evening light streams through the window. Tamil literature, photorealistic, detailed, cinematic lighting"
            ],
            "perseverance": [
                "A Tamil fisherwoman continuing her work despite rough seas and stormy weather. Her determined face shows the strength of character as waves crash against her boat. Tamil literature, photorealistic, detailed, cinematic lighting",
                "A student studying by oil lamp in a simple Tamil village hut, surrounded by siblings who are sleeping. The determination on the student's face shows unwavering commitment to education despite humble circumstances. Tamil literature, photorealistic, detailed, cinematic lighting"
            ],
            "compassion": [
                "A wealthy Tamil woman distributing food to the poor during a famine. Her face shows deep compassion as hungry children and elders receive the food with gratitude. Temple architecture in background. Tamil literature, photorealistic, detailed, cinematic lighting",
                "A Tamil doctor treating patients in a rural village, refusing payment from those who cannot afford it. The scene shows a simple clinic with people of various ages waiting for care. Tamil literature, photorealistic, detailed, cinematic lighting"
            ]
        }

        # Add artistic style templates
        self.artistic_styles = {
            "traditional": "traditional Tamil painting style, rich colors, detailed ornamentation, flat perspective",
            "modern": "modern digital art with Tamil cultural elements, vibrant colors, clean lines",
            "watercolor": "delicate watercolor painting with Tamil cultural elements, soft colors, flowing brushstrokes",
            "cinematic": "cinematic scene with dramatic lighting, Tamil cultural setting, movie-like composition",
            "illustration": "detailed illustration with Tamil cultural elements, storybook quality, expressive characters",
            "photorealistic": "photorealistic rendering, highly detailed, perfect lighting, Tamil cultural setting"
        }

        # Add time period templates
        self.time_periods = {
            "ancient": "ancient Tamil kingdom (300 BCE), historical accuracy, traditional architecture and clothing",
            "medieval": "medieval Tamil period (10th century), Chola dynasty influence, temple towns, traditional dress",
            "colonial": "colonial-era Tamil Nadu (19th century), blend of traditional and British influence",
            "modern": "modern-day Tamil Nadu, contemporary setting with traditional cultural elements",
            "futuristic": "futuristic Tamil society, advanced technology blended with preserved cultural traditions"
        }

    def build_prompts(
        self,
        tamil_story: Optional[str],
        english_story: Optional[str],
        kural_text: str,
        kural_translation: str,
        num_images: int = 3,
        style: str = "photorealistic",
        time_period: str = "modern",
        custom_elements: Optional[List[str]] = None
    ) -> List[str]:
        """
        Build prompts for image generation based on the story.

        Args:
            tamil_story: The Tamil story.
            english_story: The English story.
            kural_text: The Tamil text of the Kural.
            kural_translation: The English translation of the Kural.
            num_images: Number of image prompts to generate.
            style: Artistic style for the images (traditional, modern, watercolor, etc.).
            time_period: Time period for the images (ancient, medieval, modern, etc.).
            custom_elements: Custom elements to include in the prompts.

        Returns:
            List of image prompts.
        """
        # Check cache first
        cache_key = {
            "tamil_story": tamil_story,
            "english_story": english_story,
            "kural_text": kural_text,
            "kural_translation": kural_translation,
            "num_images": num_images,
            "style": style,
            "time_period": time_period,
            "custom_elements": custom_elements
        }
        cached_prompts = cache.get("image_prompts", cache_key)
        if cached_prompts:
            return cached_prompts

        # Use the English story if available, otherwise use the Tamil story
        story = english_story if english_story else tamil_story

        # Get style and time period descriptions
        style_desc = self.artistic_styles.get(style, self.artistic_styles["photorealistic"])
        period_desc = self.time_periods.get(time_period, self.time_periods["modern"])

        # Prepare custom elements
        custom_desc = ""
        if custom_elements:
            custom_desc = ", ".join(custom_elements)

        if not story:
            # If no story is available, generate generic prompts based on the Kural
            prompts = self._generate_generic_prompts(kural_text, kural_translation, num_images, style_desc, period_desc, custom_desc)
        elif OPENAI_AVAILABLE and self.client and self.provider == "openai":
            # If OpenAI is available, use it to generate prompts
            prompts = self._generate_with_openai(story, kural_translation, num_images, style_desc, period_desc, custom_desc)
        else:
            # Otherwise, use a rule-based approach
            prompts = self._generate_rule_based(story, kural_translation, num_images, style_desc, period_desc, custom_desc)

        # Cache the results
        cache.set("image_prompts", cache_key, prompts)

        return prompts

    def _generate_with_openai(self, story: str, kural_translation: str, num_images: int, style_desc: str, period_desc: str, custom_desc: str = "") -> List[str]:
        """
        Generate image prompts using OpenAI's API.

        Args:
            story: The story text.
            kural_translation: The English translation of the Kural.
            num_images: Number of image prompts to generate.
            style_desc: Description of the artistic style.
            period_desc: Description of the time period.
            custom_desc: Custom elements to include.

        Returns:
            List of image prompts.
        """
        try:
            system_prompt = """
            You are an expert at creating detailed, vivid prompts for AI image generation.
            Your task is to create prompts that capture key scenes from a story based on Thirukkural.

            Each prompt should:
            1. Be detailed and specific (50-100 words)
            2. Include visual elements like lighting, colors, and composition
            3. Capture the emotional tone of the scene
            4. Include Tamil cultural elements when appropriate
            5. Be suitable for text-to-image AI models like DALL-E or Stable Diffusion
            6. NOT include any text or writing to appear in the image
            7. Incorporate the specified artistic style and time period
            8. Include any custom elements requested
            """

            style_period_info = f"Artistic style: {style_desc}\nTime period: {period_desc}"
            if custom_desc:
                style_period_info += f"\nCustom elements to include: {custom_desc}"

            user_prompt = f"""
            Here is a story based on the Thirukkural verse: "{kural_translation}"

            Story:
            {story}

            {style_period_info}

            Please create {num_images} distinct image prompts that capture key moments or scenes from this story.
            Each prompt should be a separate paragraph and should incorporate the specified artistic style, time period, and any custom elements.
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            # Extract the prompts from the response
            content = response.choices[0].message.content.strip()

            # Split the content into separate prompts
            prompts = []
            for paragraph in content.split("\n\n"):
                if paragraph.strip():
                    # Remove any numbering or prefixes
                    clean_prompt = re.sub(r"^\d+[\.\)]\s*", "", paragraph.strip())
                    clean_prompt = re.sub(r"^Prompt \d+[\:\.\)]\s*", "", clean_prompt)
                    prompts.append(clean_prompt)

            # Ensure we have the requested number of prompts
            while len(prompts) < num_images:
                prompts.append(self._generate_generic_prompts(
                    "", kural_translation, 1, style_desc, period_desc, custom_desc
                )[0])

            return prompts[:num_images]

        except Exception as e:
            print(f"Error generating prompts with OpenAI: {e}")
            # Fall back to rule-based approach
            return self._generate_rule_based(story, kural_translation, num_images, style_desc, period_desc, custom_desc)

    def _generate_rule_based(self, story: str, kural_translation: str, num_images: int, style_desc: str, period_desc: str, custom_desc: str = "") -> List[str]:
        """
        Generate image prompts using a rule-based approach.

        Args:
            story: The story text.
            kural_translation: The English translation of the Kural.
            num_images: Number of image prompts to generate.
            style_desc: Description of the artistic style.
            period_desc: Description of the time period.
            custom_desc: Custom elements to include.

        Returns:
            List of image prompts.
        """
        # Extract key sentences from the story
        sentences = re.split(r'(?<=[.!?])\s+', story)

        # Filter out short sentences
        sentences = [s for s in sentences if len(s.split()) > 5]

        # Select sentences that might contain visual elements
        visual_sentences = []
        for sentence in sentences:
            # Look for sentences with descriptive words
            descriptive_words = ["village", "temple", "house", "field", "sea", "mountain",
                                "elderly", "young", "woman", "man", "child", "family",
                                "கிராமம்", "கோயில்", "வீடு", "வயல்", "கடல்", "மலை",
                                "முதியவர்", "இளைஞர்", "பெண்", "ஆண்", "குழந்தை", "குடும்பம்"]

            if any(word in sentence.lower() for word in descriptive_words):
                visual_sentences.append(sentence)

        # If we don't have enough visual sentences, add more from the original list
        while len(visual_sentences) < num_images and sentences:
            visual_sentences.append(sentences.pop(0))

        # Create prompts from the visual sentences
        prompts = []
        for i, sentence in enumerate(visual_sentences[:num_images]):
            # Clean the sentence
            clean_sentence = sentence.strip()

            # Add details to make it a good image prompt with style and period
            style_elements = style_desc if style_desc else "photorealistic, detailed, cinematic lighting"
            period_elements = period_desc if period_desc else "modern Tamil cultural setting"
            custom_elements = f", {custom_desc}" if custom_desc else ""

            prompt = f"{clean_sentence} Scene from a story illustrating the Thirukkural teaching: '{kural_translation}'. {period_elements}, rich colors, emotional depth, {style_elements}{custom_elements}"
            prompts.append(prompt)

        # If we still don't have enough prompts, add generic ones
        while len(prompts) < num_images:
            prompts.append(self._generate_generic_prompts(
                "", kural_translation, 1, style_desc, period_desc, custom_desc
            )[0])

        return prompts

    def _generate_generic_prompts(self, kural_text: str, kural_translation: str, num_images: int, style_desc: str = "", period_desc: str = "", custom_desc: str = "") -> List[str]:
        """
        Generate generic image prompts based on the Kural.

        Args:
            kural_text: The Tamil text of the Kural.
            kural_translation: The English translation of the Kural.
            num_images: Number of image prompts to generate.
            style_desc: Description of the artistic style.
            period_desc: Description of the time period.
            custom_desc: Custom elements to include.

        Returns:
            List of image prompts.
        """
        # Extract key themes from the Kural translation
        themes = []

        # Common themes in Thirukkural
        theme_keywords = {
            "forgiveness": ["forgiveness", "patience", "tolerance", "bear", "strength"],
            "love": ["love", "affection", "heart", "loving"],
            "learning": ["learning", "knowledge", "learn", "education"],
            "virtue": ["virtue", "good", "righteous", "dharma"],
            "friendship": ["friend", "friendship", "companion"],
            "wisdom": ["wisdom", "wise", "sage", "knowledge"],
            "family": ["family", "home", "household", "domestic"],
            "leadership": ["leader", "king", "rule", "govern"]
        }

        # Identify themes in the Kural translation
        for theme, keywords in theme_keywords.items():
            if any(keyword in kural_translation.lower() for keyword in keywords):
                themes.append(theme)

        # If no themes identified, use a default
        if not themes:
            themes = ["wisdom"]

        # Generate prompts based on identified themes
        prompts = []

        # Template prompts for different themes
        theme_prompts = {
            "forgiveness": [
                "An elderly Tamil village elder with gentle eyes and white hair forgiving a young man who kneels before him, surrounded by villagers in traditional clothing. Golden evening light filters through trees, creating a warm atmosphere of reconciliation. Tamil literature, photorealistic, detailed, cinematic lighting",
                "A Tamil grandfather teaching his grandson about forgiveness under a banyan tree. The old man's weathered face shows wisdom while the boy listens attentively. Rural Tamil Nadu setting with traditional mud houses in background. Tamil literature, photorealistic, detailed, cinematic lighting",
                "Two former rivals embracing in reconciliation during a village festival. Colorful temple decorations and oil lamps surround them as community members watch with approval. Emotional moment of forgiveness captured in warm colors. Tamil literature, photorealistic, detailed, cinematic lighting"
            ],
            "love": [
                "An elderly Tamil woman sharing her limited food with neighbors after a storm. Her small hut is filled with displaced villagers as she serves them with a loving smile. Rain patters on the roof while warm lamplight illuminates their grateful faces. Tamil literature, photorealistic, detailed, cinematic lighting",
                "A Tamil family embracing each other during a reunion. Multiple generations from grandparents to grandchildren share joyful tears. Traditional brass lamps and jasmine flowers decorate their ancestral home. Tamil literature, photorealistic, detailed, cinematic lighting",
                "A young Tamil couple helping an elderly stranger during monsoon floods. They guide the old man through water while protecting him with an umbrella. Their faces show compassion despite their own difficulties. Tamil literature, photorealistic, detailed, cinematic lighting"
            ],
            "learning": [
                "A respected Tamil teacher and student walking through different parts of a city, observing real-life examples of ethical principles. The teacher points out situations while the student's face shows dawning understanding. Tamil literature, photorealistic, detailed, cinematic lighting",
                "An ancient palm-leaf manuscript of Thirukkural being studied by a young scholar in a traditional Tamil school. Oil lamps illuminate the text as the student takes notes with focused concentration. Tamil literature, photorealistic, detailed, cinematic lighting",
                "A modern classroom where a teacher illustrates Thirukkural principles using contemporary examples. Students of different ages engage in lively discussion while charts showing Tamil ethical concepts hang on walls. Tamil literature, photorealistic, detailed, cinematic lighting"
            ],
            "wisdom": [
                "An elderly Tamil scholar sitting beneath a flowering tree, sharing ancient wisdom with attentive villagers gathered around him. His expressive hands gesture as he speaks, with the magnificent Meenakshi Temple visible in the distance. Tamil literature, photorealistic, detailed, cinematic lighting",
                "A grandmother telling stories to children by lamplight in a traditional Tamil home. Her face is animated as she passes down cultural wisdom, with the children's eyes wide with wonder. Brass and bronze traditional items decorate the simple home. Tamil literature, photorealistic, detailed, cinematic lighting",
                "A modern Tamil professional pausing for reflection at a temple before making an important decision. Ancient stone carvings contrast with their contemporary clothing, symbolizing timeless wisdom in modern context. Tamil literature, photorealistic, detailed, cinematic lighting"
            ]
        }

        # Apply style and period to all prompts
        style_elements = style_desc if style_desc else "photorealistic, detailed, cinematic lighting"
        period_elements = period_desc if period_desc else "Tamil Nadu with traditional cultural elements"
        custom_elements = f", {custom_desc}" if custom_desc else ""

        # Add default prompts for themes not in our template dictionary
        for theme in themes:
            if theme in theme_prompts:
                # Modify the theme-specific prompts to use the specified style and period
                theme_specific_prompts = []
                for prompt in theme_prompts[theme]:
                    # Replace the default style with the specified style
                    modified_prompt = re.sub(r'Tamil literature, photorealistic, detailed, cinematic lighting$',
                                            f"{style_elements}{custom_elements}", prompt)
                    theme_specific_prompts.append(modified_prompt)
                prompts.extend(theme_specific_prompts)
            else:
                # Generic Tamil cultural prompt
                # Apply style and period to generic prompt (using the already defined variables)

                prompts.append(
                    f"A scene illustrating the Thirukkural teaching about {theme}. Set in {period_elements}. An elder sharing wisdom with younger people. Rich colors and emotional depth. {style_elements}{custom_elements}"
                )

        # Ensure we have the requested number of prompts
        if len(prompts) < num_images:
            # Add generic prompts to fill the gap with style and period
            # Use the already defined style_elements and custom_elements
            # Just update period_elements for this specific context
            period_elements_village = period_desc if period_desc else "traditional Tamil village"

            generic_prompts = [
                f"A serene scene in a {period_elements_village} with people exemplifying Thirukkural values. Golden sunlight illuminates their faces as they interact with kindness and wisdom. {style_elements}{custom_elements}",
                f"An emotional moment of human connection in a Tamil setting, with architecture and clothing reflecting Tamil culture. The scene captures the essence of Thirukkural teachings through expressive faces and body language. {style_elements}{custom_elements}",
                f"A symbolic representation of Thirukkural wisdom through a multi-generational Tamil family scene. Traditional elements like kolam patterns, temple architecture, and traditional clothing create an authentic atmosphere. {style_elements}{custom_elements}"
            ]
            prompts.extend(generic_prompts)

        return prompts[:num_images]
