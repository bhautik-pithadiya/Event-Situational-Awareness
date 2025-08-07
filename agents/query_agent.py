"""
Query Agent for handling user questions using contextual knowledge from vision and report analyses
"""
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from config import config


class QueryAgent:
    """Agent responsible for answering user questions using situational awareness context"""
    
    def __init__(self):
        """Initialize the Query Agent with Gemini configuration"""
        try:
            genai.configure(api_key=config.GOOGLE_API_KEY)
            self.text_model = genai.GenerativeModel(config.TEXT_MODEL)
            self.context_data = {}  # Store context for query answering
            print("Query Agent initialized successfully")
        except Exception as e:
            print(f"Error initializing Query Agent: {str(e)}")
            self.text_model = None
    
    def update_context(self, vision_analyses: List[Dict[str, Any]] = None,
                      report_analysis: Dict[str, Any] = None,
                      fusion_summary: Dict[str, Any] = None):
        """
        Update the contextual knowledge base for query answering
        
        Args:
            vision_analyses: Latest vision analysis results
            report_analysis: Latest report analysis results
            fusion_summary: Latest fusion summary
        """
        self.context_data = {
            'vision_analyses': vision_analyses or [],
            'report_analysis': report_analysis or {},
            'fusion_summary': fusion_summary or {},
            'last_update': datetime.now().isoformat()
        }
        
        print(f"Query Agent context updated with {len(vision_analyses or [])} vision analyses")
    
    def answer_query(self, user_question: str) -> Dict[str, Any]:
        """
        Answer a user question using available context
        
        Args:
            user_question: User's question about the event situation
            
        Returns:
            Dictionary with answer and supporting information
        """
        if not self.text_model:
            return self._create_error_response("Query model not initialized")
        
        if not self.context_data:
            return self._create_error_response("No contextual data available. Please wait for system to process current situation.")
        
        try:
            # Generate answer using Gemini with context
            answer_result = self._generate_contextual_answer(user_question)
            
            return answer_result
            
        except Exception as e:
            print(f"Error answering query: {str(e)}")
            return self._create_error_response(f"Query processing failed: {str(e)}")
    
    def _generate_contextual_answer(self, user_question: str) -> Dict[str, Any]:
        """
        Generate answer using Gemini API with contextual knowledge
        
        Args:
            user_question: User's question
            
        Returns:
            Answer result dictionary
        """
        try:
            # Prepare context summary for the query
            context_summary = self._prepare_context_summary()
            
            # Create query prompt
            prompt = self._create_query_prompt(user_question)
            
            # Combine prompt with context
            full_prompt = f"{prompt}\n\nCONTEXT INFORMATION:\n{context_summary}\n\nUSER QUESTION: {user_question}"
            
            # Generate answer
            response = self.text_model.generate_content(full_prompt)
            
            # Parse and structure the response
            answer_result = self._parse_query_response(response.text, user_question)
            
            return answer_result
            
        except Exception as e:
            print(f"Error in contextual answer generation: {str(e)}")
            return self._create_error_response(f"Answer generation failed: {str(e)}")
    
    def _prepare_context_summary(self) -> str:
        """
        Prepare a concise summary of available context for query answering
        
        Returns:
            Context summary string
        """
        context_parts = []
        
        # Add fusion summary if available
        fusion_summary = self.context_data.get('fusion_summary', {})
        if fusion_summary and not fusion_summary.get('error'):
            context_parts.append("=== CURRENT SITUATION SUMMARY ===")
            
            exec_summary = fusion_summary.get('executive_summary', {})
            context_parts.append(f"Overall Situation: {exec_summary.get('overall_situation', 'Unknown')}")
            context_parts.append(f"Threat Level: {exec_summary.get('threat_level', 'Unknown')}")
            
            immediate_concerns = exec_summary.get('immediate_concerns', [])
            if immediate_concerns:
                context_parts.append(f"Immediate Concerns: {', '.join(immediate_concerns)}")
            
            # Add zone analysis
            zone_analyses = fusion_summary.get('zone_analysis', [])
            if zone_analyses:
                context_parts.append("\n=== ZONE STATUS ===")
                for zone in zone_analyses:
                    zone_name = zone.get('zone_name', 'Unknown')
                    status = zone.get('status_assessment', 'Unknown')
                    context_parts.append(f"{zone_name}: {status}")
                    
                    crowd_situation = zone.get('crowd_situation', {})
                    if crowd_situation:
                        density = crowd_situation.get('density_level', 'unknown')
                        behavior = crowd_situation.get('crowd_behavior', 'unknown')
                        context_parts.append(f"  Crowd: {density} density, {behavior} behavior")
        
        # Add report analysis if fusion summary not available
        elif self.context_data.get('report_analysis') and not self.context_data['report_analysis'].get('error'):
            report_analysis = self.context_data['report_analysis']
            context_parts.append("=== FIELD REPORT SUMMARY ===")
            
            event_overview = report_analysis.get('event_overview', {})
            context_parts.append(f"Event Status: {event_overview.get('overall_status', 'Unknown')}")
            
            # Add priority issues
            priority_issues = report_analysis.get('priority_issues', [])
            if priority_issues:
                context_parts.append("\nPriority Issues:")
                for issue in priority_issues[:3]:  # Top 3 issues
                    context_parts.append(f"- {issue.get('issue', 'Unknown')} (Zone: {issue.get('zone', 'Unknown')})")
        
        # Add vision analysis summary if other sources not available
        elif self.context_data.get('vision_analyses'):
            vision_analyses = self.context_data['vision_analyses']
            context_parts.append("=== VIDEO ANALYSIS SUMMARY ===")
            
            # Group by zone
            zone_data = {}
            for analysis in vision_analyses:
                if analysis.get('error'):
                    continue
                zone = analysis.get('zone', 'Unknown')
                if zone not in zone_data:
                    zone_data[zone] = {'densities': [], 'risks': []}
                zone_data[zone]['densities'].append(analysis.get('crowd_density', 'unknown'))
                zone_data[zone]['risks'].extend(analysis.get('potential_risks', []))
            
            for zone, data in zone_data.items():
                density_counts = {}
                for density in data['densities']:
                    density_counts[density] = density_counts.get(density, 0) + 1
                most_common = max(density_counts.items(), key=lambda x: x[1])[0] if density_counts else 'unknown'
                context_parts.append(f"{zone}: {most_common} crowd density")
                
                unique_risks = list(set(data['risks']))
                if unique_risks:
                    context_parts.append(f"  Risks: {', '.join(unique_risks[:3])}")
        
        # Add timestamp
        last_update = self.context_data.get('last_update', 'Unknown')
        context_parts.append(f"\n=== DATA TIMESTAMP ===")
        context_parts.append(f"Last Updated: {last_update}")
        
        return '\n'.join(context_parts) if context_parts else "No contextual information available."
    
    def _create_query_prompt(self, user_question: str) -> str:
        """
        Create a prompt for query answering
        
        Args:
            user_question: User's question
            
        Returns:
            Query prompt string
        """
        prompt = f"""
You are an expert situational awareness analyst answering questions about a current event situation.

Based on the provided context information, please answer the user's question with the following structured response in JSON format:

{{
    "answer": "direct answer to the user's question",
    "confidence": 0.0-1.0,
    "supporting_evidence": [
        "specific data points that support this answer"
    ],
    "data_sources": [
        "which data sources were used (vision analysis, field reports, etc.)"
    ],
    "additional_context": "relevant background information",
    "limitations": [
        "any limitations or uncertainties in the answer"
    ],
    "related_information": [
        "other relevant information the user might find useful"
    ],
    "recommendations": [
        "any actionable recommendations based on the question"
    ],
    "follow_up_questions": [
        "suggested follow-up questions the user might ask"
    ]
}}

Guidelines for answering:
1. Be specific and cite relevant data from the context
2. If information is not available, clearly state this
3. Provide confidence level based on data quality and completeness
4. Include relevant warnings or caveats
5. Suggest actionable next steps when appropriate
6. If the question cannot be answered with available data, explain what additional information would be needed

Question types you should be able to handle:
- Zone-specific questions (e.g., "What's the situation in Zone A?")
- Crowd-related questions (e.g., "How crowded is the event?")
- Safety and security questions (e.g., "Are there any safety concerns?")
- Resource questions (e.g., "Do we need more security personnel?")
- Trend questions (e.g., "Is the situation getting better or worse?")
- Comparison questions (e.g., "Which zone has the highest crowd density?")
- Prediction questions (e.g., "What should we expect in the next hour?")

Remember to base your answer only on the provided context information and be honest about limitations.
"""
        return prompt
    
    def _parse_query_response(self, response_text: str, user_question: str) -> Dict[str, Any]:
        """
        Parse Gemini API response for query answering
        
        Args:
            response_text: Raw response from Gemini
            user_question: Original user question
            
        Returns:
            Structured query response
        """
        try:
            # Try to extract JSON from the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                answer_data = json.loads(json_str)
            else:
                # If no JSON found, create structured response from text
                answer_data = self._create_fallback_answer(response_text, user_question)
            
            # Add metadata
            answer_data['query_metadata'] = {
                'question': user_question,
                'response_timestamp': datetime.now().isoformat(),
                'agent_type': 'query_agent',
                'context_available': bool(self.context_data),
                'context_timestamp': self.context_data.get('last_update', 'unknown')
            }
            
            # Validate the answer structure
            answer_data = self._validate_query_response(answer_data)
            
            return answer_data
            
        except json.JSONDecodeError as e:
            print(f"Error parsing query JSON response: {str(e)}")
            return self._create_fallback_answer(response_text, user_question)
        except Exception as e:
            print(f"Error processing query response: {str(e)}")
            return self._create_error_response(f"Query response processing failed: {str(e)}")
    
    def _create_fallback_answer(self, response_text: str, user_question: str) -> Dict[str, Any]:
        """
        Create a fallback answer when JSON parsing fails
        
        Args:
            response_text: Raw response text
            user_question: Original question
            
        Returns:
            Basic answer structure
        """
        return {
            'answer': f"I have information about your question, but there was an issue formatting the response. Here's what I found: {response_text[:500]}{'...' if len(response_text) > 500 else ''}",
            'confidence': 0.5,
            'supporting_evidence': ['Response formatting error occurred'],
            'data_sources': ['System analysis'],
            'additional_context': 'The system had difficulty formatting the response properly.',
            'limitations': ['Response parsing incomplete', 'Manual review of raw response may be needed'],
            'related_information': [],
            'recommendations': ['Contact system administrator if this continues'],
            'follow_up_questions': ['Could you rephrase your question?'],
            'raw_response': response_text,
            'parsing_error': True
        }
    
    def _validate_query_response(self, answer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and ensure required fields are present in query response
        
        Args:
            answer_data: Answer result dictionary
            
        Returns:
            Validated answer result
        """
        # Ensure required fields exist
        required_fields = {
            'answer': 'Information not available',
            'confidence': 0.5,
            'supporting_evidence': [],
            'data_sources': [],
            'additional_context': '',
            'limitations': [],
            'related_information': [],
            'recommendations': [],
            'follow_up_questions': []
        }
        
        for field, default_value in required_fields.items():
            if field not in answer_data:
                answer_data[field] = default_value
        
        # Ensure lists are actually lists
        list_fields = ['supporting_evidence', 'data_sources', 'limitations', 
                      'related_information', 'recommendations', 'follow_up_questions']
        for field in list_fields:
            if not isinstance(answer_data[field], list):
                answer_data[field] = [str(answer_data[field])] if answer_data[field] else []
        
        # Ensure confidence is a float between 0 and 1
        try:
            answer_data['confidence'] = max(0.0, min(1.0, float(answer_data['confidence'])))
        except (ValueError, TypeError):
            answer_data['confidence'] = 0.5
        
        return answer_data
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Create an error response structure for query answering
        
        Args:
            error_message: Error description
            
        Returns:
            Error response dictionary
        """
        return {
            'answer': 'I apologize, but I am unable to process your question at the moment due to a system error.',
            'confidence': 0.0,
            'supporting_evidence': [],
            'data_sources': [],
            'additional_context': 'The query system is experiencing technical difficulties.',
            'limitations': ['System error preventing analysis'],
            'related_information': [],
            'recommendations': ['Please try again later or contact system administrator'],
            'follow_up_questions': [],
            'error': True,
            'error_message': error_message,
            'query_metadata': {
                'response_timestamp': datetime.now().isoformat(),
                'agent_type': 'query_agent',
                'error_occurred': True
            }
        }
    
    def get_suggested_questions(self) -> List[str]:
        """
        Get a list of suggested questions based on available context
        
        Returns:
            List of suggested question strings
        """
        suggestions = []
        
        if not self.context_data:
            return [
                "What is the current overall situation?",
                "Are there any safety concerns?",
                "What should I know about the event status?"
            ]
        
        # Base suggestions
        suggestions.extend([
            "What is the overall situation assessment?",
            "Which zones need immediate attention?",
            "Are there any critical safety issues?",
            "What are the current crowd density levels?",
            "What resources are needed most urgently?"
        ])
        
        # Add zone-specific suggestions if we have zone data
        fusion_summary = self.context_data.get('fusion_summary', {})
        if fusion_summary and not fusion_summary.get('error'):
            zone_analyses = fusion_summary.get('zone_analysis', [])
            if zone_analyses:
                for zone in zone_analyses[:3]:  # Top 3 zones
                    zone_name = zone.get('zone_name', 'Unknown')
                    suggestions.append(f"What's the situation in {zone_name}?")
        
        # Add suggestions based on vision analysis
        vision_analyses = self.context_data.get('vision_analyses', [])
        if vision_analyses:
            zones = list(set([a.get('zone', 'Unknown') for a in vision_analyses if not a.get('error')]))
            for zone in zones[:2]:  # Top 2 zones
                suggestions.append(f"How crowded is {zone}?")
        
        # Add suggestions based on report analysis
        report_analysis = self.context_data.get('report_analysis', {})
        if report_analysis and not report_analysis.get('error'):
            priority_issues = report_analysis.get('priority_issues', [])
            if priority_issues:
                suggestions.append("What are the most urgent issues right now?")
                suggestions.append("Which areas need additional resources?")
        
        return suggestions[:8]  # Return max 8 suggestions
    
    def clear_context(self):
        """Clear the current context data"""
        self.context_data = {}
        print("Query Agent context cleared")


if __name__ == "__main__":
    # Test the Query Agent
    print("Testing Query Agent...")
    
    # This would require actual API key and context to test
    # agent = QueryAgent()
    
    print("Query Agent structure validated successfully")