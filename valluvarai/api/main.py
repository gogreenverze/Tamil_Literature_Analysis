"""
FastAPI application for ValluvarAI with authentication.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
from fastapi import FastAPI, HTTPException, Query, Depends, status, Header, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from valluvarai import KuralAgent
from valluvarai.auth import auth_manager
from valluvarai.auth.models import User, UserCreate, UserUpdate, Token, UserPreferences
from valluvarai.config import config

# Initialize the FastAPI app
app = FastAPI(
    title="ValluvarAI API",
    description="API for ValluvarAI - An AI-powered storytelling & literary companion for Tamil ethics, emotions, and culture.",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize the KuralAgent
kural_agent = KuralAgent()

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Authentication dependency
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current user from the token.

    Args:
        token: JWT token.

    Returns:
        User if authentication is successful.

    Raises:
        HTTPException: If authentication fails.
    """
    if not auth_manager.enabled:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Authentication is not enabled"
        )

    token_data = auth_manager.decode_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = auth_manager.get_user(token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user

# Admin authentication dependency
async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current admin user.

    Args:
        current_user: Current user.

    Returns:
        User if the user is an admin.

    Raises:
        HTTPException: If the user is not an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return current_user

# Optional authentication dependency
async def get_optional_user(token: Optional[str] = Header(None, alias="Authorization")) -> Optional[User]:
    """
    Get the current user from the token if available.

    Args:
        token: JWT token.

    Returns:
        User if authentication is successful, None otherwise.
    """
    if not auth_manager.enabled or not token:
        return None

    # Remove "Bearer " prefix if present
    if token.startswith("Bearer "):
        token = token[7:]

    token_data = auth_manager.decode_token(token)
    if token_data is None:
        return None

    user = auth_manager.get_user(token_data.username)
    if user is None or user.disabled:
        return None

    return user

# Define API models
class SearchRequest(BaseModel):
    query: str
    language: Optional[str] = "both"

class StoryRequest(BaseModel):
    kural_id: int
    language: Optional[str] = "both"
    include_images: Optional[bool] = True

class ImageRequest(BaseModel):
    kural_id: int
    story_text: str
    num_images: Optional[int] = 3

class VideoRequest(BaseModel):
    kural_id: int
    include_audio: Optional[bool] = True
    language: Optional[str] = "both"

class AnalysisRequest(BaseModel):
    kural_id: int

# Define API routes
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "ValluvarAI API",
        "version": "0.1.0",
        "description": "An AI-powered storytelling & literary companion for Tamil ethics, emotions, and culture."
    }

