# CloudCall Transcription Application

A professional Windows desktop application for audio transcription with speaker diarization, powered by WhisperX and Pyannote.audio.

## Features

- **High-Accuracy Transcription**: Uses OpenAI's Whisper model via WhisperX for state-of-the-art speech recognition
- **Multi-Language Support**: Optimized models for Czech (27% better accuracy) and English (8x faster), with auto-detection
- **Language Detection**: Automatically detects language from Teams meeting names and file content
- **Speaker Diarization**: Automatically identifies and labels different speakers using Pyannote.audio
- **GPU Acceleration**: Leverages NVIDIA CUDA for fast transcription (up to 10x real-time on RTX 4090)
- **Audio Recording**: Capture audio from microphone and/or system audio simultaneously using WASAPI loopback
- **Teams Integration**: Auto-detects Teams meeting names for organized recordings
- **Drag & Drop Interface**: Modern, Fluent Design-inspired UI with drag-and-drop file support
- **Multiple Export Formats**: Save transcripts as TXT or SRT subtitle files
- **Batch Processing**: Process multiple audio files in queue
- **Native Windows Application**: Built with PySide6 for true native performance

## System Requirements

### Minimum Requirements
- **OS**: Windows 10 (64-bit) or later
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 5GB free space (for application and models)
- **CPU**: Intel Core i5 or equivalent

### Recommended Requirements
- **GPU**: NVIDIA GPU with 6GB+ VRAM (RTX 3060 or better)
- **CUDA**: CUDA Toolkit 11.8 or 12.x
- **RAM**: 16GB or more
- **Storage**: SSD with 10GB+ free space

## Installation

### Option 1: Install from Executable (Easiest)

1. Download `CloudCallTranscription-Setup-1.0.0.exe` from the releases page
2. Run the installer and follow the prompts
3. Launch "CloudCall Transcription" from your Start Menu
4. On first run, the application will download required models (3-6GB)

### Option 2: Install from Source (For Developers)

#### Step 1: Prerequisites

Install Python 3.10 (recommended) or 3.11:
```bash
# Download from https://www.python.org/downloads/
python --version  # Verify installation
```

Install CUDA Toolkit (for GPU support):
```bash
# Download from https://developer.nvidia.com/cuda-downloads
# Recommended: CUDA 11.8
nvidia-smi  # Verify GPU and driver
```

#### Step 2: Clone Repository

```bash
git clone https://github.com/yourorg/cloudcall-transcription.git
cd cloudcall-transcription
```

#### Step 3: Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

#### Step 4: Install PyTorch with CUDA

```bash
# For CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify GPU support
python -c "import torch; print(torch.cuda.is_available())"
```

#### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 6: Configure Application

```bash
# Copy example config
copy config\.env.example config\.env

# Edit config\.env with your settings
# IMPORTANT: Add your HuggingFace token for speaker diarization
notepad config\.env
```

Get HuggingFace token:
1. Go to https://huggingface.co/settings/tokens
2. Create a new token with read permissions
3. Accept terms at https://huggingface.co/pyannote/speaker-diarization
4. Add token to `config\.env`: `CLOUDCALL_HF_TOKEN=your_token_here`

#### Step 7: Run Application

```bash
python -m transcription_app.main
```

## Usage

### Basic Workflow

1. **Add Files**:
   - Drag and drop audio files onto the drop zone
   - Or click "Open Files" to browse
   - Supported formats: MP3, WAV, M4A, FLAC, MP4, OGG, WMA, AAC

2. **Processing**:
   - Files are automatically added to the queue
   - Transcription starts immediately
   - Progress is shown for each file

3. **View Results**:
   - Transcripts appear in the bottom pane
   - Timestamps and speaker labels included
   - Format: `[00:15.23] Speaker 1: Text content`

4. **Export**:
   - Click "Save as TXT" for plain text
   - Click "Save as SRT" for subtitle file

### Recording Audio

1. Click "Record Audio" button
2. Configure settings:
   - **Audio Sources**: Choose microphone and/or system audio
   - **Meeting Name**: Auto-detects Teams meetings or enter manually
   - **Language**: Select transcription language (Auto-detect, Czech, English)
3. Click "Start Recording"
4. Recording supports unlimited duration with pause/resume
5. Recorded file is automatically added to transcription queue

### Multi-Language Support

The application intelligently selects the best model based on language:

**Czech Language** (Fine-tuned model):
- Model: `whisper-large-v3-czech-cv13-ct2`
- Accuracy: 7.89% WER (27% better than generic model)
- Best for: Czech meetings, customer calls, documentation

**English Language** (Turbo model):
- Model: `large-v3-turbo`
- Speed: 8x faster than standard large-v3
- Best for: English meetings, quick transcription

