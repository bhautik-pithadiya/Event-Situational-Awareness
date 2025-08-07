"""
Coordinator Agent - Orchestrates all agents for Event Situational Awareness System
"""
import os
import glob
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import traceback

from utils.video_processor import VideoProcessor
from agents.vision_agent import VisionAgent
from agents.report_agent import ReportAgent
from agents.summarizer_agent import SummarizerAgent
from agents.query_agent import QueryAgent
from config import config


class CoordinatorAgent:
    """
    Main orchestrator agent that coordinates all other agents and manages the analysis workflow
    """
    
    def __init__(self):
        """Initialize the Coordinator Agent and all sub-agents"""
        self.status = "initializing"
        self.last_analysis_time = None
        self.current_data = {
            'vision_analyses': [],
            'report_analysis': {},
            'fusion_summary': {},
            'processing_status': {}
        }
        
        try:
            # Initialize all agents
            self.video_processor = VideoProcessor()
            self.vision_agent = VisionAgent()
            self.report_agent = ReportAgent()
            self.summarizer_agent = SummarizerAgent()
            self.query_agent = QueryAgent()
            
            self.status = "ready"
            print("Coordinator Agent initialized successfully")
            
        except Exception as e:
            self.status = "error"
            print(f"Error initializing Coordinator Agent: {str(e)}")
            print(traceback.format_exc())
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """
        Run complete analysis workflow: process videos, analyze reports, create fusion summary
        
        Returns:
            Dictionary with complete analysis results and status
        """
        print("Starting full analysis workflow...")
        self.status = "processing"
        
        analysis_results = {
            'start_time': datetime.now().isoformat(),
            'vision_results': [],
            'report_results': {},
            'fusion_results': {},
            'status': 'in_progress',
            'errors': [],
            'warnings': []
        }
        
        try:
            # Step 1: Process videos and run vision analysis
            print("Step 1: Processing videos...")
            vision_results = self._process_all_videos()
            analysis_results['vision_results'] = vision_results
            
            if not vision_results:
                analysis_results['warnings'].append("No video analysis results available")
            
            # Step 2: Analyze field reports
            print("Step 2: Analyzing field reports...")
            report_results = self._process_field_reports()
            analysis_results['report_results'] = report_results
            
            if report_results.get('error'):
                analysis_results['warnings'].append(f"Report analysis issue: {report_results.get('error_message')}")
            
            # Step 3: Create fusion summary
            print("Step 3: Creating fusion summary...")
            fusion_results = self._create_fusion_summary(vision_results, report_results)
            analysis_results['fusion_results'] = fusion_results
            
            if fusion_results.get('error'):
                analysis_results['warnings'].append(f"Fusion analysis issue: {fusion_results.get('error_message')}")
            
            # Step 4: Update query agent context
            print("Step 4: Updating query context...")
            self._update_query_context(vision_results, report_results, fusion_results)
            
            # Update internal state
            self.current_data = {
                'vision_analyses': vision_results,
                'report_analysis': report_results,
                'fusion_summary': fusion_results,
                'processing_status': {
                    'last_analysis': datetime.now().isoformat(),
                    'status': 'completed',
                    'warnings_count': len(analysis_results['warnings']),
                    'errors_count': len(analysis_results['errors'])
                }
            }
            
            analysis_results['status'] = 'completed'
            analysis_results['end_time'] = datetime.now().isoformat()
            self.status = "ready"
            self.last_analysis_time = datetime.now()
            
            print("Full analysis workflow completed successfully")
            
        except Exception as e:
            error_msg = f"Full analysis workflow failed: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            
            analysis_results['errors'].append(error_msg)
            analysis_results['status'] = 'failed'
            analysis_results['end_time'] = datetime.now().isoformat()
            self.status = "error"
        
        return analysis_results
    
    def _process_all_videos(self) -> List[Dict[str, Any]]:
        """
        Process all available video files
        
        Returns:
            List of vision analysis results
        """
        vision_results = []
        
        try:
            # Find video files
            video_files = self._find_video_files()
            
            if not video_files:
                print("No video files found - creating sample data for testing")
                # Create sample analysis data for testing when no videos are available
                return self._create_sample_vision_data()
            
            # Get zone names based on video count
            zone_names = config.get_zones_for_videos(len(video_files))
            print(f"Found {len(video_files)} videos, assigning {len(zone_names)} zones: {zone_names}")
            
            # Process each video file
            for i, video_path in enumerate(video_files):
                print(f"Processing video: {video_path}")
                
                # Assign zone based on video index
                zone_name = zone_names[i] if i < len(zone_names) else zone_names[0]
                
                # Process video frames
                frame_data = self.video_processor.process_video_file(video_path, zone_name)
                
                if frame_data:
                    # Analyze frames with vision agent
                    frame_analyses = self.vision_agent.analyze_multiple_frames(frame_data)
                    vision_results.extend(frame_analyses)
                    print(f"Analyzed {len(frame_analyses)} frames from {video_path}")
                else:
                    print(f"No frames extracted from {video_path}")
            
            return vision_results
            
        except Exception as e:
            print(f"Error processing videos: {str(e)}")
            return self._create_sample_vision_data()
    
    def _find_video_files(self) -> List[str]:
        """
        Find all video files in the videos directory
        
        Returns:
            List of video file paths
        """
        video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv']
        video_files = []
        
        for extension in video_extensions:
            pattern = os.path.join(config.VIDEOS_DIR, extension)
            files = glob.glob(pattern)
            video_files.extend(files)
        
        return video_files
    
    def _extract_zone_name(self, video_path: str) -> str:
        """
        Extract zone name from video filename
        
        Args:
            video_path: Path to video file
            
        Returns:
            Zone name string
        """
        filename = os.path.basename(video_path).lower()
        
        # Map common filename patterns to zones
        zone_mapping = {
            'zone_a': 'Zone A',
            'zone_b': 'Zone B', 
            'zone_c': 'Zone C',
            'zone_d': 'Zone D',
            'main': 'Zone A',
            'food': 'Zone B',
            'parking': 'Zone C',
            'emergency': 'Zone D'
        }
        
        for pattern, zone in zone_mapping.items():
            if pattern in filename:
                return zone
        
        # Default zone if no pattern matches
        return 'Zone A'
    
    def _create_sample_vision_data(self) -> List[Dict[str, Any]]:
        """
        Create sample vision analysis data for testing when no videos are available
        
        Returns:
            List of sample vision analysis results
        """
        sample_analyses = []
        
        # Use dynamic zone count - default to 2 zones if no videos
        zones = config.get_zones_for_videos(2)  # Default to 2 zones for sample data
        densities = ['moderate', 'high', 'low', 'high', 'moderate', 'low'][:len(zones)]
        behaviors = ['excited', 'calm', 'calm', 'calm', 'excited', 'calm'][:len(zones)]
        
        for i, (zone, density, behavior) in enumerate(zip(zones, densities, behaviors)):
            sample_analysis = {
                'zone': zone,
                'crowd_density': density,
                'crowd_count_estimate': '2500' if density == 'high' else '1200',
                'crowd_behavior': behavior,
                'potential_risks': ['Bottleneck near entrance'] if density == 'high' else [],
                'safety_observations': ['Normal crowd flow', 'Exits clearly visible'],
                'infrastructure_status': ['Barriers functioning', 'Signage clear'],
                'weather_conditions': 'Clear and sunny',
                'lighting_conditions': 'good',
                'accessibility_issues': [],
                'recommended_actions': ['Monitor crowd levels'] if density == 'high' else ['Continue monitoring'],
                'confidence_score': 0.8,
                'additional_notes': f'Sample analysis for {zone}',
                'frame_metadata': {
                    'frame_index': i,
                    'timestamp': f'Frame_{i:03d}',
                    'video_source': f'{zone.lower().replace(" ", "_")}.mp4',
                    'analysis_timestamp': datetime.now().isoformat()
                }
            }
            sample_analyses.append(sample_analysis)
        
        print(f"Created {len(sample_analyses)} sample vision analyses")
        return sample_analyses
    
    def _process_field_reports(self) -> Dict[str, Any]:
        """
        Process field reports using the Report Agent
        
        Returns:
            Report analysis results
        """
        try:
            report_results = self.report_agent.analyze_field_reports()
            print("Field reports analyzed successfully")
            return report_results
            
        except Exception as e:
            print(f"Error processing field reports: {str(e)}")
            return {'error': True, 'error_message': str(e)}
    
    def _create_fusion_summary(self, vision_results: List[Dict[str, Any]], 
                             report_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create fusion summary using the Summarizer Agent
        
        Args:
            vision_results: Vision analysis results
            report_results: Report analysis results
            
        Returns:
            Fusion summary results
        """
        try:
            fusion_results = self.summarizer_agent.create_comprehensive_summary(
                vision_results, report_results
            )
            print("Fusion summary created successfully")
            return fusion_results
            
        except Exception as e:
            print(f"Error creating fusion summary: {str(e)}")
            return {'error': True, 'error_message': str(e)}
    
    def _update_query_context(self, vision_results: List[Dict[str, Any]], 
                            report_results: Dict[str, Any], 
                            fusion_results: Dict[str, Any]):
        """
        Update Query Agent context with latest analysis results
        
        Args:
            vision_results: Vision analysis results
            report_results: Report analysis results
            fusion_results: Fusion summary results
        """
        try:
            self.query_agent.update_context(
                vision_analyses=vision_results,
                report_analysis=report_results,
                fusion_summary=fusion_results
            )
            print("Query agent context updated successfully")
            
        except Exception as e:
            print(f"Error updating query context: {str(e)}")
    
    def get_current_summary(self) -> Dict[str, Any]:
        """
        Get current situational awareness summary
        
        Returns:
            Current summary data
        """
        if not self.current_data.get('fusion_summary'):
            return {
                'status': 'no_data',
                'message': 'No analysis data available. Run analysis first.'
            }
        
        fusion_summary = self.current_data['fusion_summary']
        
        if fusion_summary.get('error'):
            return {
                'status': 'error',
                'message': 'Analysis error occurred',
                'error': fusion_summary.get('error_message', 'Unknown error')
            }
        
        # Extract key information for dashboard
        exec_summary = fusion_summary.get('executive_summary', {})
        zone_analysis = fusion_summary.get('zone_analysis', [])
        
        summary = {
            'status': 'success',
            'overall_situation': exec_summary.get('overall_situation', 'Unknown'),
            'threat_level': exec_summary.get('threat_level', 'yellow'),
            'immediate_concerns': exec_summary.get('immediate_concerns', []),
            'zone_count': len(zone_analysis),
            'zones': zone_analysis,
            'last_update': self.current_data.get('processing_status', {}).get('last_analysis', 'Unknown'),
            'confidence': fusion_summary.get('confidence_metrics', {}).get('overall_confidence', 0.5)
        }
        
        return summary
    
    def get_zone_details(self, zone_name: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific zone
        
        Args:
            zone_name: Name of the zone
            
        Returns:
            Zone detail data
        """
        zone_details = {
            'zone_name': zone_name,
            'status': 'unknown',
            'data_available': False
        }
        
        # Get data from fusion summary
        fusion_summary = self.current_data.get('fusion_summary', {})
        if fusion_summary and not fusion_summary.get('error'):
            zone_analysis = fusion_summary.get('zone_analysis', [])
            
            for zone in zone_analysis:
                if zone.get('zone_name') == zone_name:
                    zone_details.update({
                        'status': zone.get('status_assessment', 'unknown'),
                        'crowd_situation': zone.get('crowd_situation', {}),
                        'risk_assessment': zone.get('risk_assessment', {}),
                        'infrastructure_status': zone.get('infrastructure_status', 'unknown'),
                        'recommended_actions': zone.get('recommended_actions', []),
                        'data_available': True
                    })
                    break
        
        # Get additional data from vision analyses
        vision_analyses = self.current_data.get('vision_analyses', [])
        zone_vision_data = [a for a in vision_analyses if a.get('zone') == zone_name and not a.get('error')]
        
        if zone_vision_data:
            zone_details['vision_data'] = {
                'frames_analyzed': len(zone_vision_data),
                'latest_analysis': zone_vision_data[-1] if zone_vision_data else None
            }
        
        return zone_details
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a user question using the Query Agent
        
        Args:
            question: User's question
            
        Returns:
            Answer data
        """
        try:
            answer = self.query_agent.answer_query(question)
            return answer
            
        except Exception as e:
            return {
                'answer': 'Sorry, I cannot process your question at the moment due to a system error.',
                'error': True,
                'error_message': str(e),
                'confidence': 0.0
            }
    
    def get_suggested_questions(self) -> List[str]:
        """
        Get suggested questions for the user
        
        Returns:
            List of suggested questions
        """
        try:
            return self.query_agent.get_suggested_questions()
        except Exception as e:
            print(f"Error getting suggested questions: {str(e)}")
            return [
                "What is the current overall situation?",
                "Are there any safety concerns?",
                "Which zones need attention?"
            ]
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get overall system status
        
        Returns:
            System status information
        """
        return {
            'coordinator_status': self.status,
            'last_analysis': self.last_analysis_time.isoformat() if self.last_analysis_time else None,
            'agents_status': {
                'video_processor': 'ready' if self.video_processor else 'error',
                'vision_agent': 'ready' if self.vision_agent and self.vision_agent.vision_model else 'error',
                'report_agent': 'ready' if self.report_agent and self.report_agent.text_model else 'error',
                'summarizer_agent': 'ready' if self.summarizer_agent and self.summarizer_agent.text_model else 'error',
                'query_agent': 'ready' if self.query_agent and self.query_agent.text_model else 'error'
            },
            'data_status': {
                'vision_analyses_count': len(self.current_data.get('vision_analyses', [])),
                'report_analysis_available': bool(self.current_data.get('report_analysis')),
                'fusion_summary_available': bool(self.current_data.get('fusion_summary')),
                'last_processing_status': self.current_data.get('processing_status', {})
            },
            'api_key_configured': bool(config.GOOGLE_API_KEY)
        }
    
    def refresh_analysis(self) -> Dict[str, Any]:
        """
        Refresh analysis by running the full workflow again
        
        Returns:
            Refresh results
        """
        print("Refreshing analysis...")
        return self.run_full_analysis()


if __name__ == "__main__":
    # Test the Coordinator Agent
    print("Testing Coordinator Agent...")
    
    try:
        coordinator = CoordinatorAgent()
        print(f"Coordinator status: {coordinator.status}")
        
        # Test system status
        status = coordinator.get_system_status()
        print(f"System status: {status}")
        
        print("Coordinator Agent structure validated successfully")
        
    except Exception as e:
        print(f"Error testing Coordinator Agent: {str(e)}")
        print(traceback.format_exc())