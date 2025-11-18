"""
Audio processing utilities for gain boost and audio manipulation
"""
import numpy as np
from transcription_app.utils.logger import get_logger

logger = get_logger(__name__)


def calculate_and_apply_gain_boost(
    audio: np.ndarray,
    rms_threshold: float = 500.0,
    target_rms: float = 400.0,
    max_boost: float = 2.5,
    rms_floor: float = 100.0,
    use_soft_clipping: bool = True
) -> tuple[np.ndarray, float]:
    """
    Calculate and apply gain boost to audio if RMS is below threshold

    Args:
        audio: Audio data as int16 numpy array (mono)
        rms_threshold: RMS level below which to apply boost
        target_rms: Target RMS level to boost towards
        max_boost: Maximum boost factor to apply
        rms_floor: Minimum RMS value to prevent division by zero
        use_soft_clipping: Whether to apply soft clipping (tanh) to prevent distortion

    Returns:
        Tuple of (boosted audio array, boost factor applied)
    """
    # Calculate current RMS
    current_rms = np.sqrt(np.mean(audio**2))

    # Check if boost is needed
    if current_rms < rms_threshold:
        # Calculate boost needed to reach target RMS
        boost_factor = min(max_boost, target_rms / max(current_rms, rms_floor))
        logger.info(
            f"Applying microphone gain boost: {boost_factor:.2f}x "
            f"(RMS: {current_rms:.1f} -> {current_rms * boost_factor:.1f})"
        )

        if use_soft_clipping:
            # Apply boost with soft clipping to prevent distortion
            boosted = np.tanh(audio * boost_factor / 32767.0) * 32767.0
        else:
            # Simple multiplication boost
            boosted = audio * boost_factor

        return boosted, boost_factor
    else:
        # No boost needed
        return audio, 1.0


def calculate_rms(audio: np.ndarray) -> float:
    """
    Calculate RMS (Root Mean Square) level of audio

    Args:
        audio: Audio data as numpy array

    Returns:
        RMS level
    """
    return np.sqrt(np.mean(audio**2))


def stereo_to_mono(audio: np.ndarray) -> np.ndarray:
    """
    Convert stereo audio to mono by averaging left and right channels

    Args:
        audio: Stereo audio data as int16 numpy array (interleaved L/R)

    Returns:
        Mono audio data as int16 numpy array
    """
    left = audio[::2]
    right = audio[1::2]
    return np.array([left, right]).mean(axis=0)


def mix_audio_sources(
    source1: np.ndarray,
    source2: np.ndarray,
    source1_gain: float = 1.0,
    source2_gain: float = 1.0
) -> np.ndarray:
    """
    Mix two audio sources with optional gain adjustment

    Args:
        source1: First audio source as int16 numpy array
        source2: Second audio source as int16 numpy array
        source1_gain: Gain multiplier for source1 (default: 1.0)
        source2_gain: Gain multiplier for source2 (default: 1.0)

    Returns:
        Mixed audio clipped to int16 range
    """
    # Ensure same length
    min_len = min(len(source1), len(source2))
    source1 = source1[:min_len]
    source2 = source2[:min_len]

    # Apply gains and mix
    mixed = (source1 * source1_gain) + (source2 * source2_gain)

    # Clip to int16 range
    return np.clip(mixed, -32767, 32766).astype('int16')
