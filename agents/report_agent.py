"""
Report Agent for analyzing field reports and text data using Google Gemini API
"""
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime
from config import config


class ReportAgent:
    """Agent responsible for analyzing field reports and extracting key insights"""
    
    def __init__(self):
        """Initialize the Report Agent with Gemini configuration"""
        try:
            genai.configure(api_key=config.GOOGLE_API_KEY)
            self.text_model = genai.GenerativeModel(config.TEXT_MODEL)
            print("Report Agent initialized successfully")
        except Exception as e:
            print(f"Error initializing Report Agent: {str(e)}")
            self.text_model = None
    
    def analyze_field_reports(self, reports_file_path: str = None) -> Dict[str, Any]:
        """
        Analyze field reports from a text file
        
        Args:
            reports_file_path: Path to the field reports file
            
        Returns:
            Dictionary with analysis results
        """
        if reports_file_path is None:
            reports_file_path = config.FIELD_REPORTS_FILE
        
        if not self.text_model:
            return self._create_error_response("Text model not initialized")
        
        try:
            # Read the field reports
            reports_content = self._read_reports_file(reports_file_path)
            if not reports_content:
                return self._create_error_response("Could not read field reports")
            
            # Analyze the reports using Gemini
            analysis_result = self._analyze_reports_content(reports_content)
            
            return analysis_result
            
        except Exception as e:
            print(f"Error analyzing field reports: {str(e)}")
            return self._create_error_response(f"Analysis failed: {str(e)}")
    
    def _read_reports_file(self, file_path: str) -> Optional[str]:
        """
        Read the field reports file
        
        Args:
            file_path: Path to the reports file
            
        Returns:
            File content as string or None if error
        """
        try:
            if not os.path.exists(file_path):
                print(f"Field reports file not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
            
            if not content:
                print("Field reports file is empty")
                return None
            
            print(f"Successfully read field reports: {len(content)} characters")
            return content
            
        except Exception as e:
            print(f"Error reading field reports file: {str(e)}")
            return None
    
    def _analyze_reports_content(self, reports_content: str) -> Dict[str, Any]:
        """
        Analyze field reports content using Gemini API
        
        Args:
            reports_content: Raw text content of field reports
            
        Returns:
            Structured analysis result
        """
        try:
            # Create analysis prompt
            prompt = self._create_reports_analysis_prompt()
            
            # Combine prompt with reports content
            full_prompt = f"{prompt}\n\nFIELD REPORTS TO ANALYZE:\n{reports_content}"
            
            # Generate analysis
            response = self.text_model.generate_content(full_prompt)
            
            # Parse the response
            analysis_result = self._parse_reports_response(response.text)
            
            return analysis_result
            
        except Exception as e:
            print(f"Error in reports content analysis: {str(e)}")
            return self._create_error_response(f"Content analysis failed: {str(e)}")
    
    def _create_reports_analysis_prompt(self) -> str:
        """
        Create a detailed prompt for field reports analysis
        
        Returns:
            Analysis prompt string
        """
        prompt = """
You are an expert situational awareness analyst examining field reports from an event.

Please analyze the field reports and provide a structured assessment in JSON format with the following information:

{
    "event_overview": {
        "event_type": "type of event",
        "date": "event date",
        "time": "report time",
        "overall_status": "green|yellow|orange|red"
    },
    "zone_summaries": [
        {
            "zone_name": "zone identifier",
            "status": "operational status",
            "crowd_density": "low|moderate|high|critical",
            "crowd_estimate": "number of people",
            "key_issues": ["list of issues"],
            "infrastructure_status": "condition description",
            "security_alerts": ["any security concerns"]
        }
    ],
    "priority_issues": [
        {
            "issue": "description of issue",
            "zone": "affected zone",
            "severity": "low|medium|high|critical",
            "recommended_action": "suggested response",
            "timeline": "urgency indicator"
        }
    ],
    "resource_status": {
        "medical_teams": "status and capacity",
        "security_personnel": "deployment status",
        "emergency_services": "readiness level",
        "communication_systems": "operational status"
    },
    "environmental_factors": {
        "weather_conditions": "current weather",
        "weather_forecast": "upcoming conditions",
        "visibility": "lighting conditions",
        "environmental_risks": ["weather-related concerns"]
    },
    "operational_recommendations": [
        {
            "recommendation": "specific action",
            "priority": "high|medium|low",
            "target_zone": "affected area",
            "estimated_impact": "expected outcome"
        }
    ],
    "key_metrics": {
        "total_crowd_estimate": "overall attendance",
        "incident_count": "number of incidents",
        "medical_cases": "medical interventions",
        "security_incidents": "security events"
    },
    "next_actions": [
        "immediate actions needed"
    ],
    "confidence_assessment": {
        "data_quality": "high|medium|low",
        "information_completeness": "percentage or description",
        "reliability_score": 0.0-1.0
    }
}

Focus on:
1. Extracting key operational data from each zone
2. Identifying priority issues and risks
3. Assessing resource deployment and needs
4. Environmental factors affecting operations
5. Providing actionable recommendations
6. Quantifying crowd estimates and incident counts

Be specific and actionable in your analysis. If certain information is not available in the reports, indicate this clearly.
"""
        return prompt
    
    def _parse_reports_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Gemini API response for field reports analysis
        
        Args:
            response_text: Raw response from Gemini
            
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
                analysis = self._create_fallback_reports_analysis(response_text)
            
            # Add metadata
            analysis['analysis_metadata'] = {
                'analysis_timestamp': datetime.now().isoformat(),
                'agent_type': 'report_agent',
                'analysis_version': '1.0'
            }
            
            # Validate the analysis structure
            analysis = self._validate_reports_analysis(analysis)
            
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {str(e)}")
            return self._create_fallback_reports_analysis(response_text)
        except Exception as e:
            print(f"Error processing reports response: {str(e)}")
            return self._create_error_response(f"Response processing failed: {str(e)}")
    
    def _create_fallback_reports_analysis(self, response_text: str) -> Dict[str, Any]:
        """
        Create a fallback analysis when JSON parsing fails
        
        Args:
            response_text: Raw response text
            
        Returns:
            Basic analysis structure
        """
        return {
            'event_overview': {
                'event_type': 'unknown',
                'date': 'unknown',
                'time': 'unknown',
                'overall_status': 'yellow'
            },
            'zone_summaries': [],
            'priority_issues': [
                {
                    'issue': 'Report analysis parsing incomplete',
                    'zone': 'system',
                    'severity': 'medium',
                    'recommended_action': 'Manual review of field reports',
                    'timeline': 'immediate'
                }
            ],
            'resource_status': {
                'medical_teams': 'status unknown',
                'security_personnel': 'status unknown',
                'emergency_services': 'status unknown',
                'communication_systems': 'status unknown'
            },
            'environmental_factors': {
                'weather_conditions': 'unknown',
                'weather_forecast': 'unknown',
                'visibility': 'unknown',
                'environmental_risks': []
            },
            'operational_recommendations': [],
            'key_metrics': {
                'total_crowd_estimate': 'unknown',
                'incident_count': 'unknown',
                'medical_cases': 'unknown',
                'security_incidents': 'unknown'
            },
            'next_actions': ['Review raw field reports manually'],
            'confidence_assessment': {
                'data_quality': 'low',
                'information_completeness': 'incomplete',
                'reliability_score': 0.3
            },
            'raw_analysis': response_text[:1000] + '...' if len(response_text) > 1000 else response_text,
            'parsing_error': True
        }
    
    def _validate_reports_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and ensure required fields are present in reports analysis
        
        Args:
            analysis: Analysis result dictionary
            
        Returns:
            Validated analysis result
        """
        # Ensure required top-level keys exist
        required_keys = {
            'event_overview': {},
            'zone_summaries': [],
            'priority_issues': [],
            'resource_status': {},
            'environmental_factors': {},
            'operational_recommendations': [],
            'key_metrics': {},
            'next_actions': [],
            'confidence_assessment': {}
        }
        
        for key, default_value in required_keys.items():
            if key not in analysis:
                analysis[key] = default_value
        
        # Validate event_overview structure
        event_overview_defaults = {
            'event_type': 'unknown',
            'date': 'unknown',
            'time': 'unknown',
            'overall_status': 'yellow'
        }
        
        for key, default_value in event_overview_defaults.items():
            if key not in analysis['event_overview']:
                analysis['event_overview'][key] = default_value
        
        # Validate confidence_assessment structure
        confidence_defaults = {
            'data_quality': 'medium',
            'information_completeness': 'partial',
            'reliability_score': 0.5
        }
        
        for key, default_value in confidence_defaults.items():
            if key not in analysis['confidence_assessment']:
                analysis['confidence_assessment'][key] = default_value
        
        # Ensure reliability_score is a float between 0 and 1
        try:
            score = analysis['confidence_assessment']['reliability_score']
            analysis['confidence_assessment']['reliability_score'] = max(0.0, min(1.0, float(score)))
        except (ValueError, TypeError):
            analysis['confidence_assessment']['reliability_score'] = 0.5
        
        return analysis
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Create an error response structure for reports analysis
        
        Args:
            error_message: Error description
            
        Returns:
            Error response dictionary
        """
        return {
            'event_overview': {
                'event_type': 'error',
                'date': 'unknown',
                'time': 'unknown',
                'overall_status': 'red'
            },
            'zone_summaries': [],
            'priority_issues': [
                {
                    'issue': 'Report analysis system error',
                    'zone': 'system',
                    'severity': 'critical',
                    'recommended_action': 'Check system configuration and API access',
                    'timeline': 'immediate'
                }
            ],
            'resource_status': {
                'medical_teams': 'system error',
                'security_personnel': 'system error',
                'emergency_services': 'system error',
                'communication_systems': 'system error'
            },
            'environmental_factors': {
                'weather_conditions': 'unknown',
                'weather_forecast': 'unknown',
                'visibility': 'unknown',
                'environmental_risks': ['System analysis unavailable']
            },
            'operational_recommendations': [
                {
                    'recommendation': 'Restore report analysis system',
                    'priority': 'high',
                    'target_zone': 'system',
                    'estimated_impact': 'critical for situational awareness'
                }
            ],
            'key_metrics': {
                'total_crowd_estimate': 'error',
                'incident_count': 'error',
                'medical_cases': 'error',
                'security_incidents': 'error'
            },
            'next_actions': ['Resolve system error', 'Manual report review'],
            'confidence_assessment': {
                'data_quality': 'low',
                'information_completeness': 'error',
                'reliability_score': 0.0
            },
            'error': True,
            'error_message': error_message,
            'analysis_metadata': {
                'analysis_timestamp': datetime.now().isoformat(),
                'agent_type': 'report_agent',
                'analysis_version': '1.0',
                'error_occurred': True
            }
        }
    
    def get_zone_status_summary(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract a simplified zone status summary from full analysis
        
        Args:
            analysis_result: Full reports analysis result
            
        Returns:
            List of zone status summaries
        """
        if analysis_result.get('error'):
            return [{'zone': 'Error', 'status': 'System Error', 'issues': ['Analysis failed']}]
        
        zone_summaries = analysis_result.get('zone_summaries', [])
        
        simplified_summaries = []
        for zone in zone_summaries:
            summary = {
                'zone': zone.get('zone_name', 'Unknown'),
                'status': zone.get('status', 'Unknown'),
                'crowd_density': zone.get('crowd_density', 'unknown'),
                'crowd_estimate': zone.get('crowd_estimate', 'unknown'),
                'key_issues': zone.get('key_issues', []),
                'security_alerts': zone.get('security_alerts', [])
            }
            simplified_summaries.append(summary)
        
        return simplified_summaries


if __name__ == "__main__":
    # Test the Report Agent
    print("Testing Report Agent...")
    
    # This would require actual API key to test
    # agent = ReportAgent()
    
    print("Report Agent structure validated successfully")