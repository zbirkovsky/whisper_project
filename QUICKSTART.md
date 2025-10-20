# CloudCall Transcription - Quick Start Guide

## Getting Started in 5 Minutes

### Step 1: Install Dependencies (First Time Only)

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install PyTorch with CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install application dependencies
pip install -r requirements.txt
```

### Step 2: Configure HuggingFace Token (For Speaker Diarization)

1. Get token from https://huggingface.co/settings/tokens
2. Accept terms at https://huggingface.co/pyannote/speaker-diarization
3. Copy `config\.env.example` to `config\.env`
4. Edit `config\.env` and add your token:
   ```
   CLOUDCALL_HF_TOKEN=your_token_here
   ```

### Step 3: Run the Application

```bash
python -m transcription_app.main
```

That's it! The application window should open.

## First Use

1. **Drag & Drop**: Drop an audio file (MP3, WAV, etc.) into the drop zone
2. **Wait**: First run will download models (~1-3GB, takes 5-10 minutes)
3. **View Results**: Transcription appears in the bottom pane with timestamps and speakers

## Common Commands

### Run Application
```bash
python -m transcription_app.main
```

### Build Executable
```bash
pyinstaller transcription_app.spec
# Output in: dist\CloudCallTranscription\
```

### Run Tests (if you add them)
```bash
pytest tests/
```

## Troubleshooting

**Issue**: GPU not detected
```bash
# Check CUDA
nvidia-smi

# Verify PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

**Issue**: Out of memory
- Edit `config/settings.toml`
- Change `whisper_model = "base"` (smaller model)
- Reduce `batch_size = 8`

**Issue**: Diarization fails
- Verify HuggingFace token in `config\.env`
- Check internet connection

## Configuration Quick Reference

Edit `config/settings.toml`:

```toml
[transcription]
whisper_model = "base"  # Options: tiny, base, small, medium, large-v2
device = "cuda"         # or "cpu" if no GPU
batch_size = 16

[diarization]
enabled = true
hf_token = ""  # Or set in config\.env
```

## Model Sizes

| Model | Size | Speed | Accuracy | VRAM |
|-------|------|-------|----------|------|
| tiny | 39MB | Fastest | Low | 1GB |
| base | 74MB | Fast | Good | 2GB |
| small | 244MB | Medium | Better | 3GB |
| medium | 769MB | Slow | High | 5GB |
| large-v2 | 1.5GB | Slowest | Best | 10GB |

**Recommendation**: Start with `base` for testing, upgrade to `small` or `medium` for production.

## Next Steps

- Read full [README.md](README.md) for detailed documentation
- Check [instructions.md](instructions.md) for implementation details
- Customize UI styling in `transcription_app/gui/main_window.py`
- Add more features in the MVVM architecture

## Support

Questions? Check:
- README.md - Full documentation
- GitHub Issues - Report bugs
- instructions.md - Technical implementation details
