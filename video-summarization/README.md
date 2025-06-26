# 📹 Video Summarization App

A comprehensive video summarization system using AI models, LangChain, and Streamlit with advanced features for content analysis and batch processing.

## ✨ Features

### 🔧 Core Functionality
- **Multi-format Video Support**: MP4, AVI, MOV, MKV
- **Intelligent Frame Extraction**: Configurable intervals and maximum frame limits
- **AI-Powered Analysis**: Multiple model support (Gemma 3:27B, Llama 3:8B, Mistral:7B)
- **Customizable Summaries**: Brief, Detailed, or Comprehensive analysis options

### 🎯 Advanced Features
- **📊 Analytics Dashboard**: Processing statistics and performance metrics
- **🔄 Batch Processing**: Process multiple videos simultaneously
- **💾 Processing History**: Automatic saving and tracking of all summaries
- **📄 Export Options**: Download reports in Markdown format
- **🖼️ Frame Preview**: Visual thumbnails of extracted frames
- **⚙️ Configurable Settings**: Customizable extraction parameters and AI model selection

### 🎨 User Interface
- **Tabbed Interface**: Organized layout with separate sections for processing, analytics, and batch operations
- **Real-time Progress Tracking**: Visual progress bars and status updates
- **Responsive Design**: Clean, modern UI with proper spacing and organization
- **Sidebar Controls**: Easy access to settings and recent processing history

## 🚀 Quick Start

### Pre-requisites

