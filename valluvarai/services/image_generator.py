"""
Image Generator - Generates images based on prompts using AI services.
"""

import os
import tempfile
import time
import base64
from pathlib import Path
from typing import List, Optional, Dict, Any
import random

try:
    import requests
    from PIL import Image
    import numpy as np
    from io import BytesIO
    IMAGE_LIBS_AVAILABLE = True
except ImportError:
    IMAGE_LIBS_AVAILABLE = False

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class ImageGenerator:
    """
    Generates images based on prompts using AI services like DALL-E or Stable Diffusion.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        provider: Optional[str] = None,
        output_dir: Optional[str] = None,
        image_size: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize the ImageGenerator.

        Args:
            api_key: API key for the image generation service. If None, uses the key from config.
            provider: The provider to use ("openai", "stability", "leonardo", etc.). If None, uses the provider from config.
            output_dir: Directory to save generated images. If None, uses a temporary directory.
            image_size: Size of the generated images. If None, uses the size from config.
            model: The model to use for image generation. If None, uses the model from config.
        """
        # Try to import config if available
        try:
            from valluvarai.config import config
            # Get configuration
            image_gen_config = config.get_service_config("image_generation")
            self.api_key = api_key or config.get_api_key(provider or image_gen_config.get("provider", "openai")) or os.environ.get("OPENAI_API_KEY")
            self.provider = provider or image_gen_config.get("provider", "openai")
            self.image_size = image_size or image_gen_config.get("image_size", "1024x1024")
            self.model = model or image_gen_config.get("model", "dall-e-3")
            self.fallback_to_placeholder = image_gen_config.get("fallback_to_placeholder", True)
        except ImportError:
            # If config is not available, use default values
            self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
            self.provider = provider or "openai"
            self.image_size = image_size or "1024x1024"
            self.model = model or "dall-e-3"
            self.fallback_to_placeholder = True

        self.client = None

        # Set up output directory
        if output_dir:
            self.output_dir = Path(output_dir)
            os.makedirs(self.output_dir, exist_ok=True)
        else:
            self.output_dir = Path(tempfile.mkdtemp())
            os.makedirs(self.output_dir, exist_ok=True)

        # Initialize the client if possible
        if OPENAI_AVAILABLE and self.api_key and self.provider == "openai":
            try:
                self.client = OpenAI(api_key=self.api_key)
                print("OpenAI client initialized successfully.")
            except Exception as e:
                print(f"Error initializing OpenAI client: {e}")
                self.client = None

    def generate_images(self, prompts: List[str]) -> List[Dict[str, Any]]:
        """
        Generate images based on the provided prompts.

        Args:
            prompts: List of text prompts for image generation.

        Returns:
            List of dictionaries with image information.
        """
        # Check if we have any prompts
        if not prompts:
            print("No prompts provided for image generation.")
            return [self._generate_placeholder("No prompt provided", 0)]

        results = []

        # Check if we have a valid API key for the selected provider
        if self.provider == "openai" and not self.api_key:
            print("No OpenAI API key provided. Using placeholder images.")
            for i, prompt in enumerate(prompts):
                results.append(self._generate_placeholder(prompt, i, error="No OpenAI API key provided"))
            return results

        for i, prompt in enumerate(prompts):
            try:
                print(f"Generating image {i+1}/{len(prompts)} with provider: {self.provider}")

                if self.provider == "openai" and OPENAI_AVAILABLE and self.client:
                    result = self._generate_with_openai(prompt, i)
                elif self.provider == "stability" and self.api_key:
                    result = self._generate_with_stability(prompt, i)
                elif self.provider == "leonardo" and self.api_key:
                    result = self._generate_with_leonardo(prompt, i)
                else:
                    # Fall back to placeholder images if no provider is available
                    error_msg = f"Provider '{self.provider}' not available or not configured properly."
                    print(error_msg)
                    result = self._generate_placeholder(prompt, i, error=error_msg)

                results.append(result)

                # Add a small delay to avoid rate limiting
                time.sleep(0.5)

            except Exception as e:
                error_msg = f"Error generating image for prompt {i}: {e}"
                print(error_msg)
                # Add a placeholder image on error
                results.append(self._generate_placeholder(prompt, i, error=error_msg))

        return results

    def _generate_with_openai(self, prompt: str, index: int) -> Dict[str, Any]:
        """
        Generate an image using OpenAI's DALL-E.

        Args:
            prompt: The text prompt for image generation.
            index: Index of the prompt in the list.

        Returns:
            Dictionary with image information.
        """
        try:
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size=self.image_size,
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url

            # Download the image
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                # Save the image
                filename = f"image_{index}_{int(time.time())}.png"
                file_path = self.output_dir / filename

                with open(file_path, "wb") as f:
                    f.write(image_response.content)

                return {
                    "success": True,
                    "file_path": str(file_path),
                    "url": image_url,
                    "prompt": prompt,
                    "provider": "openai"
                }
            else:
                raise Exception(f"Failed to download image: {image_response.status_code}")

        except Exception as e:
            error_msg = f"Error with OpenAI image generation: {e}"
            print(error_msg)
            return self._generate_placeholder(prompt, index, error=error_msg)

    def _generate_with_stability(self, prompt: str, index: int) -> Dict[str, Any]:
        """
        Generate an image using Stability AI's API.

        Args:
            prompt: The text prompt for image generation.
            index: Index of the prompt in the list.

        Returns:
            Dictionary with image information.
        """
        try:
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            body = {
                "text_prompts": [
                    {
                        "text": prompt,
                        "weight": 1.0
                    }
                ],
                "cfg_scale": 7,
                "height": 1024,
                "width": 1024,
                "samples": 1,
                "steps": 30
            }

            response = requests.post(url, headers=headers, json=body)

            if response.status_code == 200:
                data = response.json()

                # Get the image data
                image_data = data["artifacts"][0]["base64"]

                # Save the image
                filename = f"image_{index}_{int(time.time())}.png"
                file_path = self.output_dir / filename

                with open(file_path, "wb") as f:
                    f.write(base64.b64decode(image_data))

                return {
                    "success": True,
                    "file_path": str(file_path),
                    "url": None,  # No URL for Stability AI
                    "prompt": prompt,
                    "provider": "stability"
                }
            else:
                raise Exception(f"Stability AI API error: {response.status_code} - {response.text}")

        except Exception as e:
            error_msg = f"Error with Stability AI image generation: {e}"
            print(error_msg)
            return self._generate_placeholder(prompt, index, error=error_msg)

    def _generate_with_leonardo(self, prompt: str, index: int) -> Dict[str, Any]:
        """
        Generate an image using Leonardo AI's API.

        Args:
            prompt: The text prompt for image generation.
            index: Index of the prompt in the list.

        Returns:
            Dictionary with image information.
        """
        try:
            # Leonardo AI API endpoints
            generation_url = "https://cloud.leonardo.ai/api/rest/v1/generations"

            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": f"Bearer {self.api_key}"
            }

            # Model ID for Leonardo.AI (example)
            model_id = "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3"  # Leonardo Creative

            # Create generation
            generation_payload = {
                "prompt": prompt,
                "modelId": model_id,
                "width": 1024,
                "height": 1024,
                "num_images": 1,
                "promptMagic": True
            }

            generation_response = requests.post(generation_url, json=generation_payload, headers=headers)

            if generation_response.status_code == 200:
                generation_data = generation_response.json()
                generation_id = generation_data["sdGenerationJob"]["generationId"]

                # Poll for generation completion
                max_attempts = 30
                for attempt in range(max_attempts):
                    # Check generation status
                    status_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"
                    status_response = requests.get(status_url, headers=headers)

                    if status_response.status_code == 200:
                        status_data = status_response.json()

                        # Check if generation is complete
                        if status_data["generations_by_pk"]["status"] == "COMPLETE":
                            # Get the image URL
                            image_url = status_data["generations_by_pk"]["generated_images"][0]["url"]

                            # Download the image
                            image_response = requests.get(image_url)
                            if image_response.status_code == 200:
                                # Save the image
                                filename = f"image_{index}_{int(time.time())}.png"
                                file_path = self.output_dir / filename

                                with open(file_path, "wb") as f:
                                    f.write(image_response.content)

                                return {
                                    "success": True,
                                    "file_path": str(file_path),
                                    "url": image_url,
                                    "prompt": prompt,
                                    "provider": "leonardo"
                                }
                            else:
                                raise Exception(f"Failed to download image: {image_response.status_code}")

                        # If not complete, wait and try again
                        time.sleep(2)
                    else:
                        raise Exception(f"Leonardo AI API error: {status_response.status_code} - {status_response.text}")

                # If we've reached here, generation timed out
                raise Exception("Leonardo AI generation timed out")
            else:
                raise Exception(f"Leonardo AI API error: {generation_response.status_code} - {generation_response.text}")

        except Exception as e:
            error_msg = f"Error with Leonardo AI image generation: {e}"
            print(error_msg)
            return self._generate_placeholder(prompt, index, error=error_msg)

    def _generate_placeholder(self, prompt: str, index: int, error: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a placeholder image when no provider is available or on error.

        Args:
            prompt: The text prompt for image generation.
            index: Index of the prompt in the list.
            error: Optional error message to include in the placeholder image.

        Returns:
            Dictionary with image information.
        """
        if not IMAGE_LIBS_AVAILABLE:
            # If PIL is not available, just return metadata
            filename = f"placeholder_{index}.png"
            file_path = self.output_dir / filename

            return {
                "success": False,
                "file_path": str(file_path),
                "url": None,
                "prompt": prompt,
                "provider": "placeholder",
                "error": error or "Image libraries not available"
            }

        try:
            # Create a simple colored image with text
            width, height = 512, 512

            # Generate a random color based on the hash of the prompt
            prompt_hash = hash(prompt)
            r = (prompt_hash & 0xFF0000) >> 16
            g = (prompt_hash & 0x00FF00) >> 8
            b = prompt_hash & 0x0000FF

            # Create a gradient background
            array = np.zeros((height, width, 3), dtype=np.uint8)
            for y in range(height):
                for x in range(width):
                    array[y, x, 0] = int(r * (1 - y/height) + (255 - r) * (y/height))
                    array[y, x, 1] = int(g * (1 - x/width) + (255 - g) * (x/width))
                    array[y, x, 2] = int(b * (1 - (x+y)/(width+height)) + (255 - b) * ((x+y)/(width+height)))

            # Create the image
            image = Image.fromarray(array)

            # Save the image
            filename = f"placeholder_{index}_{int(time.time())}.png"
            file_path = self.output_dir / filename
            image.save(file_path)

            # If we have an error message, try to add it to the image
            if error and hasattr(image, "text"):
                try:
                    from PIL import ImageDraw, ImageFont
                    draw = ImageDraw.Draw(image)
                    # Use a default font
                    font_size = 20
                    try:
                        font = ImageFont.truetype("Arial", font_size)
                    except:
                        font = ImageFont.load_default()

                    # Wrap text to fit in the image
                    lines = []
                    words = error.split()
                    current_line = words[0]
                    for word in words[1:]:
                        if len(current_line + " " + word) * font_size < width - 40:
                            current_line += " " + word
                        else:
                            lines.append(current_line)
                            current_line = word
                    lines.append(current_line)

                    # Draw text
                    y = height // 2 - (len(lines) * font_size) // 2
                    for line in lines:
                        draw.text((width // 2, y), line, fill=(255, 255, 255), font=font, anchor="mm")
                        y += font_size + 5
                except Exception as e:
                    print(f"Error adding text to placeholder image: {e}")

            return {
                "success": False,
                "file_path": str(file_path),
                "url": None,
                "prompt": prompt,
                "provider": "placeholder",
                "error": error or "No image provider available or error occurred"
            }

        except Exception as e:
            print(f"Error generating placeholder image: {e}")
            return {
                "success": False,
                "file_path": None,
                "url": None,
                "prompt": prompt,
                "provider": "none",
                "error": error or str(e)
            }