@app.post("/search")
async def search(request: SearchRequest):
    """
    Search for a Kural based on a keyword.

    Args:
        request: SearchRequest object with query and language.

    Returns:
        Dictionary with Kural information.
    """
    try:
        kural_id, kural_text, kural_translation = kural_agent.kural_matcher.find_kural(request.query)

        # Get additional details about the Kural
        kural_details = kural_agent.kural_matcher._get_kural_details(kural_id)

        return {
            "kural_id": kural_id,
            "kural_text": kural_text,
            "kural_translation": kural_translation,
            "section": kural_details.get("section", ""),
            "section_english": kural_details.get("section_english", ""),
            "chapter": kural_details.get("chapter", ""),
            "chapter_english": kural_details.get("chapter_english", ""),
            "explanation_tamil": kural_details.get("explanation_tamil", ""),
            "explanation_english": kural_details.get("explanation_english", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-story")
async def generate_story(request: StoryRequest):
    """
    Generate a story based on a Kural.

    Args:
        request: StoryRequest object with kural_id, language, and include_images.

    Returns:
        Dictionary with story information.
    """
    try:
        # Get the Kural details
        kural_details = kural_agent.kural_matcher._get_kural_details(request.kural_id)
        kural_text = kural_details.get("tamil", "")
        kural_translation = kural_details.get("english", "")

        # Generate the story
        tamil_story, english_story = kural_agent.story_generator.generate_story(
            request.kural_id, kural_text, kural_translation, request.language
        )

        # Generate literary analysis
        analysis = kural_agent.insight_engine.analyze(
            request.kural_id, kural_text, kural_translation
        )

        result = {
            "kural_id": request.kural_id,
            "kural_text": kural_text,
            "kural_translation": kural_translation,
            "tamil_story": tamil_story,
            "english_story": english_story,
            "analysis": analysis["analysis"],
            "images": []
        }

        # Generate images if requested
        if request.include_images:
            image_prompts = kural_agent.image_prompt_builder.build_prompts(
                tamil_story, english_story, kural_text, kural_translation
            )
            result["images"] = kural_agent.image_generator.generate_images(image_prompts)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-images")
async def generate_images(request: ImageRequest):
    """
    Generate images based on a story.

    Args:
        request: ImageRequest object with kural_id, story_text, and num_images.

    Returns:
        Dictionary with image information.
    """
    try:
        # Get the Kural details
        kural_details = kural_agent.kural_matcher._get_kural_details(request.kural_id)
        kural_text = kural_details.get("tamil", "")
        kural_translation = kural_details.get("english", "")

        # Generate image prompts
        image_prompts = kural_agent.image_prompt_builder.build_prompts(
            None, request.story_text, kural_text, kural_translation, request.num_images
        )

        # Generate images
        images = kural_agent.image_generator.generate_images(image_prompts)

        return {
            "kural_id": request.kural_id,
            "images": images
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-video")
async def generate_video(request: VideoRequest):
    """
    Generate a video based on a Kural.

    Args:
        request: VideoRequest object with kural_id, include_audio, and language.

    Returns:
        Dictionary with video information.
    """
    try:
        # Get the Kural details
        kural_details = kural_agent.kural_matcher._get_kural_details(request.kural_id)
        kural_text = kural_details.get("tamil", "")
        kural_translation = kural_details.get("english", "")

        # Generate the story
        tamil_story, english_story = kural_agent.story_generator.generate_story(
            request.kural_id, kural_text, kural_translation, request.language
        )

        # Generate image prompts
        image_prompts = kural_agent.image_prompt_builder.build_prompts(
            tamil_story, english_story, kural_text, kural_translation
        )

        # Generate images
        images = kural_agent.image_generator.generate_images(image_prompts)

        # Generate audio if requested
        audio = {}
        if request.include_audio:
            if tamil_story and "tamil" in request.language:
                audio["tamil"] = kural_agent.narration_engine.generate_audio(tamil_story, "tamil")
            if english_story and "english" in request.language:
                audio["english"] = kural_agent.narration_engine.generate_audio(english_story, "english")

        # Generate video
        video = kural_agent.video_builder.create_video(
            images,
            audio,
            tamil_story if "tamil" in request.language else None,
            english_story if "english" in request.language else None
        )

        return {
            "kural_id": request.kural_id,
            "video": video
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    """
    Analyze a Kural.

    Args:
        request: AnalysisRequest object with kural_id.

    Returns:
        Dictionary with analysis information.
    """
    try:
        # Get the Kural details
        kural_details = kural_agent.kural_matcher._get_kural_details(request.kural_id)
        kural_text = kural_details.get("tamil", "")
        kural_translation = kural_details.get("english", "")

        # Generate literary analysis
        analysis = kural_agent.insight_engine.analyze(
            request.kural_id, kural_text, kural_translation
        )

        return {
            "kural_id": request.kural_id,
            "kural_text": kural_text,
            "kural_translation": kural_translation,
            "analysis": analysis["analysis"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/image/{image_id}")
async def get_image(image_id: str):
    """
    Get an image by ID.

    Args:
        image_id: The ID of the image.

    Returns:
        The image file.
    """
    try:
        # This is a simplified implementation
        # In a real application, you would look up the image in a database
        image_path = f"images/{image_id}.png"

        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image not found")

        return FileResponse(image_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/video/{video_id}")
async def get_video(video_id: str):
    """
    Get a video by ID.

    Args:
        video_id: The ID of the video.

    Returns:
        The video file.
    """
    try:
        # This is a simplified implementation
        # In a real application, you would look up the video in a database
        video_path = f"videos/{video_id}.mp4"

        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video not found")

        return FileResponse(video_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