1. **Install Ollama** from the [official website](https://ollama.com/)

2. **Pull AI Models** (choose one or more):
```bash
# Recommended for best quality
ollama pull gemma3:27b

# Alternative models
ollama pull llama3:8b
ollama pull mistral:7b
```

### Installation

1. **Create Python Virtual Environment**:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the Application**:
```bash
streamlit run video_summary.py
```

4. **Access the App**: Open your browser to `http://localhost:8501`

## 📖 How to Use

### Single Video Processing
1. Navigate to the **📹 Video Processor** tab
2. Configure settings in the sidebar:
   - Frame interval (1-30 seconds)
   - Maximum frames (5-50)
   - AI model selection
   - Summary length preference
3. Upload your video file
4. View processing progress and results
5. Download summary report or copy to clipboard

### Batch Processing
1. Enable **🔄 Batch Processing Mode** in the Video Processor tab
2. Upload multiple video files
3. Click **Process All Videos**
4. Monitor progress and view results for each video

### Analytics & History
1. Visit the **📊 Analytics** tab to view:
   - Total videos processed
   - Average processing times
   - Performance metrics
   - Detailed processing history

## 🏗️ Technical Architecture

### Processing Pipeline
1. **Video Upload**: Secure file handling with size and format validation
2. **Frame Extraction**: OpenCV-based intelligent frame sampling
3. **AI Analysis**: Multi-model support with customizable prompts
4. **Result Processing**: Enhanced formatting and export capabilities
5. **Data Persistence**: JSON-based history and analytics storage

### Technology Stack
- **Frontend**: Streamlit with custom UI components
- **Video Processing**: OpenCV (cv2) for frame extraction
- **AI Integration**: LangChain with Ollama backend
- **Data Storage**: JSON files for history and configuration
- **Logging**: Comprehensive logging system with file and console output

## 📁 Project Structure

```
video-summarization/
├── video_summary.py          # Main application
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── GEMMA3.md               # Model documentation
├── LIBRARIES.md            # Library information
├── Prompts.md              # Prompt templates
├── videos/                 # Uploaded videos
├── frames/                 # Extracted frames
├── logs/                   # Application logs
└── processing_history.json # Processing history (auto-generated)
```

## ⚙️ Configuration Options

### Frame Extraction
- **Interval**: 1-30 seconds between frames
- **Max Frames**: 5-50 frames per video
- **Quality**: Automatic optimization based on video properties

### AI Models
- **Gemma 3:27B**: Best quality, slower processing
- **Llama 3:8B**: Balanced performance
- **Mistral:7B**: Fastest processing

### Summary Types
- **Brief**: 2-3 sentence concise summary
- **Detailed**: Comprehensive paragraph with key elements
- **Comprehensive**: Full analysis with scene descriptions

## 🛠️ Advanced Usage

### Environment Management
```bash
# Deactivate virtual environment
deactivate

# Delete virtual environment
rm -rf .venv  # Linux/Mac
rmdir /s .venv  # Windows
```

### Custom Model Configuration
Edit the `available_models` list in `video_summary.py` to add or remove models:
```python
available_models = ["gemma3:27b", "llama3:8b", "mistral:7b", "your-custom-model"]
```

### Logging Configuration
Logs are automatically saved to `logs/video_summary.log` with configurable levels and formats.

## 🧪 Testing

### Unit Tests Overview
The project includes a comprehensive test suite with 37 tests covering:
- **Core functionality** (video processing, frame extraction, AI analysis)
- **Settings validation** (all configuration options)
- **Integration testing** (real video file processing)
- **Error handling** and edge cases

### Test Structure
```
test_video_summary.py
├── TestVideoSummary (18 tests)
│   ├── Processing history tests
│   ├── Export functionality tests
│   ├── Frame extraction tests
│   └── Video analysis tests
├── TestVideoSummaryIntegration (4 tests)
│   ├── Real video file testing
│   ├── Video properties validation
│   └── Integration scenarios
└── TestVideoSummarySettings (15 tests)
    ├── Frame interval validation (1, 5, 15, 30s)
    ├── Max frames validation (5, 25, 50)
    ├── AI model validation (gemma3:27b, llava:7b, bakllava)
    ├── Summary options validation (Brief, Detailed, Comprehensive)
    ├── Timestamp validation (checked/unchecked)
    └── Input video validation (test01.mkv, test02.mp4)
```

### Running Unit Tests

#### Prerequisites for Testing
Ensure you have test video files in the `videos/` directory:
- `./videos/test01.mkv` (longer video for comprehensive testing)
- `./videos/test02.mp4` (shorter video for quick testing)

#### Basic Test Commands

1. **Run All Tests**:
```bash
# Activate virtual environment first
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run all tests with verbose output
python -m unittest test_video_summary -v
```

2. **Run Specific Test Classes**:
```bash
# Test core functionality
python -m unittest test_video_summary.TestVideoSummary -v

# Test integration scenarios
python -m unittest test_video_summary.TestVideoSummaryIntegration -v

# Test settings validation
python -m unittest test_video_summary.TestVideoSummarySettings -v
```

3. **Run Individual Test Methods**:
```bash
# Test video path setup
python -m unittest test_video_summary.TestVideoSummary.test_video_paths_setup -v

# Test frame extraction with real video
python -m unittest test_video_summary.TestVideoSummaryIntegration.test_extract_frames_with_real_video -v

# Test all frame interval settings
python -m unittest test_video_summary.TestVideoSummarySettings.test_frame_interval_settings -v
```

#### Test Categories

**Unit Tests (Mocked)**:
```bash
# Fast tests with mocked dependencies
python -m unittest test_video_summary.TestVideoSummary.test_save_processing_history_new_file -v
python -m unittest test_video_summary.TestVideoSummary.test_export_summary -v
python -m unittest test_video_summary.TestVideoSummary.test_extract_frames_success -v
```

**Integration Tests (Real Files)**:
```bash
# Tests that work with actual video files
python -m unittest test_video_summary.TestVideoSummaryIntegration.test_video_files_exist -v
python -m unittest test_video_summary.TestVideoSummaryIntegration.test_video_properties_validation -v
```

**Settings Validation Tests**:
```bash
# Verify all required configuration options
python -m unittest test_video_summary.TestVideoSummarySettings.test_ai_model_settings -v
python -m unittest test_video_summary.TestVideoSummarySettings.test_summary_length_settings -v
python -m unittest test_video_summary.TestVideoSummarySettings.test_input_video_paths -v
```

#### Test Output Example
```bash
$ python -m unittest test_video_summary.TestVideoSummarySettings -v

test_ai_model_settings ... ok
test_combination_settings_matrix ... ok
test_frame_interval_settings ... ok
test_input_video_paths ... ok
test_max_frames_25 ... ok
test_summary_length_settings ... ok
test_timestamp_settings_checked ... ok

----------------------------------------------------------------------
Ran 15 tests in 0.787s

OK
```

#### Continuous Testing
For development, you can use a simple watch script:
```bash
# Install pytest-watch if you prefer
pip install pytest-watch

# Or use a simple loop for continuous testing
while true; do
    python -m unittest test_video_summary.TestVideoSummary -v
    sleep 5
done
```

### Test Configuration Validation

The test suite validates all required settings from the application:

**✅ Frame Extraction Settings**:
- Frame intervals: 1, 5, 15, 30 seconds
- Max frames: 5, 25, 50 frames

**✅ AI Model Settings**:
- gemma3:27b, llava:7b, bakllava models

**✅ Summary Options**:
- Summary lengths: Brief, Detailed, Comprehensive
- Include timestamps: checked/unchecked

**✅ Input Videos**:
- ./videos/test01.mkv (1920x1080, 60 FPS, ~8 minutes)
- ./videos/test02.mp4 (1280x720, 24 FPS, 8 seconds)

### Testing Best Practices

1. **Run tests before committing changes**:
```bash
python -m unittest test_video_summary -v
```

2. **Test specific functionality after modifications**:
```bash
# After modifying frame extraction
python -m unittest test_video_summary.TestVideoSummary.test_extract_frames_success -v

# After modifying AI model integration
python -m unittest test_video_summary.TestVideoSummarySettings.test_ai_model_settings -v
```

3. **Validate with real videos periodically**:
```bash
python -m unittest test_video_summary.TestVideoSummaryIntegration -v
```

### Test Data Requirements

- **Test Videos**: Place test videos in `videos/` directory
- **Temporary Files**: Tests create and clean up temporary files automatically
- **Mock Data**: Unit tests use mocked data for fast, isolated testing
- **Real Integration**: Integration tests require actual video files

## 🔍 Troubleshooting

### Common Issues
1. **Model Not Found**: Ensure Ollama is running and models are pulled
2. **Video Upload Failed**: Check file size (<200MB) and format compatibility
3. **Frame Extraction Error**: Verify video file integrity and codec support
4. **Memory Issues**: Reduce max frames or use smaller models

### Performance Optimization
- Use smaller models for faster processing
- Reduce frame extraction interval for lighter analysis
- Enable batch processing for multiple videos
- Monitor system resources during processing

## 🤝 Contributing

This is a proof-of-concept application. For improvements or bug reports, please:
1. Check existing issues
2. Create detailed bug reports
3. Suggest feature enhancements
4. Submit pull requests with tests

## 📄 License

This project is open source and available under standard terms.

---

**Built with ❤️ using Streamlit, OpenCV, LangChain, and Ollama**