**Auto-Detection**:
- Automatically detects language from Teams meeting names
- Uses Czech-specific character detection (áčďéěíňóřšťúůýž)
- Falls back to generic `large-v3` model for other languages

**How to Use**:
1. In Recording Dialog, language is auto-detected from Teams meeting name
2. You can override by selecting from the dropdown (Auto-detect, Czech, English)
3. System automatically loads the optimal model for selected language

### Configuration

Edit `config/settings.toml` to customize:

```toml
[transcription]
whisper_model = "large-v3"  # Default model for auto-detection
compute_type = "float16"  # float16 (GPU), int8 (CPU), float32 (compatibility)
batch_size = 16
device = "cuda"  # or "cpu"
language = "auto"  # auto, cs (Czech), en (English)

# Language-specific models for optimal quality
model_czech = "whisper-large-v3-czech-cv13-ct2"  # 7.89% WER - 27% better for Czech
model_english = "large-v3-turbo"  # 8x faster for English
model_fallback = "large-v3"  # Used when language unknown

[diarization]
enabled = true
min_speakers = 1
max_speakers = 10
```

**Model Size Guide**:
- `tiny` (39MB): Fast but less accurate, good for testing
- `base` (74MB): Good balance, recommended for most users
- `small` (244MB): Better accuracy
- `medium` (769MB): High accuracy
- `large-v2` (1.5GB): Best accuracy, requires 6GB+ VRAM

## Building Executable

### Create Standalone Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Edit transcription_app.spec and update CUDA_PATH if needed

# Build
pyinstaller transcription_app.spec

# Output will be in dist\CloudCallTranscription\
```

### Create Installer

1. Install Inno Setup: https://jrsoftware.org/isdl.php
2. Open `installer.iss` in Inno Setup Compiler
3. Click "Build" → "Compile"
4. Installer will be created in `installer_output\`

## Troubleshooting

### GPU Not Detected

```bash
# Check CUDA installation
nvidia-smi

# Verify PyTorch CUDA support
python -c "import torch; print(torch.cuda.is_available())"
```

If GPU not detected, reinstall PyTorch with correct CUDA version.

### Speaker Diarization Not Working

- Ensure HuggingFace token is set in `config\.env`
- Accept terms at https://huggingface.co/pyannote/speaker-diarization
- Check internet connection (models download on first use)

### Audio Recording Issues

- Ensure microphone permissions are granted in Windows Settings
- For system audio, verify "Stereo Mix" or similar is enabled
- PyAudioWPatch should automatically detect loopback devices

### Out of Memory Errors

- Reduce `batch_size` in `config/settings.toml`
- Use smaller Whisper model (`base` or `small`)
- Close other GPU-intensive applications

## Project Structure

```
cloudcall-transcription/
├── transcription_app/          # Main application package
│   ├── core/                   # Core business logic
│   │   ├── audio_recorder.py   # Audio recording with PyAudioWPatch
│   │   ├── transcription_engine.py  # WhisperX integration
│   │   └── model_manager.py    # Model management
│   ├── gui/                    # User interface
│   │   ├── main_window.py      # Main window
│   │   └── widgets/            # UI widgets (file queue, recording, overlay)
│   ├── viewmodels/             # MVVM ViewModels
│   │   └── transcription_vm.py
│   ├── integrations/           # External integrations
│   │   └── teams_detector.py   # Teams meeting detection
│   ├── utils/                  # Utilities
│   │   ├── config.py           # Configuration management
│   │   ├── logger.py           # Logging setup
│   │   └── language_detector.py # Language detection for multi-language support
│   └── main.py                 # Application entry point
├── config/                     # Configuration files
│   ├── settings.toml
│   └── .env.example
├── requirements.txt            # Python dependencies
├── transcription_app.spec      # PyInstaller spec
├── installer.iss               # Inno Setup script
└── README.md
```

## Technology Stack

- **GUI**: PySide6 (Qt for Python)
- **Transcription**: WhisperX, Faster Whisper
- **Diarization**: Pyannote.audio
- **Audio**: PyAudioWPatch (WASAPI loopback)
- **ML Framework**: PyTorch with CUDA
- **Packaging**: PyInstaller, Inno Setup

## Performance

Expected performance with RTX 4090:
- Transcription: 5-10x real-time
- Memory: 4-8GB VRAM (depending on model)
- First-time model download: 5-10 minutes (3-6GB)
- Subsequent runs: 2-5 seconds startup

## License

[Add your license here]

## Credits

- WhisperX: https://github.com/m-bain/whisperX
- Pyannote.audio: https://github.com/pyannote/pyannote-audio
- OpenAI Whisper: https://github.com/openai/whisper

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourorg/cloudcall-transcription/issues
- Documentation: [Add docs link]

---

**Built with Claude Code** 🤖
