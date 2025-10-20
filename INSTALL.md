# Installation Guide

## ✅ What You Have

Good news! PyTorch with CUDA 11.8 is already installed in your virtual environment:
- torch 2.7.1+cu118 ✓
- torchvision 0.22.1+cu118 ✓
- torchaudio 2.7.1+cu118 ✓

## 🔧 Complete Installation

### Step 1: Navigate to Project Directory

```bash
cd C:\Whisper_project
```

### Step 2: Activate Virtual Environment

Your venv is at: `C:\Windows\System32\venv`

```bash
C:\Windows\System32\venv\Scripts\activate
```

### Step 3: Install Application Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- PySide6 (GUI framework)
- PyAudioWPatch (audio recording)
- WhisperX (transcription)
- Pyannote.audio (speaker diarization)
- All supporting libraries

### Step 4: Configure HuggingFace Token

**Required for speaker diarization:**

1. Get token from: https://huggingface.co/settings/tokens
2. Accept model terms: https://huggingface.co/pyannote/speaker-diarization
3. Create config file:
   ```bash
   copy config\.env.example config\.env
   ```
4. Edit `config\.env` and add your token:
   ```
   CLOUDCALL_HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### Step 5: Run the Application

From the Whisper_project directory:

```bash
python -m transcription_app.main
```

Or use the launcher:

```bash
run.bat
```

## 📋 Manual Installation Steps

If you prefer manual installation:

```bash
# Activate venv
C:\Windows\System32\venv\Scripts\activate

# Navigate to project
cd C:\Whisper_project

# Install GUI framework
pip install PySide6>=6.6.0

# Install audio recording
pip install PyAudioWPatch>=0.2.12.5

# Install ML dependencies
pip install whisperx>=3.1.1
pip install faster-whisper>=0.9.0
pip install pyannote.audio>=3.1.0
pip install transformers>=4.30.0

# Install audio processing
pip install librosa>=0.10.0
pip install soundfile>=0.12.1

# Install configuration tools
pip install pydantic>=2.0.0
pip install pydantic-settings>=2.0.0
pip install python-dotenv>=1.0.0
pip install toml>=0.10.2

# Install utilities
pip install tqdm>=4.65.0
```

## 🧪 Verify Installation

Test GPU availability:

```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}')"
```

Expected output:
```
CUDA available: True
GPU: NVIDIA GeForce RTX 4090
```

## 🚀 First Run

When you run the app for the first time:

1. **Model Download**: WhisperX will download models (~1-3GB)
   - Location: `%USERPROFILE%\.cloudcall\models\`
   - Time: 5-10 minutes (depending on internet speed)

2. **Application Data**: Created at `%USERPROFILE%\.cloudcall\`
   - Models
   - Logs
   - Recordings

## ⚙️ Configuration

Edit `config/settings.toml` to customize:

```toml
[transcription]
whisper_model = "base"  # Start with base, upgrade to small/medium later
device = "cuda"         # Use GPU
batch_size = 16         # Adjust based on VRAM

[diarization]
enabled = true
min_speakers = 1
max_speakers = 10
```

## 🐛 Troubleshooting

### Issue: "No module named 'PySide6'"

```bash
pip install PySide6
```

### Issue: "No module named 'whisperx'"

```bash
pip install whisperx
```

### Issue: CUDA not available

1. Check GPU driver: `nvidia-smi`
2. Verify CUDA Toolkit installation
3. Reinstall PyTorch with correct CUDA version

### Issue: Diarization fails

- Verify HuggingFace token in `config\.env`
- Accept terms at https://huggingface.co/pyannote/speaker-diarization
- Check internet connection

## 📁 File Locations

- **Project**: `C:\Whisper_project\`
- **Virtual Environment**: `C:\Windows\System32\venv\`
- **App Data**: `%USERPROFILE%\.cloudcall\`
- **Models**: `%USERPROFILE%\.cloudcall\models\`
- **Logs**: `%USERPROFILE%\.cloudcall\app.log`

## ✨ Quick Test

1. Run the application:
   ```bash
   python -m transcription_app.main
   ```

2. Drag and drop a short audio file (MP3, WAV, etc.)

3. Watch the transcription appear in real-time!

## 📚 Next Steps

- Read [README.md](README.md) for full documentation
- Check [QUICKSTART.md](QUICKSTART.md) for usage tips
- Review [config/settings.toml](config/settings.toml) for customization

## 💡 Tips

- **First run**: Use `whisper_model = "base"` for quick testing
- **Production**: Upgrade to `whisper_model = "small"` or `"medium"`
- **Best quality**: Use `"large-v2"` (requires 10GB VRAM)
- **No GPU?**: Set `device = "cpu"` (slower but works)

---

**Need help?** Check the logs at `%USERPROFILE%\.cloudcall\app.log`
