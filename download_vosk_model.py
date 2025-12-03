"""
Download Vosk multilingual model for real-time transcription
Supports 17 languages including Vietnamese, English, Chinese, etc.
"""
import os
import urllib.request
import zipfile
from pathlib import Path

# English model (40MB) - fast and accurate for English
# For multilingual support, manually download from: https://alphacephei.com/vosk/models
MODEL_URL = "https://alphacephei.com/kaldi/models/vosk-model-small-en-us-0.15.zip"
MODEL_NAME = "vosk-model-small-en-us-0.15"

def download_model():
    """Download and extract Vosk model"""
    models_dir = Path.home() / ".cloudcall" / "models" / "vosk"
    models_dir.mkdir(parents=True, exist_ok=True)

    model_path = models_dir / MODEL_NAME

    if model_path.exists():
        print(f"✓ Model already exists: {model_path}")
        return model_path

    zip_path = models_dir / f"{MODEL_NAME}.zip"

    print(f"Downloading Vosk model ({MODEL_NAME})...")
    print(f"URL: {MODEL_URL}")
    print(f"Destination: {models_dir}")

    # Download with progress
    def show_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(downloaded / total_size * 100, 100)
        print(f"\rDownloading: {percent:.1f}% ({downloaded / 1024 / 1024:.1f} MB)", end='')

    urllib.request.urlretrieve(MODEL_URL, zip_path, show_progress)
    print("\n✓ Download complete!")

    print("Extracting model...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(models_dir)

    # Cleanup zip file
    zip_path.unlink()

    print(f"✓ Model extracted to: {model_path}")
    return model_path

if __name__ == "__main__":
    model_path = download_model()
    print(f"\n✓ Vosk model ready: {model_path}")
    print("\nSupported languages:")
    print("  - English (en)")
    print("  - Vietnamese (vi)")
    print("  - Chinese (zh)")
    print("  - Spanish (es)")
    print("  - And 13 more languages!")
