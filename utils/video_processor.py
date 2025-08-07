"""
Video Processing utilities for Event Situational Awareness System
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional
import os
from PIL import Image
import io
import base64
from config import config


class VideoProcessor:
    """Process videos to extract meaningful frames for AI analysis"""
    
    def __init__(self):
        self.motion_threshold = config.VIDEO_FRAME_SKIP_THRESHOLD
        self.max_frames = config.MAX_FRAMES_PER_VIDEO
        self.frame_interval = config.FRAME_EXTRACTION_INTERVAL
    
    def extract_frames_with_motion_detection(self, video_path: str) -> List[np.ndarray]:
        """
        Extract frames from video using motion-aware frame skipping
        
        Args:
            video_path: Path to the video file
            
        Returns:
            List of selected frames as numpy arrays
        """
        if not os.path.exists(video_path):
            print(f"Warning: Video file not found: {video_path}")
            return []
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video file: {video_path}")
            return []
        
        frames = []
        prev_frame = None
        frame_count = 0
        selected_count = 0
        
        try:
            while cap.isOpened() and selected_count < self.max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Skip frames based on interval to reduce processing
                if frame_count % self.frame_interval != 0:
                    continue
                
                # Convert to grayscale for motion detection
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                if prev_frame is not None:
                    # Calculate motion between frames
                    motion_score = self._calculate_motion_score(prev_frame, gray_frame)
                    
                    # Only select frame if significant motion detected
                    if motion_score > self.motion_threshold:
                        frames.append(frame.copy())
                        selected_count += 1
                        print(f"Selected frame {frame_count} with motion score: {motion_score:.3f}")
                else:
                    # Always include first frame
                    frames.append(frame.copy())
                    selected_count += 1
                    print(f"Selected first frame {frame_count}")
                
                prev_frame = gray_frame.copy()
                
        except Exception as e:
            print(f"Error processing video {video_path}: {str(e)}")
        finally:
            cap.release()
        
        print(f"Extracted {len(frames)} frames from {video_path}")
        return frames
    
    def _calculate_motion_score(self, prev_frame: np.ndarray, current_frame: np.ndarray) -> float:
        """
        Calculate motion score between two consecutive frames
        
        Args:
            prev_frame: Previous frame in grayscale
            current_frame: Current frame in grayscale
            
        Returns:
            Motion score (0.0 to 1.0)
        """
        try:
            # Calculate absolute difference
            diff = cv2.absdiff(prev_frame, current_frame)
            
            # Apply threshold to get binary image
            _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
            
            # Calculate percentage of pixels that changed
            motion_pixels = np.sum(thresh > 0)
            total_pixels = thresh.shape[0] * thresh.shape[1]
            motion_score = motion_pixels / total_pixels
            
            return motion_score
            
        except Exception as e:
            print(f"Error calculating motion score: {str(e)}")
            return 0.0
    
    def frame_to_base64(self, frame: np.ndarray) -> str:
        """
        Convert frame to base64 string for API transmission
        
        Args:
            frame: Frame as numpy array
            
        Returns:
            Base64 encoded image string
        """
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(rgb_frame)
            
            # Convert to bytes
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG', quality=85)
            
            # Encode to base64
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return img_base64
            
        except Exception as e:
            print(f"Error converting frame to base64: {str(e)}")
            return ""
    
    def process_video_file(self, video_path: str, zone_name: str) -> List[dict]:
        """
        Process a single video file and return frame data
        
        Args:
            video_path: Path to video file
            zone_name: Name of the zone (e.g., "Zone A")
            
        Returns:
            List of frame data dictionaries
        """
        frames = self.extract_frames_with_motion_detection(video_path)
        
        frame_data = []
        for i, frame in enumerate(frames):
            base64_frame = self.frame_to_base64(frame)
            if base64_frame:
                frame_data.append({
                    'zone': zone_name,
                    'frame_index': i,
                    'frame_base64': base64_frame,
                    'timestamp': f"Frame_{i:03d}",
                    'video_source': os.path.basename(video_path)
                })
        
        return frame_data
    
    def get_video_info(self, video_path: str) -> dict:
        """
        Get basic information about a video file
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video information
        """
        if not os.path.exists(video_path):
            return {'error': 'Video file not found'}
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {'error': 'Could not open video file'}
        
        try:
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            info = {
                'filename': os.path.basename(video_path),
                'total_frames': total_frames,
                'fps': fps,
                'duration_seconds': duration,
                'resolution': f"{width}x{height}",
                'width': width,
                'height': height
            }
            
            return info
            
        except Exception as e:
            return {'error': f'Error getting video info: {str(e)}'}
        finally:
            cap.release()


def create_sample_frames_for_testing():
    """Create sample colored frames for testing when no videos are available"""
    processor = VideoProcessor()
    
    # Create sample frames with different colors to simulate motion
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # Red, Green, Blue, Yellow
    sample_frames = []
    
    for i, color in enumerate(colors):
        # Create a 640x480 frame with solid color
        frame = np.full((480, 640, 3), color, dtype=np.uint8)
        
        # Add some text to make it more realistic
        cv2.putText(frame, f"Zone Sample {i+1}", (50, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        
        sample_frames.append(frame)
    
    return sample_frames


if __name__ == "__main__":
    # Test the video processor
    processor = VideoProcessor()
    
    # Test with sample frames if no videos available
    sample_frames = create_sample_frames_for_testing()
    print(f"Created {len(sample_frames)} sample frames for testing")
    
    # Convert first frame to base64 for testing
    if sample_frames:
        base64_data = processor.frame_to_base64(sample_frames[0])
        print(f"Base64 conversion successful: {len(base64_data)} characters")