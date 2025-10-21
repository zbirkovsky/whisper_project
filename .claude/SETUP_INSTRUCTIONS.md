# Claude Code Setup Instructions for CloudCall Transcription

This file contains automated setup instructions for Claude Code. When you paste these instructions into Claude Code on a new computer, it will automatically clone the repository and install all dependencies.

## Project Information

- **Repository**: https://github.com/zbirkovsky/whisper_project.git
- **Project Type**: Windows Desktop Application (Audio Transcription with AI)
- **Tech Stack**: Python 3.10+, PySide6, WhisperX, PyTorch with CUDA
- **Platform**: Windows 10/11 (64-bit)

## Prerequisites

Before running these instructions, ensure you have:
1. Python 3.10 or 3.11 installed
2. NVIDIA GPU with CUDA support (recommended, optional for CPU mode)
3. CUDA Toolkit 11.8 installed (for GPU acceleration)
4. Git installed
5. Internet connection (for downloading models)

## Automated Setup Instructions

Follow these steps in order. Claude Code will execute each step automatically.

### Step 1: Clone Repository

```bash
git clone https://github.com/zbirkovsky/whisper_project.git
cd whisper_project
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment

```bash
venv\Scripts\activate
```

### Step 4: Install PyTorch with CUDA Support

Install PyTorch with CUDA 11.8 (required before other dependencies):

```bash
venv\Scripts\pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

For CPU-only installation (if no NVIDIA GPU):
```bash
venv\Scripts\pip install torch torchvision torchaudio
```

### Step 5: Verify GPU Support

```bash
venv\Scripts\python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU-only mode\"}')"
```

### Step 6: Install Application Dependencies

```bash
venv\Scripts\pip install -r requirements.txt
```

This installs:
- PySide6 (GUI framework)
- PyAudioWPatch (audio recording with WASAPI loopback)
- WhisperX (transcription engine)
- Pyannote.audio (speaker diarization)
- All supporting libraries (librosa, transformers, etc.)

### Step 7: Configure HuggingFace Token

**Important**: Speaker diarization requires a HuggingFace token.

1. Get your token:
   - Visit: https://huggingface.co/settings/tokens
   - Create a new token with read permissions
   - Accept model terms: https://huggingface.co/pyannote/speaker-diarization

2. Create config file:
```bash
copy config\.env.example config\.env
```

3. Edit `config\.env` and add your token:
```
CLOUDCALL_HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 8: Test Installation

Run a quick verification:

```bash
venv\Scripts\python -m transcription_app.main --help
```

### Step 9: Launch Application

```bash
venv\Scripts\python -m transcription_app.main
```

Or use the launcher script:
```bash
run.bat
```

## Configuration Options

After installation, you can customize settings in `config/settings.toml`:

```toml
[transcription]
# Model selection - larger = better quality but slower
whisper_model = "base"  # Options: tiny, base, small, medium, large-v2, large-v3
compute_type = "float16"  # float16 (GPU), int8 (CPU), float32 (compatibility)
batch_size = 16  # Reduce if out of memory errors
device = "cuda"  # "cuda" for GPU, "cpu" for CPU-only
language = "auto"  # auto, cs (Czech), en (English), or any Whisper language code

# Language-specific optimized models
model_czech = "whisper-large-v3-czech-cv13-ct2"  # 27% better accuracy for Czech
model_english = "large-v3-turbo"  # 8x faster for English
model_fallback = "large-v3"  # Used when language unknown

[diarization]
enabled = true
min_speakers = 1
max_speakers = 10

[audio]
sample_rate = 16000
chunk_duration = 30  # seconds
```

## First Run Notes

On the first run:
1. **Model Download**: WhisperX will automatically download required models (~1-6GB)
   - Location: `%USERPROFILE%\.cloudcall\models\`
   - Time: 5-15 minutes (depending on model size and internet speed)
2. **Application Data**: Created at `%USERPROFILE%\.cloudcall\`
   - Includes models, logs, and recordings

## Troubleshooting

### GPU Not Detected

```bash
# Check NVIDIA driver
nvidia-smi

# Verify PyTorch CUDA support
venv\Scripts\python -c "import torch; print(torch.cuda.is_available())"
```

If False, reinstall PyTorch with correct CUDA version.

### Module Import Errors

If you get "No module named 'X'" errors:

```bash
# Ensure virtual environment is activated
venv\Scripts\activate

