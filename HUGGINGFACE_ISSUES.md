# HuggingFace Connection Issues

## What Just Happened

You encountered a **HuggingFace server error (500)** - this is a temporary issue on HuggingFace's side, not your application.

### The Error Message
```
500 Server Error: Internal Server Error for url:
https://huggingface.co/api/models/Systran/faster-whisper-base/revision/main

Internal Error - We're working hard to fix this as soon as possible!
```

## ✅ Fixes Applied

I've made **three improvements** to handle this better:

### 1. Enable Online Mode
```python
os.environ['HF_HUB_OFFLINE'] = '0'
```
This ensures the application can download models from HuggingFace.

### 2. Automatic Retry with Exponential Backoff
The app now retries 3 times if HuggingFace servers return errors:
- Attempt 1: Wait 1 second
- Attempt 2: Wait 2 seconds
- Attempt 3: Wait 4 seconds

### 3. Better Error Messages
If HuggingFace is down, you'll see:
```
HuggingFace servers are temporarily down. Please try again in a few minutes.
This is a temporary server issue, not a problem with the application.
```

## 🔄 What To Do Now

### Option 1: Wait and Retry (Recommended)
HuggingFace server issues usually resolve in 5-30 minutes.

1. **Wait 5-10 minutes**
2. **Restart the application**
3. **Try your transcription again**

### Option 2: Check HuggingFace Status
Visit: https://status.huggingface.co/

If there's an ongoing incident, wait for it to be resolved.

### Option 3: Use Pre-downloaded Models
If you have the models already downloaded elsewhere:

1. Copy model files to: `%USERPROFILE%\.cloudcall\models\`
2. Structure should be:
   ```
   .cloudcall\
   └── models\
       └── Systran\
           └── faster-whisper-base\
               ├── config.json
               ├── model.bin
               ├── tokenizer.json
               └── vocabulary.txt
   ```

## 🌐 Internet Connection Issues

### If You Have No Internet
The application **requires internet** for the first run to download models (~1-3GB).

**After first successful run:**
- Models are cached locally
- Internet not required for transcription
- Internet only needed for:
  - Speaker diarization (Pyannote models)
  - Alignment models (per language)

### Check Your Connection
```bash
# Test HuggingFace connectivity
curl -I https://huggingface.co

# Test DNS resolution
ping huggingface.co
```

### Behind Corporate Firewall?
Some corporate networks block HuggingFace. You may need:

1. **Proxy Configuration**:
   ```bash
   set HTTP_PROXY=http://your-proxy:port
   set HTTPS_PROXY=http://your-proxy:port
   ```

2. **Download models on home network**, then copy to work machine

3. **VPN**: Use company VPN if HuggingFace is blocked

## 📦 Manual Model Download

If automatic download keeps failing, download manually:

### Step 1: Download Models

Visit these URLs in browser:
- Base model: https://huggingface.co/Systran/faster-whisper-base
- Click "Files and versions" tab
- Download all files to a folder

### Step 2: Place in Cache

```bash
# Create directory
mkdir "%USERPROFILE%\.cache\huggingface\hub\models--Systran--faster-whisper-base\snapshots\main"

# Copy downloaded files there
```

### Step 3: Retry Application

The app should now find the cached models.

## 🔍 Verify Model Location

After successful download, verify:

```bash
# List cached models
dir "%USERPROFILE%\.cache\huggingface\hub" /s
```

Expected structure:
```
hub\
├── models--Systran--faster-whisper-base\
│   └── snapshots\
│       └── main\
│           ├── config.json
│           ├── model.bin
│           └── ...
```

## ⚙️ Configuration Options

### Use Different Model Source

If HuggingFace continues having issues, you can use local models:

Edit `config/settings.toml`:
```toml
[transcription]
whisper_model = "/path/to/local/model"  # Use local path
```

### Disable Automatic Downloads

If you want to use only pre-cached models:

```python
# In main.py or as environment variable
import os
os.environ['HF_HUB_OFFLINE'] = '1'  # Disable downloads
```

## 🐛 Still Having Issues?

### Check the Log
```bash
type "%USERPROFILE%\.cloudcall\app.log"
```

Look for:
- Connection errors
- Timeout errors
- Authentication errors
- Disk space errors

### Common Solutions

1. **Disk Space**: Ensure you have 5GB+ free space
2. **Antivirus**: May block downloads - add exception
3. **Windows Firewall**: Allow Python/application
4. **VPN/Proxy**: May interfere with downloads
5. **DNS Issues**: Try `8.8.8.8` (Google DNS)

### Test Connection Manually

```python
# Test script: test_huggingface.py
import requests

try:
    response = requests.get("https://huggingface.co/api/models/Systran/faster-whisper-base")
    print(f"Status: {response.status_code}")
    print(f"Connection: OK" if response.status_code == 200 else "FAILED")
except Exception as e:
    print(f"Error: {e}")
```

Run:
```bash
python test_huggingface.py
```

## 📊 Current Status

Based on your error, HuggingFace had a **500 Internal Server Error** when you tried.

This means:
- ✅ Your application is configured correctly
- ✅ Your internet connection works
- ❌ HuggingFace servers were temporarily down

**Solution**: Wait and retry in 10-30 minutes.

## 🚀 Quick Retry Guide

1. Close the application
2. Wait 10 minutes
3. Restart:
   ```bash
   run.bat
   ```
4. Drop your file again
5. Watch for "Loading models..." progress

## 💡 Pro Tips

1. **First Run**: Do it during off-peak hours (late evening/early morning)
2. **Stable Connection**: Use wired connection for initial download
3. **Models Cache**: Keep `%USERPROFILE%\.cloudcall\models\` backed up
4. **Monitor**: Watch Task Manager for download progress (network activity)

---

**The application now has retry logic built-in, so temporary HuggingFace errors will be handled automatically!**
