"""
Audio format handling abstractions
Provides extensible support for different audio file formats
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np
from transcription_app.utils.logger import get_logger

logger = get_logger(__name__)


class AudioFormatHandler(ABC):
    """Abstract base class for audio format handlers"""

    @abstractmethod
    def can_handle(self, file_path: Path) -> bool:
        """
        Check if this handler can process the given file

        Args:
            file_path: Path to audio file

        Returns:
            True if handler supports this format
        """
        pass

    @abstractmethod
    def load_audio(self, file_path: Path) -> np.ndarray:
        """
        Load audio file and return as numpy array

        Args:
            file_path: Path to audio file

        Returns:
            Audio data as numpy array (mono, float32, normalized to [-1, 1])
        """
        pass

    @abstractmethod
    def get_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from audio file

        Args:
            file_path: Path to audio file

        Returns:
            Dictionary with metadata (sample_rate, channels, duration, etc.)
        """
        pass

    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """
        Get list of supported file extensions

        Returns:
            List of extensions (e.g., ['.wav', '.wave'])
        """
        pass


class WAVFormatHandler(AudioFormatHandler):
    """Handler for WAV audio files"""

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions()

    def load_audio(self, file_path: Path) -> np.ndarray:
        """Load WAV file using wave module"""
        import wave

        with wave.open(str(file_path), 'rb') as wf:
            sample_rate = wf.getframerate()
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            frames = wf.readframes(wf.getnframes())

        # Convert to numpy array
        if sampwidth == 2:  # 16-bit PCM
            audio = np.frombuffer(frames, dtype=np.int16)
            audio = audio.astype(np.float32) / 32768.0
        elif sampwidth == 3:  # 24-bit PCM
            # Convert 24-bit to 32-bit then normalize
            audio = np.frombuffer(frames, dtype=np.uint8)
            audio = audio.reshape(-1, 3)
            audio = np.pad(audio, ((0, 0), (0, 1)), mode='constant')
            audio = audio.view(np.int32).astype(np.float32) / 2147483648.0
        elif sampwidth == 4:  # 32-bit PCM
            audio = np.frombuffer(frames, dtype=np.int32)
            audio = audio.astype(np.float32) / 2147483648.0
        else:
            raise ValueError(f"Unsupported sample width: {sampwidth}")

        # Convert stereo to mono if needed
        if n_channels == 2:
            audio = audio.reshape(-1, 2).mean(axis=1)
        elif n_channels > 2:
            audio = audio.reshape(-1, n_channels).mean(axis=1)

        return audio

    def get_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract WAV metadata"""
        import wave

        with wave.open(str(file_path), 'rb') as wf:
            return {
                'sample_rate': wf.getframerate(),
                'channels': wf.getnchannels(),
                'sample_width': wf.getsampwidth(),
                'n_frames': wf.getnframes(),
                'duration': wf.getnframes() / wf.getframerate(),
                'format': 'WAV'
            }

    def supported_extensions(self) -> list[str]:
        return ['.wav', '.wave']


class MP3FormatHandler(AudioFormatHandler):
    """Handler for MP3 audio files using pydub"""

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions()

    def load_audio(self, file_path: Path) -> np.ndarray:
        """Load MP3 file using pydub"""
        try:
            from pydub import AudioSegment
        except ImportError:
            raise ImportError(
                "pydub is required for MP3 support. "
                "Install with: pip install pydub"
            )

        audio_segment = AudioSegment.from_mp3(str(file_path))

        # Convert to mono
        if audio_segment.channels > 1:
            audio_segment = audio_segment.set_channels(1)

        # Convert to numpy array
        samples = np.array(audio_segment.get_array_of_samples())

        # Normalize based on sample width
        if audio_segment.sample_width == 2:
            samples = samples.astype(np.float32) / 32768.0
        elif audio_segment.sample_width == 4:
            samples = samples.astype(np.float32) / 2147483648.0
        else:
            samples = samples.astype(np.float32) / (2 ** (8 * audio_segment.sample_width - 1))

        return samples

    def get_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract MP3 metadata"""
        try:
            from pydub import AudioSegment
        except ImportError:
            raise ImportError("pydub is required for MP3 support")

        audio_segment = AudioSegment.from_mp3(str(file_path))

        return {
            'sample_rate': audio_segment.frame_rate,
            'channels': audio_segment.channels,
            'sample_width': audio_segment.sample_width,
            'duration': len(audio_segment) / 1000.0,  # Convert ms to seconds
            'format': 'MP3'
        }

    def supported_extensions(self) -> list[str]:
        return ['.mp3']


