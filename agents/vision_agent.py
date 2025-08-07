"""
Vision Agent for analyzing video frames using Google Gemini Vision API
"""
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import base64
import json
from config import config


class VisionAgent:
    """Agent responsible for analyzing video frames and extracting situational awareness data"""
    
    def __init__(self):
        """Initialize the Vision Agent with Gemini configuration"""
        try:
            genai.configure(api_key=config.GOOGLE_API_KEY)
            self.vision_model = genai.GenerativeModel(config.VISION_MODEL)
            print("Vision Agent initialized successfully")
        except Exception as e:
            print(f"Error initializing Vision Agent: {str(e)}")
            self.vision_model = None
    
    def analyze_frame(self, frame_data: dict) -> Dict[str, Any]:
        """
        Analyze a single frame using Gemini Vision API
        
        Args:
            frame_data: Dictionary containing frame information and base64 image
            
        Returns:
            Dictionary with analysis results
        """
        if not self.vision_model:
            return self._create_error_response("Vision model not initialized")
        
        try:
            # Create the analysis prompt
            prompt = self._create_analysis_prompt(frame_data['zone'])
            
            # Prepare the image for Gemini
            image_data = {
                'mime_type': 'image/jpeg',
                'data': frame_data['frame_base64']
            }
            
            # Generate analysis
            response = self.vision_model.generate_content([prompt, image_data])
            
            # Parse the response
            analysis_result = self._parse_gemini_response(response.text, frame_data)
            
            return analysis_result
            
        except Exception as e:
            print(f"Error analyzing frame: {str(e)}")
            return self._create_error_response(f"Analysis failed: {str(e)}")
    
    def analyze_multiple_frames(self, frames_data: List[dict]) -> List[Dict[str, Any]]:
        """
        Analyze multiple frames from a video
        
        Args:
            frames_data: List of frame data dictionaries
            
        Returns:
            List of analysis results
        """
        results = []
        
        for i, frame_data in enumerate(frames_data):
            print(f"Analyzing frame {i+1}/{len(frames_data)} for {frame_data.get('zone', 'Unknown Zone')}")
            result = self.analyze_frame(frame_data)
            results.append(result)
        
        return results
    
    def _create_analysis_prompt(self, zone_name: str) -> str:
        """
        Create a detailed prompt for frame analysis
        
        Args:
            zone_name: Name of the zone being analyzed
            
        Returns:
            Analysis prompt string
        """
        prompt = f"""
You are an expert situational awareness analyst examining a video frame from {zone_name} at an event.

Please analyze this image and provide a structured assessment in JSON format with the following information:

{{
    "zone": "{zone_name}",
    "crowd_density": "low|moderate|high|critical",
    "crowd_count_estimate": "estimated number of people visible",
    "crowd_behavior": "calm|excited|restless|agitated|dispersing|gathering",
    "potential_risks": ["list of identified risks or concerns"],
    "safety_observations": ["list of safety-related observations"],
    "infrastructure_status": ["observations about facilities, barriers, exits"],
    "weather_conditions": "description if visible",
    "lighting_conditions": "good|fair|poor|dark",
    "accessibility_issues": ["any accessibility concerns observed"],
    "recommended_actions": ["suggested immediate actions if any"],
    "confidence_score": 0.0-1.0,
    "additional_notes": "any other relevant observations"
}}

Focus on:
1. Crowd density and movement patterns
2. Potential safety hazards or bottlenecks
3. Infrastructure conditions (barriers, exits, facilities)
4. Any unusual behaviors or situations
5. Environmental factors affecting safety

Provide specific, actionable insights that would help event managers make informed decisions.
"""
        return prompt
    
    def _parse_gemini_response(self, response_text: str, frame_data: dict) -> Dict[str, Any]:
        """
        Parse Gemini API response and structure the data
        
        Args:
            response_text: Raw response from Gemini
            frame_data: Original frame data
            
        Returns:
            Structured analysis result
        """
        try:
            # Try to extract JSON from the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                analysis = json.loads(json_str)
            else:
                # If no JSON found, create structured response from text
                analysis = self._create_fallback_analysis(response_text, frame_data['zone'])
            
            # Add metadata
            analysis['frame_metadata'] = {
                'frame_index': frame_data.get('frame_index', 0),
                'timestamp': frame_data.get('timestamp', 'unknown'),
                'video_source': frame_data.get('video_source', 'unknown'),
                'analysis_timestamp': self._get_current_timestamp()
            }
            
            # Validate required fields
            analysis = self._validate_analysis_result(analysis)
            
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {str(e)}")
            return self._create_fallback_analysis(response_text, frame_data['zone'])
        except Exception as e:
            print(f"Error processing response: {str(e)}")
            return self._create_error_response(f"Response processing failed: {str(e)}")
    
    def _create_fallback_analysis(self, response_text: str, zone_name: str) -> Dict[str, Any]:
        """
        Create a fallback analysis when JSON parsing fails
        
        Args:
            response_text: Raw response text
            zone_name: Zone being analyzed
            
        Returns:
            Basic analysis structure
        """
        return {
            'zone': zone_name,
            'crowd_density': 'moderate',
            'crowd_count_estimate': 'unknown',
            'crowd_behavior': 'calm',
            'potential_risks': ['Analysis parsing incomplete'],
            'safety_observations': ['Manual review recommended'],
            'infrastructure_status': ['Status unclear'],
            'weather_conditions': 'unknown',
            'lighting_conditions': 'fair',
            'accessibility_issues': [],
            'recommended_actions': ['Review raw analysis output'],
            'confidence_score': 0.3,
            'additional_notes': f'Raw analysis: {response_text[:500]}...',
            'parsing_error': True
        }
    
    def _validate_analysis_result(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and ensure required fields are present
        
        Args:
            analysis: Analysis result dictionary
            
        Returns:
            Validated analysis result
        """
        required_fields = {
            'zone': 'unknown',
            'crowd_density': 'moderate',
            'crowd_count_estimate': 'unknown',
            'crowd_behavior': 'calm',
            'potential_risks': [],
            'safety_observations': [],
            'infrastructure_status': [],
            'weather_conditions': 'unknown',
            'lighting_conditions': 'fair',
            'accessibility_issues': [],
            'recommended_actions': [],
            'confidence_score': 0.5,
            'additional_notes': ''
        }
        
        for field, default_value in required_fields.items():
            if field not in analysis:
                analysis[field] = default_value
        
        # Ensure lists are actually lists
        list_fields = ['potential_risks', 'safety_observations', 'infrastructure_status', 
                      'accessibility_issues', 'recommended_actions']
        for field in list_fields:
            if not isinstance(analysis[field], list):
                analysis[field] = [str(analysis[field])] if analysis[field] else []
        
        # Ensure confidence_score is a float between 0 and 1
        try:
            analysis['confidence_score'] = max(0.0, min(1.0, float(analysis['confidence_score'])))
        except (ValueError, TypeError):
            analysis['confidence_score'] = 0.5
        
        return analysis
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Create an error response structure
        
        Args:
            error_message: Error description
            
        Returns:
            Error response dictionary
        """
        return {
            'zone': 'unknown',
            'crowd_density': 'unknown',
            'crowd_count_estimate': 'error',
            'crowd_behavior': 'unknown',
            'potential_risks': ['Analysis system error'],
            'safety_observations': ['System malfunction detected'],
            'infrastructure_status': ['Unable to assess'],
            'weather_conditions': 'unknown',
            'lighting_conditions': 'unknown',
            'accessibility_issues': [],
            'recommended_actions': ['Check system configuration'],
            'confidence_score': 0.0,
            'additional_notes': error_message,
            'error': True,
            'error_message': error_message
        }
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for analysis metadata"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_zone_summary(self, zone_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a summary of multiple frame analyses for a zone
        
        Args:
            zone_analyses: List of frame analysis results for a zone
            
        Returns:
            Zone summary dictionary
        """
        if not zone_analyses:
            return {'error': 'No analyses provided'}
        
        zone_name = zone_analyses[0].get('zone', 'Unknown')
        
        # Aggregate crowd density assessments
        density_counts = {}
        behaviors = []
        all_risks = []
        all_recommendations = []
        confidence_scores = []
        
        for analysis in zone_analyses:
            if analysis.get('error'):
                continue
                
            density = analysis.get('crowd_density', 'moderate')
            density_counts[density] = density_counts.get(density, 0) + 1
            
            behaviors.append(analysis.get('crowd_behavior', 'calm'))
            all_risks.extend(analysis.get('potential_risks', []))
            all_recommendations.extend(analysis.get('recommended_actions', []))
            
            if 'confidence_score' in analysis:
                confidence_scores.append(analysis['confidence_score'])
        
        # Determine most common density level
        most_common_density = max(density_counts.items(), key=lambda x: x[1])[0] if density_counts else 'moderate'
        
        # Remove duplicate risks and recommendations
        unique_risks = list(set(all_risks))
        unique_recommendations = list(set(all_recommendations))
        
        # Calculate average confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        
        summary = {
            'zone': zone_name,
            'total_frames_analyzed': len(zone_analyses),
            'successful_analyses': len([a for a in zone_analyses if not a.get('error')]),
            'overall_crowd_density': most_common_density,
            'density_distribution': density_counts,
            'common_behaviors': list(set(behaviors)),
            'aggregated_risks': unique_risks,
            'priority_actions': unique_recommendations,
            'average_confidence': round(avg_confidence, 2),
            'analysis_timestamp': self._get_current_timestamp()
        }
        
        return summary


if __name__ == "__main__":
    # Test the Vision Agent with sample data
    print("Testing Vision Agent...")
    
    # This would require actual API key to test
    # agent = VisionAgent()
    
    # Sample frame data for testing structure
    sample_frame_data = {
        'zone': 'Zone A',
        'frame_index': 0,
        'frame_base64': 'sample_base64_data',
        'timestamp': 'Frame_000',
        'video_source': 'zone_a.mp4'
    }
    
    print("Vision Agent structure validated successfully")