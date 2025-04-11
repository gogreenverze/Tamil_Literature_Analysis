"""
Video Builder - Creates videos from images and audio narration with enhanced transitions and effects.
"""

import os
import tempfile
import subprocess
import random
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union, Literal

from valluvarai.config import config
from valluvarai.utils.cache import cache

class VideoBuilder:
    """
    Creates videos from images and audio narration using FFmpeg with enhanced transitions and effects.
    """
    
    # Define available transitions
    TRANSITIONS = {
        'fade': 'fade=t=in:st=0:d=1,fade=t=out:st={duration-1}:d=1',
        'crossfade': 'xfade=transition=fade:duration=1',
        'fadeblack': 'xfade=transition=fadeblack:duration=1',
        'fadewhite': 'xfade=transition=fadewhite:duration=1',
        'slideleft': 'xfade=transition=slideleft:duration=1',
        'slideright': 'xfade=transition=slideright:duration=1',
        'slideup': 'xfade=transition=slideup:duration=1',
        'slidedown': 'xfade=transition=slidedown:duration=1',
        'circlecrop': 'xfade=transition=circlecrop:duration=1',
        'rectcrop': 'xfade=transition=rectcrop:duration=1',
        'distance': 'xfade=transition=distance:duration=1',
        'wipeleft': 'xfade=transition=wipeleft:duration=1',
        'wiperight': 'xfade=transition=wiperight:duration=1',
        'wipeup': 'xfade=transition=wipeup:duration=1',
        'wipedown': 'xfade=transition=wipedown:duration=1',
        'zoomin': 'zoompan=z=\'min(zoom+0.0015,1.5)\':d=25:s=1024x1024',
        'zoomout': 'zoompan=z=\'if(lte(zoom,1.0),1.5,max(1.001,zoom-0.0015))\':d=25:s=1024x1024',
        'kenburns': 'zoompan=z=\'min(max(zoom,pzoom)+0.0015,1.5)\':d=25:s=1024x1024:x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\'',
    }
    
    # Define available music genres
    MUSIC_GENRES = {
        'ambient': 'Ambient, calm, atmospheric background music',
        'classical': 'Classical Tamil music with traditional instruments',
        'emotional': 'Emotional, moving background score',
        'inspirational': 'Uplifting, inspirational background music',
        'traditional': 'Traditional Tamil folk music',
        'cinematic': 'Cinematic orchestral background score',
        'meditation': 'Peaceful meditation music with Tamil influences'
    }
    
    def __init__(self, output_dir: Optional[str] = None, music_dir: Optional[str] = None):
        """
        Initialize the VideoBuilder.
        
        Args:
            output_dir: Directory to save generated videos. If None, uses the default from config.
            music_dir: Directory containing background music files. If None, uses the default from config.
        """
        # Get configuration
        video_config = config.get_service_config("video_generation")
        
        # Set up output directory
        if output_dir:
            self.output_dir = Path(output_dir)
        elif video_config.get("output_dir"):
            self.output_dir = Path(video_config.get("output_dir"))
        else:
            self.output_dir = Path(tempfile.mkdtemp())
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set up music directory
        if music_dir:
            self.music_dir = Path(music_dir)
        elif video_config.get("music_path"):
            self.music_dir = Path(video_config.get("music_path"))
        else:
            self.music_dir = Path(__file__).parent.parent / "resources" / "music"
            
        # Create music directory if it doesn't exist
        os.makedirs(self.music_dir, exist_ok=True)
        
        # Set default parameters from config
        self.default_fps = video_config.get("default_fps", 24)
        self.default_duration = video_config.get("default_duration", 45)
        self.add_music_default = video_config.get("add_music", True)
        self.default_transition = video_config.get("default_transition", "crossfade")
        self.enable_effects = video_config.get("enable_effects", True)
        self.subtitle_style = video_config.get("subtitle_style", "FontSize=24,Alignment=2,BorderStyle=3,Outline=1,Shadow=0,MarginV=25")
    
    def create_video(
        self,
        images: List[Dict[str, Any]],
        audio: Dict[str, Dict[str, Any]],
        tamil_text: Optional[str] = None,
        english_text: Optional[str] = None,
        duration: Optional[int] = None,
        fps: Optional[int] = None,
        add_music: Optional[bool] = None,
        transition: Optional[str] = None,
        music_genre: Optional[str] = None,
        apply_effects: Optional[bool] = None,
        cache_result: bool = True
    ) -> Dict[str, Any]:
        """
        Create a video from images and audio narration with enhanced transitions and effects.
        
        Args:
            images: List of dictionaries with image information.
            audio: Dictionary with audio information for different languages.
            tamil_text: Tamil story text for subtitles.
            english_text: English story text for subtitles.
            duration: Target duration of the video in seconds. If None, uses the default from config.
            fps: Frames per second for the video. If None, uses the default from config.
            add_music: Whether to add background music. If None, uses the default from config.
            transition: Transition effect to use between images. If None, uses the default from config.
                Options: 'fade', 'crossfade', 'fadeblack', 'fadewhite', 'slideleft', 'slideright',
                'slideup', 'slidedown', 'circlecrop', 'rectcrop', 'distance', 'wipeleft',
                'wiperight', 'wipeup', 'wipedown', 'zoomin', 'zoomout', 'kenburns'.
            music_genre: Genre of background music to use. If None, selects randomly.
                Options: 'ambient', 'classical', 'emotional', 'inspirational', 'traditional',
                'cinematic', 'meditation'.
            apply_effects: Whether to apply visual effects to the video. If None, uses the default from config.
            cache_result: Whether to cache the result for future use.
            
        Returns:
            Dictionary with video information.
        """
        # Set default values from config if not provided
        duration_value = duration if duration is not None else self.default_duration
        fps_value = fps if fps is not None else self.default_fps
        add_music_value = add_music if add_music is not None else self.add_music_default
        transition_value = transition if transition is not None else self.default_transition
        apply_effects_value = apply_effects if apply_effects is not None else self.enable_effects
        
        # Check if we have a cached result
        if cache_result:
            cache_key = {
                "images": [img.get("file_path", "") for img in images],
                "audio": {k: v.get("file_path", "") for k, v in audio.items()},
                "tamil_text": tamil_text,
                "english_text": english_text,
                "duration": duration_value,
                "fps": fps_value,
                "add_music": add_music_value,
                "transition": transition_value,
                "music_genre": music_genre,
                "apply_effects": apply_effects_value
            }
            cached_result = cache.get("videos", cache_key)
            if cached_result and os.path.exists(cached_result.get("file_path", "")):
                return cached_result
        
        # Check if FFmpeg is available
        if not self._is_ffmpeg_available():
            return {
                "success": False,
                "error": "FFmpeg is not available. Please install FFmpeg to generate videos.",
                "file_path": None
            }
        
        try:
            # Filter out images with missing file paths
            valid_images = [img for img in images if img.get("file_path") and os.path.exists(img.get("file_path"))]
            
            if not valid_images:
                return {
                    "success": False,
                    "error": "No valid images available for video creation.",
                    "file_path": None
                }
            
            # Get audio files
            tamil_audio = audio.get("tamil", {}).get("file_path") if "tamil" in audio else None
            english_audio = audio.get("english", {}).get("file_path") if "english" in audio else None
            
            # Determine which audio to use
            audio_file = None
            if tamil_audio and os.path.exists(tamil_audio):
                audio_file = tamil_audio
            elif english_audio and os.path.exists(english_audio):
                audio_file = english_audio
            
            # Create a temporary directory for intermediate files
            temp_dir = Path(tempfile.mkdtemp())
            
            # Select background music if requested
            background_music = None
            if add_music_value and not audio_file:
                background_music = self._select_background_music(music_genre, temp_dir)
            
            # Create image sequence with transitions
            image_sequence = self._create_image_sequence_with_transitions(
                valid_images, 
                duration_value, 
                transition_value,
                apply_effects_value,
                temp_dir
            )
            
            # Create subtitles if text is provided
            subtitle_file = None
            if tamil_text or english_text:
                subtitle_file = self._create_subtitles(tamil_text, english_text, duration_value, temp_dir)
            
            # Generate the video
            timestamp = int(os.path.getmtime(valid_images[0]['file_path']))
            output_file = self.output_dir / f"valluvar_story_{timestamp}_{transition_value}.mp4"
            
            # Create the video with FFmpeg
            self._generate_video(
                image_sequence, 
                audio_file, 
                subtitle_file, 
                output_file, 
                duration_value, 
                fps_value, 
                add_music_value,
                background_music
            )
            
            result = {
                "success": True,
                "file_path": str(output_file),
                "duration": duration_value,
                "has_audio": audio_file is not None or background_music is not None,
                "has_subtitles": subtitle_file is not None,
                "transition": transition_value,
                "effects_applied": apply_effects_value
            }
            
            # Cache the result if requested
            if cache_result:
                cache.set("videos", cache_key, result)
            
            return result
            
        except Exception as e:
            print(f"Error creating video: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": None
            }
    
    def _select_background_music(self, genre: Optional[str], temp_dir: Path) -> Optional[str]:
        """
        Select background music based on the genre.
        
        Args:
            genre: The genre of music to select. If None, selects randomly.
            temp_dir: Temporary directory for intermediate files.
            
        Returns:
            Path to the selected music file, or None if no music is available.
        """
        # Check if we have any music files
        if not os.path.exists(self.music_dir):
            return None
        
        # Get all music files
        music_files = []
        for ext in ['.mp3', '.wav', '.ogg']:
            music_files.extend(list(self.music_dir.glob(f"*{ext}")))
        
        if not music_files:
            return None
        
        # If genre is specified, filter by genre
        if genre:
            genre_files = [f for f in music_files if genre.lower() in f.name.lower()]
            if genre_files:
                music_files = genre_files
        
        # Select a random music file
        selected_music = random.choice(music_files)
        
        # Copy to temp directory to avoid permission issues
        temp_music = temp_dir / selected_music.name
        shutil.copy(selected_music, temp_music)
        
        return str(temp_music)
    
    def _create_image_sequence_with_transitions(self, 
                                              images: List[Dict[str, Any]], 
                                              duration: int,
                                              transition: str,
                                              apply_effects: bool,
                                              temp_dir: Path) -> List[Dict[str, Any]]:
        """
        Create a sequence of images with transitions for the video.
        
        Args:
            images: List of dictionaries with image information.
            duration: Target duration of the video in seconds.
            transition: Transition effect to use between images.
            apply_effects: Whether to apply visual effects to the images.
            temp_dir: Temporary directory for intermediate files.
            
        Returns:
            List of dictionaries with image sequence information.
        """
        # Calculate duration for each image
        num_images = len(images)
        image_duration = duration / num_images
        
        # Create the sequence
        sequence = []
        
        for i, img in enumerate(images):
            # Get the transition filter
            transition_filter = self.TRANSITIONS.get(transition, self.TRANSITIONS['crossfade'])
            
            # Apply effects if requested
            filters = []
            if apply_effects:
                # Add random effects based on the image content
                if i % 3 == 0:  # Every third image gets a zoom effect
                    filters.append(self.TRANSITIONS['zoomin'])
                elif i % 3 == 1:  # Every third+1 image gets a ken burns effect
                    filters.append(self.TRANSITIONS['kenburns'])
                # Otherwise, no additional effects
            
            # Add the transition filter
            if i > 0:  # Don't add transition for the first image
                filters.append(transition_filter)
            
            sequence.append({
                "file_path": img["file_path"],
                "duration": image_duration,
                "filters": filters
            })
        
        return sequence
    
    def _is_ffmpeg_available(self) -> bool:
        """
        Check if FFmpeg is available on the system.
        
        Returns:
            True if FFmpeg is available, False otherwise.
        """
        try:
            subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _create_image_sequence(
        self,
        images: List[Dict[str, Any]],
        duration: int,
        temp_dir: Path
    ) -> List[Tuple[str, float]]:
        """
        Create a sequence of images with durations for the video.
        
        Args:
            images: List of dictionaries with image information.
            duration: Target duration of the video in seconds.
            temp_dir: Temporary directory for intermediate files.
            
        Returns:
            List of tuples with (image_path, duration_in_seconds).
        """
        # Calculate duration for each image
        num_images = len(images)
        image_duration = duration / num_images
        
        # Create the sequence
        sequence = []
        for img in images:
            sequence.append((img["file_path"], image_duration))
        
        return sequence
    
    def _create_subtitles(
        self,
        tamil_text: Optional[str],
        english_text: Optional[str],
        duration: int,
        temp_dir: Path
    ) -> Optional[str]:
        """
        Create subtitles for the video.
        
        Args:
            tamil_text: Tamil story text for subtitles.
            english_text: English story text for subtitles.
            duration: Target duration of the video in seconds.
            temp_dir: Temporary directory for intermediate files.
            
        Returns:
            Path to the subtitle file, or None if no subtitles were created.
        """
        if not tamil_text and not english_text:
            return None
        
        # Create a subtitle file
        subtitle_file = temp_dir / "subtitles.srt"
        
        with open(subtitle_file, "w", encoding="utf-8") as f:
            subtitle_index = 1
            
            # Add Tamil subtitles
            if tamil_text:
                # Split the text into sentences
                sentences = tamil_text.split(".")
                sentences = [s.strip() for s in sentences if s.strip()]
                
                # Calculate time per sentence
                time_per_sentence = duration / (len(sentences) + (1 if english_text else 0))
                
                for i, sentence in enumerate(sentences):
                    start_time = i * time_per_sentence
                    end_time = (i + 1) * time_per_sentence
                    
                    f.write(f"{subtitle_index}\n")
                    f.write(f"{self._format_time(start_time)} --> {self._format_time(end_time)}\n")
                    f.write(f"{sentence}\n\n")
                    
                    subtitle_index += 1
            
            # Add English subtitles
            if english_text:
                # Split the text into sentences
                sentences = english_text.split(".")
                sentences = [s.strip() for s in sentences if s.strip()]
                
                # Calculate time per sentence
                time_per_sentence = duration / (len(sentences) + (1 if tamil_text else 0))
                
                # Start after Tamil subtitles if present
                start_offset = len(tamil_text.split(".")) * time_per_sentence if tamil_text else 0
                
                for i, sentence in enumerate(sentences):
                    start_time = start_offset + i * time_per_sentence
                    end_time = start_offset + (i + 1) * time_per_sentence
                    
                    f.write(f"{subtitle_index}\n")
                    f.write(f"{self._format_time(start_time)} --> {self._format_time(end_time)}\n")
                    f.write(f"{sentence}\n\n")
                    
                    subtitle_index += 1
        
        return str(subtitle_file)
    
    def _format_time(self, seconds: float) -> str:
        """
        Format time in SRT format (HH:MM:SS,mmm).
        
        Args:
            seconds: Time in seconds.
            
        Returns:
            Formatted time string.
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"
    
    def _generate_video(
        self,
        image_sequence: List[Dict[str, Any]],
        audio_file: Optional[str],
        subtitle_file: Optional[str],
        output_file: Path,
        duration: int,
        fps: int,
        add_music: bool,
        background_music: Optional[str] = None
    ) -> None:
        """
        Generate the video using FFmpeg with enhanced transitions and effects.
        
        Args:
            image_sequence: List of dictionaries with image sequence information.
            audio_file: Path to the audio file.
            subtitle_file: Path to the subtitle file.
            output_file: Path to the output video file.
            duration: Target duration of the video in seconds.
            fps: Frames per second for the video.
            add_music: Whether to add background music.
            background_music: Path to the background music file. If None and add_music is True,
                a default music file will be used.
        """
        # Create a temporary file for the FFmpeg input
        temp_dir = Path(tempfile.mkdtemp())
        input_file = temp_dir / "input.txt"
        filter_file = temp_dir / "filters.txt"
        
        # Prepare filter complex for transitions and effects
        filter_complex = []
        
        # Write the input file for FFmpeg and prepare filters
        with open(input_file, "w", encoding="utf-8") as f:
            for i, img_info in enumerate(image_sequence):
                img_path = img_info["file_path"]
                img_duration = img_info["duration"]
                filters = img_info.get("filters", [])
                
                f.write(f"file '{img_path}'\n")
                f.write(f"duration {img_duration}\n")
                
                # Add filters to filter complex if any
                if filters:
                    for filter_str in filters:
                        # Replace placeholders in filter string
                        filter_str = filter_str.replace("{duration-1}", str(img_duration-1))
                        filter_complex.append(f"[{i}:v]{filter_str}[v{i}]")
            
            # Add the last image again without duration to avoid cutting it off
            last_img_path = image_sequence[-1]["file_path"]
            f.write(f"file '{last_img_path}'\n")
        
        # Write filter complex to file if needed
        if filter_complex:
            with open(filter_file, "w", encoding="utf-8") as f:
                f.write(";".join(filter_complex))
        
        # Base FFmpeg command
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output file if it exists
            "-f", "concat",
            "-safe", "0",
            "-i", str(input_file),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", str(fps),
            "-preset", "medium",
            "-crf", "23"
        ]
        
        # Add filter complex if available
        if filter_complex:
            cmd.extend([
                "-filter_complex_script", str(filter_file)
            ])
        
        # Add audio if available
        if audio_file and os.path.exists(audio_file):
            cmd.extend([
                "-i", audio_file,
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest"
            ])
        
        # Add background music if requested
        elif add_music:
            if background_music and os.path.exists(background_music):
                cmd.extend([
                    "-i", background_music,
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-shortest"
                ])
            else:
                # Use a placeholder for background music if no file is available
                cmd.extend([
                    "-f", "lavfi",
                    "-i", "anullsrc=r=44100:cl=stereo",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-shortest"
                ])
        
        # Add subtitles if available
        if subtitle_file and os.path.exists(subtitle_file):
            cmd.extend([
                "-vf", f"subtitles={subtitle_file}:force_style='{self.subtitle_style}'"
            ])
        
        # Output file
        cmd.append(str(output_file))
        
        # Run FFmpeg
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
            raise