class M4AFormatHandler(AudioFormatHandler):
    """Handler for M4A/AAC audio files using pydub"""

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions()

    def load_audio(self, file_path: Path) -> np.ndarray:
        """Load M4A file using pydub"""
        try:
            from pydub import AudioSegment
        except ImportError:
            raise ImportError("pydub is required for M4A support")

        # Try different loaders
        try:
            audio_segment = AudioSegment.from_file(str(file_path), format='m4a')
        except:
            # Fallback to generic loader
            audio_segment = AudioSegment.from_file(str(file_path))

        # Convert to mono
        if audio_segment.channels > 1:
            audio_segment = audio_segment.set_channels(1)

        # Convert to numpy array
        samples = np.array(audio_segment.get_array_of_samples())

        # Normalize
        if audio_segment.sample_width == 2:
            samples = samples.astype(np.float32) / 32768.0
        elif audio_segment.sample_width == 4:
            samples = samples.astype(np.float32) / 2147483648.0
        else:
            samples = samples.astype(np.float32) / (2 ** (8 * audio_segment.sample_width - 1))

        return samples

    def get_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract M4A metadata"""
        try:
            from pydub import AudioSegment
        except ImportError:
            raise ImportError("pydub is required for M4A support")

        try:
            audio_segment = AudioSegment.from_file(str(file_path), format='m4a')
        except:
            audio_segment = AudioSegment.from_file(str(file_path))

        return {
            'sample_rate': audio_segment.frame_rate,
            'channels': audio_segment.channels,
            'sample_width': audio_segment.sample_width,
            'duration': len(audio_segment) / 1000.0,
            'format': 'M4A'
        }

    def supported_extensions(self) -> list[str]:
        return ['.m4a', '.aac', '.mp4']


class FLACFormatHandler(AudioFormatHandler):
    """Handler for FLAC audio files using pydub"""

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions()

    def load_audio(self, file_path: Path) -> np.ndarray:
        """Load FLAC file using pydub"""
        try:
            from pydub import AudioSegment
        except ImportError:
            raise ImportError("pydub is required for FLAC support")

        audio_segment = AudioSegment.from_file(str(file_path), format='flac')

        # Convert to mono
        if audio_segment.channels > 1:
            audio_segment = audio_segment.set_channels(1)

        # Convert to numpy array
        samples = np.array(audio_segment.get_array_of_samples())

        # Normalize
        if audio_segment.sample_width == 2:
            samples = samples.astype(np.float32) / 32768.0
        elif audio_segment.sample_width == 3:
            samples = samples.astype(np.float32) / 8388608.0  # 24-bit
        elif audio_segment.sample_width == 4:
            samples = samples.astype(np.float32) / 2147483648.0
        else:
            samples = samples.astype(np.float32) / (2 ** (8 * audio_segment.sample_width - 1))

        return samples

    def get_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract FLAC metadata"""
        try:
            from pydub import AudioSegment
        except ImportError:
            raise ImportError("pydub is required for FLAC support")

        audio_segment = AudioSegment.from_file(str(file_path), format='flac')

        return {
            'sample_rate': audio_segment.frame_rate,
            'channels': audio_segment.channels,
            'sample_width': audio_segment.sample_width,
            'duration': len(audio_segment) / 1000.0,
            'format': 'FLAC'
        }

    def supported_extensions(self) -> list[str]:
        return ['.flac']


class AudioFormatRegistry:
    """Registry for audio format handlers"""

    def __init__(self):
        self.handlers: list[AudioFormatHandler] = []
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register built-in format handlers"""
        self.register(WAVFormatHandler())
        self.register(MP3FormatHandler())
        self.register(M4AFormatHandler())
        self.register(FLACFormatHandler())

    def register(self, handler: AudioFormatHandler):
        """
        Register a new format handler

        Args:
            handler: AudioFormatHandler instance
        """
        self.handlers.append(handler)
        logger.info(f"Registered handler: {handler.__class__.__name__} for {handler.supported_extensions()}")

    def get_handler(self, file_path: Path) -> Optional[AudioFormatHandler]:
        """
        Get appropriate handler for file

        Args:
            file_path: Path to audio file

        Returns:
            Handler instance or None if no handler found
        """
        for handler in self.handlers:
            if handler.can_handle(file_path):
                logger.debug(f"Selected handler: {handler.__class__.__name__} for {file_path.suffix}")
                return handler

        logger.warning(f"No handler found for file: {file_path}")
        return None

    def supported_extensions(self) -> list[str]:
        """
        Get list of all supported extensions

        Returns:
            List of supported file extensions
        """
        extensions = []
        for handler in self.handlers:
            extensions.extend(handler.supported_extensions())
        return sorted(set(extensions))


# Global registry instance
_registry: Optional[AudioFormatRegistry] = None


def get_audio_format_registry() -> AudioFormatRegistry:
    """Get or create global audio format registry"""
    global _registry
    if _registry is None:
        _registry = AudioFormatRegistry()
    return _registry
