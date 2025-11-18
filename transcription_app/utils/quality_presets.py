"""
Quality presets for transcription
Optimized configurations for different hardware and use cases
"""
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class QualityPreset:
    """Quality preset configuration"""
    name: str
    description: str
    device: str  # "cuda" or "cpu"
    compute_type: str  # "float32", "float16", "int8"
    batch_size: int
    asr_options: Dict[str, Any]
    vad_options: Dict[str, Any]


# Define presets
PRESETS = {
    "gpu_ultra": QualityPreset(
        name="GPU - Ultra Quality",
        description="Maximum accuracy, slower (RTX 4090/5090 recommended)",
        device="cuda",
        compute_type="float32",
        batch_size=24,
        asr_options={},  # WhisperX uses its own defaults, don't override
        vad_options={}
    ),

    "gpu_balanced": QualityPreset(
        name="GPU - Balanced",
        description="Good quality, fast (RTX 3060+ recommended)",
        device="cuda",
        compute_type="float16",
        batch_size=16,
        asr_options={},  # WhisperX uses its own defaults
        vad_options={}
    ),

    "gpu_fast": QualityPreset(
        name="GPU - Fast",
        description="Quick transcription, good enough (Any GPU)",
        device="cuda",
        compute_type="float16",
        batch_size=8,
        asr_options={},  # WhisperX uses its own defaults
        vad_options={}
    ),

    "cpu_optimized": QualityPreset(
        name="CPU - Optimized",
        description="For laptops without GPU (slow but works)",
        device="cpu",
        compute_type="int8",
        batch_size=4,
        asr_options={},  # WhisperX uses its own defaults
        vad_options={}
    ),
}


def get_preset(preset_id: str) -> QualityPreset:
    """Get preset by ID"""
    if preset_id not in PRESETS:
        # Default to balanced
        preset_id = "gpu_balanced"
    return PRESETS[preset_id]


def get_available_presets(has_gpu: bool = True) -> Dict[str, QualityPreset]:
    """Get available presets based on hardware"""
    if has_gpu:
        return PRESETS
    else:
        # Only return CPU preset if no GPU
        return {"cpu_optimized": PRESETS["cpu_optimized"]}


def get_preset_display_name(preset_id: str) -> str:
    """Get display name for preset"""
    preset = get_preset(preset_id)
    return preset.name
