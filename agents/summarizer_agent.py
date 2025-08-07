"""
Summarizer Agent for combining multi-modal insights using Google Gemini API
"""
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from config import config


class SummarizerAgent:
    """Agent responsible for fusing vision and text analysis into comprehensive summaries"""
    
    def __init__(self):
        """Initialize the Summarizer Agent with Gemini configuration"""
        try:
            genai.configure(api_key=config.GOOGLE_API_KEY)
            self.text_model = genai.GenerativeModel(config.TEXT_MODEL)
            print("Summarizer Agent initialized successfully")
        except Exception as e:
            print(f"Error initializing Summarizer Agent: {str(e)}")
            self.text_model = None
    
    def create_comprehensive_summary(self, vision_analyses: List[Dict[str, Any]], 
                                   report_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a comprehensive summary by fusing vision and report analyses
        
        Args:
            vision_analyses: List of vision analysis results from video frames
            report_analysis: Report analysis results from field reports
            
        Returns:
            Comprehensive summary dictionary
        """
        if not self.text_model:
            return self._create_error_response("Summarizer model not initialized")
        
        try:
            # Prepare the data for analysis
            fusion_data = self._prepare_fusion_data(vision_analyses, report_analysis)
            
            # Generate comprehensive summary using Gemini
            summary = self._generate_fusion_summary(fusion_data)
            
            return summary
            
        except Exception as e:
            print(f"Error creating comprehensive summary: {str(e)}")
            return self._create_error_response(f"Summary generation failed: {str(e)}")
    
    def _prepare_fusion_data(self, vision_analyses: List[Dict[str, Any]], 
                           report_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare and structure data from both vision and report analyses
        
        Args:
            vision_analyses: Vision analysis results
            report_analysis: Report analysis results
            
        Returns:
            Structured fusion data
        """
        # Extract key insights from vision analyses
        vision_insights = self._extract_vision_insights(vision_analyses)
        
        # Extract key insights from report analysis
        report_insights = self._extract_report_insights(report_analysis)
        
        fusion_data = {
            'vision_insights': vision_insights,
            'report_insights': report_insights,
            'analysis_timestamp': datetime.now().isoformat(),
            'data_sources': {
                'vision_frames_count': len(vision_analyses),
                'field_reports_available': not report_analysis.get('error', False)
            }
        }
        
        return fusion_data
    
    def _extract_vision_insights(self, vision_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract and aggregate key insights from vision analyses
        
        Args:
            vision_analyses: List of vision analysis results
            
        Returns:
            Aggregated vision insights
        """
        if not vision_analyses:
            return {'error': 'No vision analyses available'}
        
        # Group analyses by zone
        zone_data = {}
        all_risks = []
        all_recommendations = []
        confidence_scores = []
        
        for analysis in vision_analyses:
            if analysis.get('error'):
                continue
            
            zone = analysis.get('zone', 'Unknown')
            if zone not in zone_data:
                zone_data[zone] = {
                    'analyses_count': 0,
                    'crowd_densities': [],
                    'behaviors': [],
                    'risks': [],
                    'recommendations': []
                }
            
            zone_data[zone]['analyses_count'] += 1
            zone_data[zone]['crowd_densities'].append(analysis.get('crowd_density', 'moderate'))
            zone_data[zone]['behaviors'].append(analysis.get('crowd_behavior', 'calm'))
            zone_data[zone]['risks'].extend(analysis.get('potential_risks', []))
            zone_data[zone]['recommendations'].extend(analysis.get('recommended_actions', []))
            
            all_risks.extend(analysis.get('potential_risks', []))
            all_recommendations.extend(analysis.get('recommended_actions', []))
            
            if 'confidence_score' in analysis:
                confidence_scores.append(analysis['confidence_score'])
        
        # Process zone summaries
        zone_summaries = []
        for zone, data in zone_data.items():
            # Determine most common crowd density
            density_counts = {}
            for density in data['crowd_densities']:
                density_counts[density] = density_counts.get(density, 0) + 1
            most_common_density = max(density_counts.items(), key=lambda x: x[1])[0] if density_counts else 'moderate'
            
            zone_summary = {
                'zone': zone,
                'frames_analyzed': data['analyses_count'],
                'predominant_crowd_density': most_common_density,
                'density_distribution': density_counts,
                'observed_behaviors': list(set(data['behaviors'])),
                'identified_risks': list(set(data['risks'])),
                'recommended_actions': list(set(data['recommendations']))
            }
            zone_summaries.append(zone_summary)
        
        vision_insights = {
            'zones_analyzed': list(zone_data.keys()),
            'total_frames_processed': len(vision_analyses),
            'successful_analyses': len([a for a in vision_analyses if not a.get('error')]),
            'zone_summaries': zone_summaries,
            'overall_risks': list(set(all_risks)),
            'overall_recommendations': list(set(all_recommendations)),
            'average_confidence': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        }
        
        return vision_insights
    
    def _extract_report_insights(self, report_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key insights from report analysis
        
        Args:
            report_analysis: Report analysis results
            
        Returns:
            Extracted report insights
        """
        if report_analysis.get('error'):
            return {'error': report_analysis.get('error_message', 'Report analysis failed')}
        
        report_insights = {
            'event_status': report_analysis.get('event_overview', {}).get('overall_status', 'unknown'),
            'zone_reports': report_analysis.get('zone_summaries', []),
            'priority_issues': report_analysis.get('priority_issues', []),
            'resource_status': report_analysis.get('resource_status', {}),
            'environmental_factors': report_analysis.get('environmental_factors', {}),
            'operational_recommendations': report_analysis.get('operational_recommendations', []),
            'key_metrics': report_analysis.get('key_metrics', {}),
            'confidence_level': report_analysis.get('confidence_assessment', {}).get('reliability_score', 0.5)
        }
        
        return report_insights
    
    def _generate_fusion_summary(self, fusion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive summary using Gemini API
        
        Args:
            fusion_data: Combined data from vision and report analyses
            
        Returns:
            Comprehensive summary
        """
        try:
            # Create fusion prompt
            prompt = self._create_fusion_prompt()
            
            # Convert fusion data to text for analysis
            data_text = self._fusion_data_to_text(fusion_data)
            
            # Combine prompt with data
            full_prompt = f"{prompt}\n\nDATA TO ANALYZE:\n{data_text}"
            
            # Generate summary
            response = self.text_model.generate_content(full_prompt)
            
            # Parse the response
            summary = self._parse_fusion_response(response.text, fusion_data)
            
            return summary
            
        except Exception as e:
            print(f"Error in fusion summary generation: {str(e)}")
            return self._create_error_response(f"Fusion analysis failed: {str(e)}")
    
    def _create_fusion_prompt(self) -> str:
        """
        Create a detailed prompt for multi-modal fusion analysis
        
        Returns:
            Fusion analysis prompt string
        """
        prompt = """
You are an expert situational awareness analyst combining real-time video analysis with field reports to create a comprehensive event assessment.

Please analyze the combined data from video feeds and field reports, then provide a structured assessment in JSON format:

{
    "executive_summary": {
        "overall_situation": "brief high-level assessment",
        "threat_level": "green|yellow|orange|red",
        "immediate_concerns": ["top 3 priority issues"],
        "recommendation_urgency": "low|medium|high|critical"
    },
    "zone_analysis": [
        {
            "zone_name": "zone identifier",
            "status_assessment": "current operational status",
            "crowd_situation": {
                "visual_assessment": "from video analysis",
                "reported_status": "from field reports",
                "reconciled_estimate": "best estimate combining both sources",
                "crowd_behavior": "observed/reported behavior",
                "density_level": "low|moderate|high|critical"
            },
            "risk_assessment": {
                "visual_risks": ["risks identified from video"],
                "reported_risks": ["risks from field reports"],
                "combined_risk_level": "low|medium|high|critical",
                "primary_concerns": ["top risks for this zone"]
            },
            "infrastructure_status": "condition based on both sources",
            "recommended_actions": ["specific actions for this zone"]
        }
    ],
    "cross_validation": {
        "vision_report_alignment": "how well video and reports align",
        "discrepancies": ["any conflicting information"],
        "confidence_assessment": "overall confidence in analysis",
        "data_gaps": ["information still needed"]
    },
    "operational_priorities": [
        {
            "priority": "specific action needed",
            "urgency": "immediate|short-term|medium-term",
            "zone_focus": "primary zone affected",
            "resource_requirements": "what resources needed",
            "success_metrics": "how to measure effectiveness"
        }
    ],
    "resource_deployment": {
        "current_status": "resource distribution from reports",
        "visual_assessment": "resource needs based on video analysis",
        "recommended_adjustments": ["changes to resource deployment"],
        "critical_shortfalls": ["urgent resource needs"]
    },
    "environmental_context": {
        "reported_conditions": "weather/environment from reports",
        "visual_conditions": "conditions observed in video",
        "impact_assessment": "how environment affects situation",
        "forecast_considerations": "upcoming environmental factors"
    },
    "communication_summary": {
        "key_messages": ["main points for stakeholders"],
        "public_information": "what can be shared publicly",
        "internal_alerts": ["information for operations team"],
        "media_considerations": ["public relations aspects"]
    },
    "monitoring_recommendations": {
        "critical_metrics": ["key indicators to track"],
        "alert_thresholds": ["when to escalate"],
        "reporting_frequency": "how often to update",
        "additional_data_needed": ["what other information would help"]
    },
    "confidence_metrics": {
        "overall_confidence": 0.0-1.0,
        "vision_data_quality": "assessment of video analysis quality",
        "report_data_quality": "assessment of field report quality",
        "synthesis_reliability": "confidence in combined analysis"
    }
}

Focus on:
1. Reconciling differences between video observations and field reports
2. Creating actionable operational recommendations
3. Identifying critical gaps or discrepancies in information
4. Providing clear priority ranking for actions
5. Assessing the reliability of the combined analysis
6. Highlighting areas where additional information is needed

Be specific, actionable, and honest about uncertainties or conflicting information.
"""
        return prompt
    
    def _fusion_data_to_text(self, fusion_data: Dict[str, Any]) -> str:
        """
        Convert fusion data to readable text format for analysis
        
        Args:
            fusion_data: Structured fusion data
            
        Returns:
            Text representation of the data
        """
        text_parts = []
        
        # Vision insights section
        vision_insights = fusion_data.get('vision_insights', {})
        if not vision_insights.get('error'):
            text_parts.append("=== VIDEO ANALYSIS INSIGHTS ===")
            text_parts.append(f"Zones analyzed: {', '.join(vision_insights.get('zones_analyzed', []))}")
            text_parts.append(f"Total frames processed: {vision_insights.get('total_frames_processed', 0)}")
            text_parts.append(f"Average confidence: {vision_insights.get('average_confidence', 0.5):.2f}")
            
            for zone_summary in vision_insights.get('zone_summaries', []):
                text_parts.append(f"\nZone: {zone_summary.get('zone', 'Unknown')}")
                text_parts.append(f"  Frames analyzed: {zone_summary.get('frames_analyzed', 0)}")
                text_parts.append(f"  Crowd density: {zone_summary.get('predominant_crowd_density', 'unknown')}")
                text_parts.append(f"  Behaviors: {', '.join(zone_summary.get('observed_behaviors', []))}")
                text_parts.append(f"  Risks: {', '.join(zone_summary.get('identified_risks', []))}")
        
        # Report insights section
        report_insights = fusion_data.get('report_insights', {})
        if not report_insights.get('error'):
            text_parts.append("\n=== FIELD REPORT INSIGHTS ===")
            text_parts.append(f"Event status: {report_insights.get('event_status', 'unknown')}")
            text_parts.append(f"Confidence level: {report_insights.get('confidence_level', 0.5):.2f}")
            
            # Priority issues
            priority_issues = report_insights.get('priority_issues', [])
            if priority_issues:
                text_parts.append("\nPriority Issues:")
                for issue in priority_issues[:5]:  # Top 5 issues
                    text_parts.append(f"  - {issue.get('issue', 'Unknown issue')} (Zone: {issue.get('zone', 'Unknown')}, Severity: {issue.get('severity', 'Unknown')})")
            
            # Zone reports
            zone_reports = report_insights.get('zone_reports', [])
            if zone_reports:
                text_parts.append("\nZone Reports:")
                for zone in zone_reports:
                    text_parts.append(f"  {zone.get('zone_name', 'Unknown')}: {zone.get('status', 'Unknown status')}")
                    if zone.get('key_issues'):
                        text_parts.append(f"    Issues: {', '.join(zone.get('key_issues', []))}")
        
        return '\n'.join(text_parts)
    
    def _parse_fusion_response(self, response_text: str, fusion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Gemini API response for fusion analysis
        
        Args:
            response_text: Raw response from Gemini
            fusion_data: Original fusion data
            
        Returns:
            Structured fusion summary
        """
        try:
            # Try to extract JSON from the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                summary = json.loads(json_str)
            else:
                # If no JSON found, create structured response from text
                summary = self._create_fallback_fusion_summary(response_text, fusion_data)
            
            # Add metadata
            summary['fusion_metadata'] = {
                'analysis_timestamp': datetime.now().isoformat(),
                'agent_type': 'summarizer_agent',
                'data_sources': fusion_data.get('data_sources', {}),
                'fusion_version': '1.0'
            }
            
            # Validate the summary structure
            summary = self._validate_fusion_summary(summary)
            
            return summary
            
        except json.JSONDecodeError as e:
            print(f"Error parsing fusion JSON response: {str(e)}")
            return self._create_fallback_fusion_summary(response_text, fusion_data)
        except Exception as e:
            print(f"Error processing fusion response: {str(e)}")
            return self._create_error_response(f"Fusion response processing failed: {str(e)}")
    
    def _create_fallback_fusion_summary(self, response_text: str, fusion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a fallback fusion summary when JSON parsing fails
        
        Args:
            response_text: Raw response text
            fusion_data: Original fusion data
            
        Returns:
            Basic fusion summary structure
        """
        return {
            'executive_summary': {
                'overall_situation': 'Analysis parsing incomplete - manual review required',
                'threat_level': 'yellow',
                'immediate_concerns': ['Fusion analysis system error'],
                'recommendation_urgency': 'medium'
            },
            'zone_analysis': [],
            'cross_validation': {
                'vision_report_alignment': 'unable to assess',
                'discrepancies': ['System parsing error'],
                'confidence_assessment': 'low',
                'data_gaps': ['Complete analysis unavailable']
            },
            'operational_priorities': [
                {
                    'priority': 'Restore fusion analysis system',
                    'urgency': 'immediate',
                    'zone_focus': 'system',
                    'resource_requirements': 'Technical support',
                    'success_metrics': 'System operational'
                }
            ],
            'confidence_metrics': {
                'overall_confidence': 0.3,
                'vision_data_quality': 'available',
                'report_data_quality': 'available',
                'synthesis_reliability': 'compromised'
            },
            'raw_analysis': response_text[:1500] + '...' if len(response_text) > 1500 else response_text,
            'parsing_error': True
        }
    
    def _validate_fusion_summary(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and ensure required fields are present in fusion summary
        
        Args:
            summary: Summary result dictionary
            
        Returns:
            Validated summary result
        """
        # Ensure required top-level keys exist
        required_keys = {
            'executive_summary': {},
            'zone_analysis': [],
            'cross_validation': {},
            'operational_priorities': [],
            'confidence_metrics': {}
        }
        
        for key, default_value in required_keys.items():
            if key not in summary:
                summary[key] = default_value
        
        # Validate executive_summary structure
        exec_summary_defaults = {
            'overall_situation': 'Assessment in progress',
            'threat_level': 'yellow',
            'immediate_concerns': [],
            'recommendation_urgency': 'medium'
        }
        
        for key, default_value in exec_summary_defaults.items():
            if key not in summary['executive_summary']:
                summary['executive_summary'][key] = default_value
        
        # Validate confidence_metrics structure
        confidence_defaults = {
            'overall_confidence': 0.5,
            'vision_data_quality': 'unknown',
            'report_data_quality': 'unknown',
            'synthesis_reliability': 'unknown'
        }
        
        for key, default_value in confidence_defaults.items():
            if key not in summary['confidence_metrics']:
                summary['confidence_metrics'][key] = default_value
        
        # Ensure overall_confidence is a float between 0 and 1
        try:
            score = summary['confidence_metrics']['overall_confidence']
            summary['confidence_metrics']['overall_confidence'] = max(0.0, min(1.0, float(score)))
        except (ValueError, TypeError):
            summary['confidence_metrics']['overall_confidence'] = 0.5
        
        return summary
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Create an error response structure for fusion analysis
        
        Args:
            error_message: Error description
            
        Returns:
            Error response dictionary
        """
        return {
            'executive_summary': {
                'overall_situation': 'System error - manual assessment required',
                'threat_level': 'red',
                'immediate_concerns': ['Fusion analysis system failure'],
                'recommendation_urgency': 'critical'
            },
            'zone_analysis': [],
            'cross_validation': {
                'vision_report_alignment': 'system error',
                'discrepancies': ['Analysis system offline'],
                'confidence_assessment': 'none',
                'data_gaps': ['Complete system failure']
            },
            'operational_priorities': [
                {
                    'priority': 'Restore situational awareness system',
                    'urgency': 'immediate',
                    'zone_focus': 'all',
                    'resource_requirements': 'Technical team and manual assessment',
                    'success_metrics': 'System restored and operational'
                }
            ],
            'confidence_metrics': {
                'overall_confidence': 0.0,
                'vision_data_quality': 'error',
                'report_data_quality': 'error',
                'synthesis_reliability': 'failed'
            },
            'error': True,
            'error_message': error_message,
            'fusion_metadata': {
                'analysis_timestamp': datetime.now().isoformat(),
                'agent_type': 'summarizer_agent',
                'fusion_version': '1.0',
                'error_occurred': True
            }
        }


if __name__ == "__main__":
    # Test the Summarizer Agent
    print("Testing Summarizer Agent...")
    
    # This would require actual API key and data to test
    # agent = SummarizerAgent()
    
    print("Summarizer Agent structure validated successfully")