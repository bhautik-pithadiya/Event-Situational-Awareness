# 🚨 Event Situational Awareness System

An **Agentic AI System** for Real-Time Event Situational Awareness using **Google Gemini API**, **LangChain**, and **Streamlit**.

## 🌟 Features

### 🎥 **Multi-Modal Analysis**
- **Video Processing**: Analyzes 3-4 local video feeds with motion-aware frame extraction
- **Field Reports**: Processes text-based field reports and logs
- **AI Vision**: Google Gemini Vision API for crowd density, behavior, and risk assessment
- **Text Analysis**: Gemini API for extracting key insights from reports

### 🤖 **Agentic Architecture**
- **Coordinator Agent**: Orchestrates the entire analysis workflow
- **Vision Agent**: Analyzes video frames for crowd dynamics and safety
- **Report Agent**: Processes field reports and incident logs
- **Summarizer Agent**: Fuses multi-modal data into comprehensive summaries
- **Query Agent**: Handles user questions with contextual knowledge

### 📊 **Interactive Dashboard**
- **Real-time Overview**: Event status, threat levels, and key metrics
- **Zone Cards**: Individual zone status with crowd density and risks
- **AI Chat Interface**: Ask questions about the current situation
- **Auto-refresh**: Continuous monitoring capabilities

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │   Summary   │ │ Zone Cards  │ │   Query Interface   │   │
│  │   Panel     │ │             │ │                     │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                               │
                   ┌─────────────────────┐
                   │ Coordinator Agent   │
                   │   (Orchestrator)    │
                   └─────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Vision Agent │    │Report Agent  │    │ Query Agent  │
│              │    │              │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
        │                      │                      │
        │                      │                      │
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│Video         │    │Field Reports │    │Summarizer    │
│Processor     │    │Analyzer      │    │Agent         │
└──────────────┘    └──────────────┘    └──────────────┘
        │                      │                      │
┌──────────────┐    ┌──────────────┐           ┌──────────────┐
│   Videos/    │    │    data/     │           │  Google      │
│   Frames     │    │field_reports │           │  Gemini API  │
└──────────────┘    └──────────────┘           └──────────────┘
```

## 🚀 Quick Start

### 1. **Clone and Setup**
```bash
git clone <repository-url>
cd Event_Situational_Awareness
pip install -r requirements.txt
```

### 2. **Configure API Key**
```bash
# Copy environment template
cp .env.template .env

# Edit .env file and add your Google Gemini API key
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

### 3. **Add Video Files** (Optional)
Place video files in the `videos/` directory:
- `zone_a.mp4` - Main stage area
- `zone_b.mp4` - Food court area  
- `zone_c.mp4` - Parking area
- `zone_d.mp4` - Emergency services area

*Note: The system will work with sample data if no videos are provided.*

### 4. **Launch Dashboard**
```bash
streamlit run main.py
```

The dashboard will open at `http://localhost:8501`

## 📁 Project Structure

```
Event_Situational_Awareness/
├── main.py                 # Streamlit dashboard entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env.template         # Environment variables template
├── README.md             # This file
├── agents/               # AI agents directory
│   ├── coordinator.py    # Main orchestrator agent
│   ├── vision_agent.py   # Video analysis agent
│   ├── report_agent.py   # Text analysis agent
│   ├── summarizer_agent.py # Multi-modal fusion agent
│   └── query_agent.py    # User query handling agent
├── utils/                # Utility modules
│   └── video_processor.py # Video processing utilities
├── data/                 # Data directory
│   └── field_reports.txt # Sample field reports
└── videos/               # Video files directory
    └── README.md         # Video requirements
```

## 🔧 Usage

### **Running Analysis**
1. Open the Streamlit dashboard
2. Check system status in the sidebar
3. Click "Run Analysis" to process videos and reports
4. View results in the Overview and Zones tabs

### **Asking Questions**
1. Go to the "Query" tab
2. Use suggested questions or type your own
3. Get AI-powered answers with supporting evidence
4. View confidence scores and related information

### **Example Questions**
- "What's the current overall situation?"
- "Which zones need immediate attention?"
- "Are there any safety concerns in Zone A?"
- "What are the crowd density levels?"
- "What resources are needed most urgently?"

## ⚙️ Configuration

### **API Configuration**
- **Required**: Google Gemini API key in `.env` file
- **Models**: Uses `gemini-1.5-pro` for both vision and text analysis

### **Video Processing**
- **Formats**: MP4, AVI, MOV, MKV
- **Frame Extraction**: Motion-aware with configurable thresholds
- **Processing**: Automatic zone detection from filenames

### **Customization**
Edit `config.py` to modify:
- Frame extraction settings
- Zone configurations  
- API model selection
- File paths and directories

## 🛠️ Technical Details

### **Dependencies**
- `streamlit` - Web dashboard framework
- `google-generativeai` - Google Gemini API client
- `langchain` - AI agent framework
- `opencv-python` - Video processing
- `pillow` - Image processing
- `python-dotenv` - Environment management

### **AI Models**
- **Vision Analysis**: Gemini-1.5-Pro Vision for frame analysis
- **Text Analysis**: Gemini-1.5-Pro for report processing
- **Multi-modal Fusion**: Advanced prompt engineering for data synthesis

### **Performance**
- **Motion Detection**: Reduces processing by skipping static frames
- **Batch Processing**: Efficient frame analysis
- **Caching**: Streamlit session state for performance
- **Error Handling**: Comprehensive error recovery

## 🔍 Features in Detail

### **Vision Analysis**
- Crowd density estimation (low/moderate/high/critical)
- Behavior assessment (calm/excited/restless/agitated)
- Risk identification (bottlenecks, safety hazards)
- Infrastructure monitoring (barriers, exits, signage)
- Environmental conditions (weather, lighting)

### **Report Processing**
- Event overview extraction
- Zone-specific status updates
- Priority issue identification
- Resource status assessment
- Environmental factor analysis

### **Multi-Modal Fusion**
- Cross-validation between video and reports
- Discrepancy identification
- Confidence assessment
- Actionable recommendations
- Priority ranking

### **Query Interface**
- Natural language processing
- Context-aware responses
- Confidence scoring
- Supporting evidence
- Follow-up suggestions

## 🚨 Troubleshooting

### **Common Issues**

1. **"System not initialized"**
   - Check Google Gemini API key in `.env` file
   - Verify internet connection for API access

2. **"No video analysis results"**
   - Add video files to `videos/` directory
   - System will use sample data if no videos found

3. **"Analysis failed"**
   - Check API quota and billing
   - Verify video file formats
   - Review console logs for detailed errors

4. **Import errors**
   - Run `pip install -r requirements.txt`
   - Check Python version (3.8+ recommended)

### **Performance Optimization**
- Use smaller video files for faster processing
- Adjust frame extraction interval in `config.py`
- Monitor API usage and costs

## 📈 Future Enhancements

- [ ] Real-time video streaming support
- [ ] Integration with security camera systems
- [ ] Advanced ML models for crowd prediction
- [ ] Mobile-responsive dashboard
- [ ] Alert system with notifications
- [ ] Historical data analysis
- [ ] Multi-language support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini API for powerful AI capabilities
- Streamlit for the excellent dashboard framework
- OpenCV for video processing capabilities
- LangChain for agent orchestration patterns

---

**Built with ❤️ for safer events and better situational awareness**