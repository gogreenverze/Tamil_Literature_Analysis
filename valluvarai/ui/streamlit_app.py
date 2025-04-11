"""
Streamlit UI for ValluvarAI.
"""

import os
import sys
import time
from pathlib import Path

# Add the parent directory to the path to import valluvarai
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    import streamlit as st
    from PIL import Image
    import base64
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    print("Streamlit is not available. Please install it with 'pip install streamlit'.")
    sys.exit(1)

from valluvarai import KuralAgent

# Set page configuration
st.set_page_config(
    page_title="ValluvarAI - Tamil Literature & Thirukkural Storytelling",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF5722;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4CAF50;
        margin-bottom: 1rem;
    }
    .kural-box {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .tamil-text {
        font-family: 'Noto Sans Tamil', sans-serif;
        font-size: 1.2rem;
    }
    .story-container {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .analysis-container {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .image-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        color: #9E9E9E;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'kural_agent' not in st.session_state:
    st.session_state.kural_agent = KuralAgent()

if 'search_history' not in st.session_state:
    st.session_state.search_history = []

if 'current_kural' not in st.session_state:
    st.session_state.current_kural = None

if 'current_stories' not in st.session_state:
    st.session_state.current_stories = {"tamil": None, "english": None}

if 'current_images' not in st.session_state:
    st.session_state.current_images = []

if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None

# Helper functions
def get_image_base64(image_path):
    """Convert an image to base64 for embedding in HTML."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def display_audio_player(audio_path):
    """Display an audio player for the given audio file."""
    if audio_path and os.path.exists(audio_path):
        audio_bytes = open(audio_path, 'rb').read()
        st.audio(audio_bytes, format='audio/mp3')
    else:
        st.warning("Audio file not available.")

# Main app
def main():
    # Header
    st.markdown('<h1 class="main-header">ValluvarAI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center;">An AI-powered storytelling & literary companion for Tamil ethics, emotions, and culture.</p>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("## Search Options")
        search_query = st.text_input("Enter a keyword (English or Tamil):", placeholder="e.g., forgiveness, அன்பு")
        language_option = st.radio("Story Language:", ["Both", "Tamil Only", "English Only"])
        include_images = st.checkbox("Generate Images", value=True)
        include_video = st.checkbox("Generate Video", value=False)

        if st.button("Search & Generate"):
            with st.spinner("Searching for relevant Thirukkural..."):
                # Map language option to parameter
                language_param = "both"
                if language_option == "Tamil Only":
                    language_param = "tamil"
                elif language_option == "English Only":
                    language_param = "english"

                # Call the KuralAgent
                try:
                    result = st.session_state.kural_agent.tell_story(
                        search_query,
                        include_images=include_images,
                        include_video=include_video,
                        language=language_param
                    )

                    # Store the results in session state
                    st.session_state.current_kural = {
                        "id": result["kural_id"],
                        "tamil": result["kural_text"],
                        "english": result["kural_translation"]
                    }

                    st.session_state.current_stories = {
                        "tamil": result.get("tamil_story"),
                        "english": result.get("english_story")
                    }

                    st.session_state.current_images = result.get("images", [])
                    st.session_state.current_analysis = result.get("analysis", {})

                    # Add to search history
                    st.session_state.search_history.append({
                        "query": search_query,
                        "kural_id": result["kural_id"]
                    })

                    st.success("Story generated successfully!")

                except Exception as e:
                    st.error(f"Error generating story: {str(e)}")

        # Search history
        if st.session_state.search_history:
            st.markdown("## Search History")
            for i, item in enumerate(st.session_state.search_history):
                if st.button(f"{item['query']} (Kural {item['kural_id']})", key=f"history_{i}"):
                    # Regenerate the story for this historical search
                    with st.spinner("Regenerating story..."):
                        try:
                            result = st.session_state.kural_agent.tell_story(
                                item['query'],
                                include_images=include_images,
                                include_video=include_video,
                                language=language_param
                            )

                            # Update session state
                            st.session_state.current_kural = {
                                "id": result["kural_id"],
                                "tamil": result["kural_text"],
                                "english": result["kural_translation"]
                            }

                            st.session_state.current_stories = {
                                "tamil": result.get("tamil_story"),
                                "english": result.get("english_story")
                            }

                            st.session_state.current_images = result.get("images", [])
                            st.session_state.current_analysis = result.get("analysis", {})

                            st.success("Story regenerated successfully!")

                        except Exception as e:
                            st.error(f"Error regenerating story: {str(e)}")

    # Main content
    if st.session_state.current_kural:
        # Display the Kural
        st.markdown('<h2 class="sub-header">Thirukkural</h2>', unsafe_allow_html=True)

        kural_col1, kural_col2 = st.columns(2)

        with kural_col1:
            st.markdown('<div class="kural-box">', unsafe_allow_html=True)
            st.markdown(f'<p class="tamil-text">{st.session_state.current_kural["tamil"]}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with kural_col2:
            st.markdown('<div class="kural-box">', unsafe_allow_html=True)
            st.markdown(f'<p>{st.session_state.current_kural["english"]}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Display the stories
        st.markdown('<h2 class="sub-header">Stories</h2>', unsafe_allow_html=True)

        story_tabs = st.tabs(["Tamil Story", "English Story"])

        with story_tabs[0]:
            if st.session_state.current_stories["tamil"]:
                st.markdown('<div class="story-container">', unsafe_allow_html=True)
                st.markdown(f'<p class="tamil-text">{st.session_state.current_stories["tamil"]}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # Display Tamil audio if available
                if "audio" in st.session_state and "tamil" in st.session_state.audio:
                    st.markdown("### Tamil Narration")
                    display_audio_player(st.session_state.audio["tamil"].get("file_path"))
            else:
                st.info("No Tamil story generated. Try changing the language option.")

        with story_tabs[1]:
            if st.session_state.current_stories["english"]:
                st.markdown('<div class="story-container">', unsafe_allow_html=True)
                st.markdown(f'<p>{st.session_state.current_stories["english"]}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # Display English audio if available
                if "audio" in st.session_state and "english" in st.session_state.audio:
                    st.markdown("### English Narration")
                    display_audio_player(st.session_state.audio["english"].get("file_path"))
            else:
                st.info("No English story generated. Try changing the language option.")

        # Display the images
        if st.session_state.current_images:
            st.markdown('<h2 class="sub-header">Generated Images</h2>', unsafe_allow_html=True)

            image_cols = st.columns(min(3, len(st.session_state.current_images)))

            for i, image_data in enumerate(st.session_state.current_images):
                col_idx = i % len(image_cols)
                with image_cols[col_idx]:
                    if image_data.get("file_path") and os.path.exists(image_data["file_path"]):
                        st.image(image_data["file_path"], caption=f"Image {i+1}", use_column_width=True)
                        # Show error message if there was an error
                        if not image_data.get("success", True) and image_data.get("error"):
                            st.warning(f"Note: {image_data['error']}")
                    else:
                        st.warning(f"Image {i+1} not available.")
                        if image_data.get("error"):
                            st.error(f"Error: {image_data['error']}")

                        # Show a placeholder message with instructions
                        st.info("To enable image generation, you need to set up an API key for OpenAI or another provider. Check the documentation for details.")

                        # Show the prompt that would have been used
                        if image_data.get("prompt"):
                            with st.expander("Image prompt"):
                                st.text(image_data["prompt"])

        # Display the video if available
        if "video" in st.session_state and st.session_state.video and st.session_state.video.get("file_path"):
            st.markdown('<h2 class="sub-header">Generated Video</h2>', unsafe_allow_html=True)

            video_path = st.session_state.video["file_path"]
            if os.path.exists(video_path):
                video_bytes = open(video_path, 'rb').read()
                st.video(video_bytes)
            else:
                st.warning("Video file not available.")

        # Display the analysis
        if st.session_state.current_analysis:
            st.markdown('<h2 class="sub-header">Literary Analysis</h2>', unsafe_allow_html=True)

            analysis_tabs = st.tabs([
                "Historical Context",
                "Linguistic Analysis",
                "Philosophical Depth",
                "Contemporary Relevance",
                "Emotional Resonance"
            ])

            with analysis_tabs[0]:
                st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
                st.markdown(st.session_state.current_analysis.get("historical_context", "Analysis not available."))
                st.markdown('</div>', unsafe_allow_html=True)

            with analysis_tabs[1]:
                st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
                st.markdown(st.session_state.current_analysis.get("linguistic_analysis", "Analysis not available."))
                st.markdown('</div>', unsafe_allow_html=True)

            with analysis_tabs[2]:
                st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
                st.markdown(st.session_state.current_analysis.get("philosophical_depth", "Analysis not available."))
                st.markdown('</div>', unsafe_allow_html=True)

            with analysis_tabs[3]:
                st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
                st.markdown(st.session_state.current_analysis.get("contemporary_relevance", "Analysis not available."))
                st.markdown('</div>', unsafe_allow_html=True)

            with analysis_tabs[4]:
                st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
                st.markdown(st.session_state.current_analysis.get("emotional_resonance", "Analysis not available."))
                st.markdown('</div>', unsafe_allow_html=True)

    else:
        # Display welcome message
        st.markdown("""
        ## Welcome to ValluvarAI!

        This application helps you explore the wisdom of Thirukkural through AI-generated stories, images, and analysis.

        To get started:
        1. Enter a keyword in English or Tamil in the search box on the left
        2. Choose your preferred language for the story
        3. Select whether to generate images and/or video
        4. Click "Search & Generate" to create your personalized Thirukkural experience

        ValluvarAI will find the most relevant Thirukkural verse based on your keyword, generate a story that illustrates its meaning, and provide a multi-dimensional analysis of its significance.
        """)

    # Footer
    st.markdown('<div class="footer">ValluvarAI - Bringing Tamil literature to life with AI</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
