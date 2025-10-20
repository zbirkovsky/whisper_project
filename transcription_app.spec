# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for CloudCall Transcription Application
"""
import os
import sys
from pathlib import Path

# Determine CUDA DLLs path - adjust to your environment
# Common locations:
# - Conda/Miniconda: C:\Users\YOUR_USER\miniconda3\envs\ENV_NAME\Library\bin
# - Standard CUDA: C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin
cuda_env = os.environ.get('CUDA_PATH', r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin')

# Essential CUDA DLLs for PyTorch
cuda_dlls = []
if os.path.exists(cuda_env):
    essential_dlls = [
        'cudart64_110.dll',
        'cublas64_11.dll',
        'cublasLt64_11.dll',
        'cudnn64_8.dll',
        'cudnn_cnn_infer64_8.dll',
        'cudnn_ops_infer64_8.dll',
    ]
    for dll in essential_dlls:
        dll_path = os.path.join(cuda_env, dll)
        if os.path.exists(dll_path):
            cuda_dlls.append((dll_path, '.'))

block_cipher = None

a = Analysis(
    ['transcription_app/main.py'],
    pathex=[],
    binaries=cuda_dlls,
    datas=[
        ('config', 'config'),
    ],
    hiddenimports=[
        # Core dependencies
        'torch',
        'torch._C',
        'torchaudio',
        'transformers',
        'whisperx',
        'faster_whisper',
        'pyannote.audio',
        'pyannote.core',
        'pyannote.database',
        'pyannote.metrics',

        # Audio processing
        'librosa',
        'soundfile',
        'pyaudiowpatch',

        # Scientific computing
        'numpy',
        'scipy',
        'scipy.signal',
        'scipy.ndimage',

        # ML dependencies
        'sklearn.utils._cython_blas',
        'sklearn.neighbors.typedefs',
        'sklearn.tree._utils',
        'sklearn.utils._weight_vector',

        # PySide6
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',

        # Configuration
        'pydantic',
        'pydantic_settings',
        'pydantic_core',
        'toml',
        'dotenv',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary packages to reduce size
        'tkinter',
        'matplotlib',
        'IPython',
        'jupyter',
        'notebook',
        'test',
        'tests',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CloudCallTranscription',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path if available: 'resources/icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CloudCallTranscription',
)
