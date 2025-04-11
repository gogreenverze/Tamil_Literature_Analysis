"""
Story Generator - Generates stories based on Thirukkural verses.
"""

import json
import os
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class StoryGenerator:
    """
    Generates stories based on Thirukkural verses using AI.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the StoryGenerator.

        Args:
            api_key: OpenAI API key. If None, uses the OPENAI_API_KEY environment variable.
            model: The OpenAI model to use for story generation.
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

    def generate_story(
        self,
        kural_id: int,
        kural_text: str,
        kural_translation: str,
        language: str = "both"
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate a story based on a Thirukkural verse.

        Args:
            kural_id: The ID of the Kural.
            kural_text: The Tamil text of the Kural.
            kural_translation: The English translation of the Kural.
            language: The language(s) for the story ("tamil", "english", or "both").

        Returns:
            Tuple of (tamil_story, english_story). Either may be None depending on the language parameter.
        """
        # Get additional details about the Kural
        kural_details = self._get_kural_details(kural_id)

        # If OpenAI is available, use it to generate the story
        if OPENAI_AVAILABLE and self.client:
            return self._generate_with_openai(kural_details, language)

        # Otherwise, use a template-based approach
        return self._generate_template_story(kural_details, language)

    def _generate_with_openai(self, kural_details: Dict[str, Any], language: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate a story using OpenAI's API.

        Args:
            kural_details: Dictionary with Kural details.
            language: The language(s) for the story.

        Returns:
            Tuple of (tamil_story, english_story).
        """
        tamil_story = None
        english_story = None

        try:
            # Prepare the prompt
            system_prompt = """
            You are ValluvarAI, an expert in Tamil literature and Thirukkural.
            Your task is to create an engaging, emotional story based on a Thirukkural verse.
            The story should:
            1. Be 3-4 paragraphs long
            2. Illustrate the moral or ethical principle in the Kural
            3. Be set in a culturally relevant context (traditional or modern Tamil setting)
            4. Include vivid imagery and emotional elements
            5. Be suitable for all ages
            6. End with a clear connection to the Kural's meaning
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

            Please create a story that illustrates the meaning of this Kural.
            """

            if language in ["tamil", "both"]:
                # Generate Tamil story
                tamil_prompt = user_prompt + "\nPlease write the story in Tamil language."
                tamil_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": tamil_prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                tamil_story = tamil_response.choices[0].message.content.strip()

            if language in ["english", "both"]:
                # Generate English story
                english_prompt = user_prompt + "\nPlease write the story in English language."
                english_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": english_prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                english_story = english_response.choices[0].message.content.strip()

            return tamil_story, english_story

        except Exception as e:
            print(f"Error generating story with OpenAI: {e}")
            # Fall back to template-based story
            return self._generate_template_story(kural_details, language)

    def _generate_template_story(self, kural_details: Dict[str, Any], language: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate a template-based story when OpenAI is not available.

        Args:
            kural_details: Dictionary with Kural details.
            language: The language(s) for the story.

        Returns:
            Tuple of (tamil_story, english_story).
        """
        tamil_story = None
        english_story = None

        # Template stories based on the chapter
        chapter_english = kural_details.get("chapter_english", "").lower()

        # English template stories
        if language in ["english", "both"]:
            if "forgiveness" in chapter_english or "patience" in chapter_english:
                english_story = f"""
                In a small village near Madurai, there lived an elderly farmer named Raman. Known for his wisdom and kindness, he was respected by everyone in the community. One day, a young man from a neighboring village stole crops from Raman's field out of desperation to feed his family.

                When the villagers caught the young man and brought him before Raman, everyone expected harsh punishment. Instead, Raman looked at the trembling young man and asked about his circumstances. Learning about his poverty and hungry family, Raman not only forgave him but offered him work in his fields.

                Years passed, and the young man became Raman's most trusted helper. When asked why he had shown such forgiveness, Raman would quote the Thirukkural: "{kural_details.get('english', '')}". He explained that true strength lies not in punishment but in understanding and forgiveness.

                The story of Raman's forgiveness spread throughout the region, teaching everyone that compassion is the greatest form of strength, just as Thiruvalluvar had written centuries ago.
                """
            elif "love" in chapter_english:
                english_story = f"""
                In the coastal town of Nagapattinam, Meena and her grandmother Parvati lived in a small house by the sea. Parvati was known for her selfless love, always putting others before herself despite having very little.

                During a devastating cyclone, their home was one of the few left standing. Without hesitation, Parvati opened their doors to neighbors who had lost everything. She shared their limited food, water, and space, even giving up her own bed to a pregnant woman.

                When Meena asked why she would give so much when they barely had enough for themselves, Parvati smiled and recited the Thirukkural: "{kural_details.get('english', '')}". She explained that love means nothing if kept to oneself; it grows only when shared with others.

                As the community rebuilt, everyone remembered Parvati's lesson. The town became known for its spirit of sharing and mutual support, embodying the timeless wisdom of Thiruvalluvar's words on love.
                """
            elif "learning" in chapter_english or "education" in chapter_english:
                english_story = f"""
                In Chennai, Professor Anand was renowned for his dedication to teaching. Unlike other professors who merely lectured, Anand lived by the knowledge he imparted, demonstrating integrity in every action.

                One day, a brilliant but arrogant student named Karthik challenged him, questioning the practical value of ethics in the modern world. Instead of dismissing him, Anand invited Karthik to follow him for a day outside the classroom.

                They visited hospitals, courts, and businesses, observing professionals who either honored or betrayed their learning. By evening, Karthik witnessed how those who applied their knowledge ethically earned respect and made meaningful contributions, while those who didn't created harm despite their credentials.

                Back at the university, Anand quoted the Thirukkural: "{kural_details.get('english', '')}". Karthik finally understood that true learning isn't measured by degrees or memorization, but by how knowledge transforms one's character and actions—a lesson straight from Thiruvalluvar's ancient wisdom.
                """
            else:
                english_story = f"""
                In the ancient city of Madurai, close to the magnificent Meenakshi Temple, lived an old scholar named Sundaram. He had spent his entire life studying the Thirukkural and teaching its wisdom to younger generations.

                One particular verse that he often emphasized was: "{kural_details.get('english', '')}". This Kural from the chapter on {kural_details.get('chapter_english', '')} had guided his life through many challenges and decisions.

                One day, a group of students came to him with questions about applying ancient wisdom in modern times. Sundaram smiled and shared a personal story that perfectly illustrated the meaning of this Kural. He explained how following this principle had brought him peace and respect throughout his life.

                As the students left, they carried not just the words of Thiruvalluvar, but a living example of how timeless wisdom can illuminate our path in any era. Sundaram's teaching reminded them that the Thirukkural's guidance remains as relevant today as it was when written nearly two millennia ago.
                """

        # Tamil template stories
        if language in ["tamil", "both"]:
            if "forgiveness" in chapter_english or "patience" in chapter_english:
                tamil_story = f"""
                மதுரைக்கு அருகில் உள்ள ஒரு சிறிய கிராமத்தில், ராமன் என்ற வயதான விவசாயி வாழ்ந்து வந்தார். அவரது ஞானம் மற்றும் கருணைக்காக அறியப்பட்ட அவர், சமூகத்தில் உள்ள அனைவராலும் மதிக்கப்பட்டார். ஒரு நாள், அடுத்த கிராமத்தைச் சேர்ந்த ஒரு இளைஞன், தனது குடும்பத்திற்கு உணவளிக்க வேண்டிய நிர்ப்பந்தத்தில், ராமனின் வயலில் இருந்து பயிர்களை திருடினான்.

                கிராமத்தினர் அந்த இளைஞனைப் பிடித்து ராமனிடம் கொண்டு வந்தபோது, அனைவரும் கடுமையான தண்டனையை எதிர்பார்த்தனர். ஆனால், நடுங்கிக் கொண்டிருந்த அந்த இளைஞனைப் பார்த்த ராமன், அவனது சூழ்நிலைகளைப் பற்றி விசாரித்தார். அவனது வறுமை மற்றும் பசியால் வாடும் குடும்பத்தைப் பற்றி அறிந்த ராமன், அவனை மன்னித்தது மட்டுமல்லாமல், தனது வயல்களில் வேலையும் வழங்கினார்.

                ஆண்டுகள் கடந்தன, அந்த இளைஞன் ராமனின் மிகவும் நம்பகமான உதவியாளரானான். ஏன் அவர் அத்தகைய மன்னிப்பைக் காட்டினார் என்று கேட்கப்பட்டபோது, ராமன் திருக்குறளை மேற்கோள் காட்டுவார்: "{kural_details.get('tamil', '')}". உண்மையான வலிமை தண்டனையில் அல்ல, புரிதல் மற்றும் மன்னிப்பில் உள்ளது என்று அவர் விளக்கினார்.

                ராமனின் மன்னிப்பின் கதை பிராந்தியம் முழுவதும் பரவி, கருணையே மிகப்பெரிய வலிமை வடிவம் என்று அனைவருக்கும் கற்பித்தது, திருவள்ளுவர் நூற்றாண்டுகளுக்கு முன்பு எழுதியது போலவே.
                """
            elif "love" in chapter_english:
                tamil_story = f"""
                நாகப்பட்டினம் கடற்கரை நகரத்தில், மீனா மற்றும் அவரது பாட்டி பார்வதி கடலருகே ஒரு சிறிய வீட்டில் வசித்து வந்தனர். பார்வதி தனது சுயநலமற்ற அன்புக்காக அறியப்பட்டவர், மிகக் குறைவாக இருந்தபோதும் எப்போதும் மற்றவர்களை தனக்கு முன் வைப்பார்.

                ஒரு கொடிய புயலின் போது, அவர்களின் வீடு நிற்கும் சில வீடுகளில் ஒன்றாக இருந்தது. தயக்கமின்றி, பார்வதி அனைத்தையும் இழந்த அக்கம்பக்கத்தினருக்கு தங்கள் கதவுகளைத் திறந்தார். அவர்கள் வரையறுக்கப்பட்ட உணவு, தண்ணீர் மற்றும் இடத்தைப் பகிர்ந்து கொண்டார், ஒரு கர்ப்பிணிப் பெண்ணுக்கு தனது படுக்கையையும் கொடுத்தார்.

                தங்களுக்கே போதுமான அளவு இல்லாதபோது ஏன் அவர் அவ்வளவு கொடுப்பார் என்று மீனா கேட்டபோது, பார்வதி புன்னகைத்து திருக்குறளை ஒப்பித்தார்: "{kural_details.get('tamil', '')}". அன்பு என்பது தனக்குள் வைத்திருந்தால் அர்த்தமில்லை; அது மற்றவர்களுடன் பகிரப்படும்போது மட்டுமே வளரும் என்று அவர் விளக்கினார்.

                சமூகம் மீண்டும் கட்டியெழுப்பப்பட்டபோது, அனைவரும் பார்வதியின் பாடத்தை நினைவில் கொண்டனர். அந்த நகரம் பகிர்வு மற்றும் பரஸ்பர ஆதரவின் உணர்வுக்காக அறியப்பட்டது, அன்பைப் பற்றிய திருவள்ளுவரின் காலத்தால் அழியாத ஞானத்தை உள்ளடக்கியது.
                """
            elif "learning" in chapter_english or "education" in chapter_english:
                tamil_story = f"""
                சென்னையில், பேராசிரியர் ஆனந்த் தனது கற்பித்தல் அர்ப்பணிப்புக்காக பிரபலமானவர். வெறுமனே விரிவுரை நடத்தும் மற்ற பேராசிரியர்களைப் போலல்லாமல், ஆனந்த் தான் வழங்கிய அறிவின்படி வாழ்ந்தார், ஒவ்வொரு செயலிலும் நேர்மையைக் காட்டினார்.

                ஒரு நாள், கார்த்திக் என்ற புத்திசாலியான ஆனால் அகந்தையுள்ள மாணவர் அவரை சவால் செய்தார், நவீன உலகில் நெறிமுறைகளின் நடைமுறை மதிப்பைக் கேள்விக்குள்ளாக்கினார். அவரை நிராகரிக்காமல், ஆனந்த் கார்த்திக்கை வகுப்பறைக்கு வெளியே ஒரு நாள் தன்னைப் பின்தொடர அழைத்தார்.

                அவர்கள் மருத்துவமனைகள், நீதிமன்றங்கள் மற்றும் வணிகங்களுக்குச் சென்று, தங்கள் கற்றலை மதித்த அல்லது துரோகம் செய்த தொழில்முறை நிபுணர்களைக் கவனித்தனர். மாலையில், கார்த்திக் தங்கள் அறிவை நெறிமுறையாகப் பயன்படுத்தியவர்கள் மரியாதையைப் பெற்று அர்த்தமுள்ள பங்களிப்புகளைச் செய்தனர், அவ்வாறு செய்யாதவர்கள் தங்கள் சான்றிதழ்கள் இருந்தபோதிலும் தீங்கு விளைவித்தனர் என்பதைக் கண்டார்.

                பல்கலைக்கழகத்திற்குத் திரும்பிய ஆனந்த், திருக்குறளை மேற்கோள் காட்டினார்: "{kural_details.get('tamil', '')}". உண்மையான கற்றல் பட்டங்கள் அல்லது மனப்பாடம் செய்வதால் அளவிடப்படவில்லை, மாறாக அறிவு ஒருவரின் குணம் மற்றும் செயல்களை எவ்வாறு மாற்றுகிறது என்பதால் அளவிடப்படுகிறது என்பதை கார்த்திக் இறுதியாகப் புரிந்துகொண்டார்—திருவள்ளுவரின் பழைய ஞானத்திலிருந்து நேரடியாக ஒரு பாடம்.
                """
            else:
                tamil_story = f"""
                பழமையான மதுரை நகரில், அற்புதமான மீனாட்சி கோவிலுக்கு அருகில், சுந்தரம் என்ற வயதான அறிஞர் வாழ்ந்து வந்தார். அவர் தனது வாழ்நாள் முழுவதையும் திருக்குறளைப் படிப்பதிலும், அதன் ஞானத்தை இளைய தலைமுறையினருக்குக் கற்பிப்பதிலும் செலவழித்தார்.

                அவர் அடிக்கடி வலியுறுத்திய ஒரு குறிப்பிட்ட குறள்: "{kural_details.get('tamil', '')}". {kural_details.get('chapter', '')} அதிகாரத்தில் இருந்து இந்த குறள் பல சவால்கள் மற்றும் முடிவுகளில் அவரது வாழ்க்கையை வழிநடத்தியது.

                ஒரு நாள், நவீன காலங்களில் பழைய ஞானத்தைப் பயன்படுத்துவது பற்றிய கேள்விகளுடன் ஒரு குழு மாணவர்கள் அவரிடம் வந்தனர். சுந்தரம் புன்னகைத்து, இந்த குறளின் பொருளை சரியாக விளக்கும் ஒரு தனிப்பட்ட கதையைப் பகிர்ந்து கொண்டார். இந்த கொள்கையைப் பின்பற்றுவது அவரது வாழ்க்கை முழுவதும் அமைதி மற்றும் மரியாதையை எவ்வாறு கொண்டு வந்தது என்பதை அவர் விளக்கினார்.

                மாணவர்கள் புறப்பட்டபோது, அவர்கள் திருவள்ளுவரின் வார்த்தைகளை மட்டுமல்ல, காலத்தால் அழியாத ஞானம் எந்த காலத்திலும் நமது பாதையை எவ்வாறு ஒளிரச் செய்யும் என்பதற்கான உயிருள்ள உதாரணத்தையும் கொண்டு சென்றனர். சுந்தரத்தின் கற்பித்தல் திருக்குறளின் வழிகாட்டுதல் இரண்டாயிரம் ஆண்டுகளுக்கு முன்பு எழுதப்பட்டது போலவே இன்றும் பொருத்தமானதாக இருப்பதை அவர்களுக்கு நினைவூட்டியது.
                """

        return tamil_story, english_story