# Reinstall dependencies
venv\Scripts\pip install -r requirements.txt
```

### Speaker Diarization Fails

- Verify HuggingFace token in `config\.env`
- Accept terms at: https://huggingface.co/pyannote/speaker-diarization
- Check internet connection (models download on first use)
- Try running with `--no-diarization` flag for testing

### Out of Memory Errors

Edit `config/settings.toml`:
- Reduce `batch_size` to 8 or 4
- Use smaller model: `whisper_model = "base"` or `"small"`
- Close other GPU applications

### Audio Recording Issues

- Check microphone permissions in Windows Settings → Privacy → Microphone
- For system audio capture, ensure loopback device is detected
- PyAudioWPatch automatically detects WASAPI loopback devices

## Project Structure

```
whisper_project/
├── transcription_app/          # Main application package
│   ├── core/                   # Core business logic
│   │   ├── audio_recorder.py   # Audio recording (WASAPI loopback)
│   │   ├── transcription_engine.py  # WhisperX integration
│   │   └── model_manager.py    # Multi-language model management
│   ├── gui/                    # User interface (PySide6)
│   │   ├── main_window.py      # Main window
│   │   ├── styles/             # Centralized theme and styling
│   │   └── widgets/            # Custom widgets (file queue, recording dialog)
│   ├── viewmodels/             # MVVM ViewModels
│   ├── integrations/           # External integrations (Teams detection)
│   ├── utils/                  # Utilities (config, logging, language detection)
│   └── main.py                 # Application entry point
├── config/                     # Configuration files
│   ├── settings.toml           # Application settings
│   └── .env.example            # Environment variables template
├── requirements.txt            # Python dependencies
├── run.bat                     # Windows launcher script
└── README.md                   # Full documentation
```

## Key Features

- **High-Accuracy Transcription**: WhisperX with state-of-the-art Whisper models
- **Multi-Language Support**: Optimized models for Czech (27% better) and English (8x faster)
- **Speaker Diarization**: Automatic speaker identification and labeling
- **GPU Acceleration**: 5-10x real-time transcription on RTX GPUs
- **Audio Recording**: Capture microphone + system audio simultaneously
- **Teams Integration**: Auto-detects meeting names for organized recordings
- **Modern UI**: Fluent Design-inspired interface with drag-and-drop
- **Multiple Export Formats**: TXT and SRT subtitle files
- **Batch Processing**: Queue multiple files for processing

## Performance Expectations

With NVIDIA RTX 4090:
- Transcription: 5-10x real-time
- Memory: 4-8GB VRAM (depending on model)
- Startup: 2-5 seconds (after models downloaded)

With NVIDIA RTX 3060:
- Transcription: 2-4x real-time
- Memory: 3-6GB VRAM

CPU-only mode:
- Transcription: 0.3-1x real-time (slower than real-time)
- Use smaller models (tiny, base) for better performance

## Usage Quick Start

1. **Launch Application**:
   ```bash
   venv\Scripts\python -m transcription_app.main
   ```

2. **Transcribe Files**:
   - Drag and drop audio files (MP3, WAV, M4A, FLAC, MP4, OGG, WMA, AAC)
   - Or click "Open Files" to browse
   - Watch progress in the queue
   - View transcripts in the bottom pane

3. **Record Audio**:
   - Click "Record Audio" button
   - Select microphone and/or system audio
   - Choose language (auto-detect, Czech, English)
   - Start recording (unlimited duration, with pause/resume)
   - Stop when done - file auto-added to transcription queue

4. **Export Results**:
   - Click "Save as TXT" for plain text
   - Click "Save as SRT" for subtitle format

## Additional Resources

- **Documentation**: See README.md for full documentation
- **Installation Details**: See INSTALL.md for manual setup
- **Quick Start**: See QUICKSTART.md for usage tips
- **GitHub Issues**: https://github.com/zbirkovsky/whisper_project/issues

## System Requirements

### Minimum
- Windows 10 (64-bit) or later
- Python 3.10 or 3.11
- 8GB RAM
- 5GB free disk space
- Intel Core i5 or equivalent

### Recommended
- Windows 11 (64-bit)
- Python 3.10
- NVIDIA GPU with 6GB+ VRAM (RTX 3060 or better)
- CUDA Toolkit 11.8
- 16GB RAM
- 10GB free SSD space
- Intel Core i7 or equivalent

## License

[Add your license information here]

## Credits

- WhisperX: https://github.com/m-bain/whisperX
- Pyannote.audio: https://github.com/pyannote/pyannote-audio
- OpenAI Whisper: https://github.com/openai/whisper
- PyAudioWPatch: https://github.com/s0d3s/PyAudioWPatch

---

**Built with Claude Code** 🤖

## Notes for Claude Code

When setting up this project:
1. Execute steps 1-6 automatically
2. For Step 7 (HuggingFace token), prompt the user to provide their token
3. Create the `.env` file and help user add the token
4. Run verification tests in Step 8
5. Launch the application in Step 9 to confirm successful setup
6. If any errors occur, refer to the Troubleshooting section

This project is GPU-intensive but can run on CPU. Always verify CUDA availability and guide the user accordingly.
