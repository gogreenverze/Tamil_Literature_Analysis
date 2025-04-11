# ValluvarAI

An AI-powered storytelling & literary companion for Tamil ethics, emotions, and culture.

## 🧠 Core Capabilities

- 🔍 **Keyword Search**: Accepts English or Tamil keywords (e.g., "forgiveness", "அருள்")
- 📜 **Kural Retrieval**: Finds semantically relevant Kural from 1330 verses
- 📖 **Bilingual Storytelling**: Auto-generates emotional stories in Tamil & English
- 🖼️ **AI Image Generation**: Creates scene-based images from the story
- 🎥 **Short Video Creation**: Auto-generates 30–60 sec video with narration + scenes
- 🔡 **Tamil/English TTS**: Voice narration using native-style voice
- 📊 **Multi-grid Literary Analysis**: Timeframe, meaning, linguistics, emotional depth

## 🚀 Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/valluvarai.git
cd valluvarai

# Install dependencies
pip install -e .
```

### Running the Streamlit UI

```bash
streamlit run valluvarai/ui/streamlit_app.py
```

### Running the API

```bash
uvicorn valluvarai.api.main:app --reload
```

## 📚 Usage

### Python Package

```python
from valluvarai import KuralAgent

agent = KuralAgent()
output = agent.tell_story("forgiveness", include_images=True, include_video=True)
```

### API Endpoints

- `/search` - Search for a Kural based on a keyword
- `/generate-story` - Generate a story based on a Kural
- `/generate-images` - Generate images based on a story
- `/generate-video` - Generate a video based on a Kural
- `/analyze` - Analyze a Kural

## 📁 Project Structure

```
valluvarai/
├── kural_data/
│   └── kural_1330.json
├── agents/
│   ├── kural_matcher.py
│   ├── story_generator.py
│   ├── image_prompt_builder.py
│   └── narration_engine.py
├── services/
│   ├── image_generator.py
│   ├── video_builder.py
│   └── insight_engine.py
├── api/
│   └── main.py
└── ui/
    └── streamlit_app.py
```

## 🛠️ Dependencies

- **Core**: numpy, scikit-learn, requests, Pillow
- **API**: fastapi, uvicorn, pydantic
- **UI**: streamlit
- **AI Services**: openai (optional)
- **Text-to-Speech**: gtts
- **Video Generation**: ffmpeg (optional)

## 📄 License

MIT License