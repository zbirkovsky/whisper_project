# Troubleshooting Guide

## Common Issues and Solutions

### ✅ FIXED: "Cannot find an appropriate cached snapshot folder" Error

**Symptom:**
```
ERROR: Transcription error: Cannot find an appropriate cached snapshot folder
for the specified revision on the local disk and outgoing traffic has been disabled.
```

**Cause:** WhisperX was trying to use cached models but couldn't find them, and model downloading was disabled.

**Solution:** This has been **fixed** in the latest version. The code now includes `local_files_only=False` to allow downloading models on first run.

**What happens now:**
- First run: Models will download automatically (~1-3GB, takes 5-10 minutes)
- Models are cached to: `%USERPROFILE%\.cloudcall\models\`
- Subsequent runs: Uses cached models (fast startup)

---

## Other Common Issues

### GPU Not Detected

**Symptom:**
```
WARNING: CUDA not available, falling back to CPU
```

**Check:**
```bash
# Verify GPU is visible
nvidia-smi

# Check CUDA in Python
python -c "import torch; print(torch.cuda.is_available())"
```

**Solutions:**
1. Update NVIDIA drivers: https://www.nvidia.com/download/index.aspx
2. Reinstall PyTorch with CUDA:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --force-reinstall
   ```
3. If still not working, check `config/settings.toml` and set `device = "cpu"` as temporary workaround

### Out of Memory (CUDA)

**Symptom:**
```
RuntimeError: CUDA out of memory
```

**Solutions:**

1. **Use smaller model** - Edit `config/settings.toml`:
   ```toml
   [transcription]
   whisper_model = "base"  # Instead of "large-v2"
   ```

2. **Reduce batch size** - Edit `config/settings.toml`:
   ```toml
   [transcription]
   batch_size = 8  # Default is 16
   ```

3. **Close other GPU applications** - Check GPU usage:
   ```bash
   nvidia-smi
   ```

### Speaker Diarization Fails

**Symptom:**
```
WARNING: Diarization failed, continuing without
```

**Common Causes:**

1. **Missing HuggingFace Token**
   - Get token: https://huggingface.co/settings/tokens
   - Accept terms: https://huggingface.co/pyannote/speaker-diarization
   - Add to `config\.env`: `CLOUDCALL_HF_TOKEN=hf_xxxxx`

2. **No Internet Connection**
   - Diarization models download on first use
   - Ensure stable internet connection

3. **Token Permissions**
   - Token must have "read" permissions
   - Must accept model terms of use

**Solution:**
```bash
# Check if token is set
type config\.env

# Should show: CLOUDCALL_HF_TOKEN=hf_xxxxx
```

### Audio Recording Not Working

**Symptom:** No audio recorded or error during recording

**Check:**

1. **Microphone permissions** - Windows Settings → Privacy → Microphone
2. **System audio** - Verify audio playback works
3. **Audio devices**:
   ```python
   from transcription_app.core.audio_recorder import AudioRecorder
   from transcription_app.utils.config import get_config

   config = get_config()
   recorder = AudioRecorder(config)
   devices = recorder.list_devices()
   for d in devices:
       print(d)
   ```

### Import Errors

**Symptom:**
```
ModuleNotFoundError: No module named 'whisperx'
```

**Solution:**
```bash
# Activate venv
C:\Windows\System32\venv\Scripts\activate

# Install dependencies
cd C:\Whisper_project
pip install -r requirements.txt
```

**For specific modules:**
```bash
pip install whisperx
pip install PySide6
pip install PyAudioWPatch
```

### Application Won't Start

**Symptom:** Application crashes immediately or shows no window

**Debug Steps:**

1. **Run from command line** to see errors:
   ```bash
   cd C:\Whisper_project
   python -m transcription_app.main
   ```

2. **Check logs**:
   ```bash
   type "%USERPROFILE%\.cloudcall\app.log"
   ```

3. **Verify Python version**:
   ```bash
   python --version
   # Should be 3.10 or 3.11
   ```

4. **Test imports**:
   ```bash
   python -c "from PySide6.QtWidgets import QApplication; print('OK')"
   ```

### Slow Transcription

**If transcription is slower than expected:**

1. **Verify GPU is being used**:
   - Check `config/settings.toml`: `device = "cuda"`
   - Run `nvidia-smi` during transcription to see GPU usage

2. **Use appropriate model**:
   - `tiny`: Fastest, less accurate
   - `base`: Good balance (recommended)
   - `small`: Better accuracy, slower
   - `medium/large`: Best accuracy, slowest

3. **Increase batch size** (if you have VRAM):
   ```toml
   [transcription]
   batch_size = 32  # Default is 16
   ```

### File Format Not Supported

**Supported formats:**
- Audio: MP3, WAV, M4A, FLAC, OGG, WMA, AAC
- Video: MP4 (audio track will be extracted)

**If file not recognized:**
1. Convert to WAV or MP3 using FFmpeg:
   ```bash
   ffmpeg -i input.file output.wav
   ```

### Models Keep Re-downloading

**Symptom:** Models download every time you run the app

**Check model cache location:**
```bash
dir "%USERPROFILE%\.cloudcall\models"
```

**If empty or missing:**
- Ensure you have write permissions to `%USERPROFILE%\.cloudcall\`
- Check antivirus isn't blocking file writes
- Try running application as administrator (once)

### Application Freezes During Transcription

**This is normal behavior:**
- UI may appear frozen during model loading
- Progress updates should appear after a few seconds
- First run takes longer (model download)

**If truly frozen (no response for >5 minutes):**
1. Check task manager - is Python using CPU/GPU?
2. Check log file: `%USERPROFILE%\.cloudcall\app.log`
3. Try with smaller audio file first
4. Try `whisper_model = "tiny"` for testing

## Getting More Help

### Enable Debug Logging

Edit `config/settings.toml`:
```toml
[logging]
log_level = "DEBUG"
```

Then check: `%USERPROFILE%\.cloudcall\app.log`

### Collect System Info

```bash
# GPU info
nvidia-smi

# Python packages
pip list > installed_packages.txt

# System info
systeminfo > system_info.txt
```

### Reset to Defaults

1. **Clear models** (will re-download):
   ```bash
   rmdir /s "%USERPROFILE%\.cloudcall\models"
   ```

2. **Reset config**:
   ```bash
   copy config\.env.example config\.env
   # Edit with your HuggingFace token
   ```

3. **Reinstall dependencies**:
   ```bash
   pip uninstall -y whisperx pyannote.audio
   pip install -r requirements.txt
   ```

## Performance Benchmarks

### Expected Transcription Speed

| Hardware | Model | Speed | VRAM Usage |
|----------|-------|-------|------------|
| RTX 4090 | base | 10x real-time | 2-3GB |
| RTX 4090 | small | 8x real-time | 3-4GB |
| RTX 4090 | medium | 5x real-time | 5-6GB |
| RTX 4090 | large-v2 | 3x real-time | 8-10GB |
| RTX 3060 | base | 5x real-time | 2-3GB |
| RTX 3060 | small | 3x real-time | 3-4GB |
| CPU (i7) | base | 0.5x real-time | N/A |

**Note:** "10x real-time" means a 1-minute audio file transcribes in ~6 seconds.

## Still Having Issues?

1. Check the log file: `%USERPROFILE%\.cloudcall\app.log`
2. Read the full documentation: [README.md](README.md)
3. Verify installation: [INSTALL.md](INSTALL.md)
4. Report bug with logs and system info

---

**Most issues are resolved by:**
1. ✅ Ensuring models can download (fixed in latest version)
2. ✅ Having valid HuggingFace token for diarization
3. ✅ Using appropriate model size for your GPU
4. ✅ Having internet connection on first run
