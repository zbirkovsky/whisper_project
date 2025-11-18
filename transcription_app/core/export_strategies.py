"""
Export strategy abstractions for transcription output
Provides extensible support for different export formats
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import timedelta
from transcription_app.utils.logger import get_logger

logger = get_logger(__name__)


class ExportStrategy(ABC):
    """Abstract base class for transcript export strategies"""

    @abstractmethod
    def export(self, result: Dict[str, Any], output_path: Path) -> bool:
        """
        Export transcription result to file

        Args:
            result: Transcription result dictionary
            output_path: Path to save exported file

        Returns:
            True if export successful
        """
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """
        Get file extension for this export format

        Returns:
            File extension (e.g., '.txt', '.srt')
        """
        pass

    @abstractmethod
    def get_format_name(self) -> str:
        """
        Get human-readable format name

        Returns:
            Format name (e.g., 'Plain Text', 'SRT Subtitles')
        """
        pass


class PlainTextExportStrategy(ExportStrategy):
    """Export transcription as plain text"""

    def __init__(self, include_timestamps: bool = True, include_speakers: bool = True):
        """
        Args:
            include_timestamps: Include timestamp markers
            include_speakers: Include speaker labels
        """
        self.include_timestamps = include_timestamps
        self.include_speakers = include_speakers

    def export(self, result: Dict[str, Any], output_path: Path) -> bool:
        """Export as plain text file"""
        try:
            lines = []

            # Add header
            file_name = result.get('file_name', 'Unknown')
            language = result.get('language', 'unknown')
            lines.append(f"=== Transcription: {file_name} ===")
            lines.append(f"Language: {language}")
            lines.append("")

            # Format segments
            for segment in result.get('segments', []):
                speaker = segment.get('speaker', 'Unknown') if self.include_speakers else ''
                start = segment.get('start', 0)
                text_content = segment.get('text', '').strip()

                if self.include_timestamps and self.include_speakers:
                    timestamp = f"[{start:.2f}s]"
                    lines.append(f"{timestamp} {speaker}: {text_content}")
                elif self.include_timestamps:
                    timestamp = f"[{start:.2f}s]"
                    lines.append(f"{timestamp} {text_content}")
                elif self.include_speakers:
                    lines.append(f"{speaker}: {text_content}")
                else:
                    lines.append(text_content)

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            logger.info(f"Exported plain text to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting plain text: {e}", exc_info=True)
            return False

    def get_file_extension(self) -> str:
        return '.txt'

    def get_format_name(self) -> str:
        return 'Plain Text'


class SRTExportStrategy(ExportStrategy):
    """Export transcription as SRT subtitle file"""

    def export(self, result: Dict[str, Any], output_path: Path) -> bool:
        """Export as SRT subtitle file"""
        try:
            lines = []
            subtitle_index = 1

            for segment in result.get('segments', []):
                start = segment.get('start', 0)
                end = segment.get('end', start + 1)
                text_content = segment.get('text', '').strip()
                speaker = segment.get('speaker', '')

                # Format timestamps as SRT time format (HH:MM:SS,mmm)
                start_time = self._format_srt_time(start)
                end_time = self._format_srt_time(end)

                # Add speaker prefix if available
                if speaker:
                    text_content = f"{speaker}: {text_content}"

                lines.append(str(subtitle_index))
                lines.append(f"{start_time} --> {end_time}")
                lines.append(text_content)
                lines.append("")  # Blank line between subtitles

                subtitle_index += 1

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            logger.info(f"Exported SRT to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting SRT: {e}", exc_info=True)
            return False

    @staticmethod
    def _format_srt_time(seconds: float) -> str:
        """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def get_file_extension(self) -> str:
        return '.srt'

    def get_format_name(self) -> str:
        return 'SRT Subtitles'


class VTTExportStrategy(ExportStrategy):
    """Export transcription as WebVTT subtitle file"""

    def export(self, result: Dict[str, Any], output_path: Path) -> bool:
        """Export as WebVTT file"""
        try:
            lines = ['WEBVTT', '']

            for segment in result.get('segments', []):
                start = segment.get('start', 0)
                end = segment.get('end', start + 1)
                text_content = segment.get('text', '').strip()
                speaker = segment.get('speaker', '')

                # Format timestamps as WebVTT time format (HH:MM:SS.mmm)
                start_time = self._format_vtt_time(start)
                end_time = self._format_vtt_time(end)

                # Add speaker prefix if available
                if speaker:
                    text_content = f"<v {speaker}>{text_content}"

                lines.append(f"{start_time} --> {end_time}")
                lines.append(text_content)
                lines.append("")  # Blank line between cues

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            logger.info(f"Exported VTT to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting VTT: {e}", exc_info=True)
            return False

    @staticmethod
    def _format_vtt_time(seconds: float) -> str:
        """Convert seconds to WebVTT time format (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

    def get_file_extension(self) -> str:
        return '.vtt'

    def get_format_name(self) -> str:
        return 'WebVTT Subtitles'


class JSONExportStrategy(ExportStrategy):
    """Export transcription as JSON file"""

    def __init__(self, pretty: bool = True):
        """
        Args:
            pretty: Use pretty-printed JSON formatting
        """
        self.pretty = pretty

    def export(self, result: Dict[str, Any], output_path: Path) -> bool:
        """Export as JSON file"""
        try:
            import json

            with open(output_path, 'w', encoding='utf-8') as f:
                if self.pretty:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(result, f, ensure_ascii=False)

            logger.info(f"Exported JSON to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting JSON: {e}", exc_info=True)
            return False

    def get_file_extension(self) -> str:
        return '.json'

    def get_format_name(self) -> str:
        return 'JSON'


class MarkdownExportStrategy(ExportStrategy):
    """Export transcription as Markdown file"""

    def export(self, result: Dict[str, Any], output_path: Path) -> bool:
        """Export as Markdown file"""
        try:
            lines = []

            # Add header
            file_name = result.get('file_name', 'Unknown')
            language = result.get('language', 'unknown')
            lines.append(f"# Transcription: {file_name}")
            lines.append("")
            lines.append(f"**Language:** {language}")
            lines.append("")
            lines.append("---")
            lines.append("")

            # Group by speaker for cleaner markdown
            current_speaker = None
            speaker_lines = []

            for segment in result.get('segments', []):
                speaker = segment.get('speaker', 'Unknown')
                start = segment.get('start', 0)
                text_content = segment.get('text', '').strip()

                if speaker != current_speaker:
                    # Write previous speaker's content
                    if current_speaker and speaker_lines:
                        lines.append(f"## {current_speaker}")
                        lines.append("")
                        lines.append(' '.join(speaker_lines))
                        lines.append("")
                        speaker_lines = []

                    current_speaker = speaker

                speaker_lines.append(text_content)

            # Write last speaker's content
            if current_speaker and speaker_lines:
                lines.append(f"## {current_speaker}")
                lines.append("")
                lines.append(' '.join(speaker_lines))
                lines.append("")

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            logger.info(f"Exported Markdown to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting Markdown: {e}", exc_info=True)
            return False

    def get_file_extension(self) -> str:
        return '.md'

    def get_format_name(self) -> str:
        return 'Markdown'


class ExportStrategyRegistry:
    """Registry for export strategies"""

    def __init__(self):
        self.strategies: Dict[str, ExportStrategy] = {}
        self._register_default_strategies()

    def _register_default_strategies(self):
        """Register built-in export strategies"""
        self.register('txt', PlainTextExportStrategy())
        self.register('srt', SRTExportStrategy())
        self.register('vtt', VTTExportStrategy())
        self.register('json', JSONExportStrategy())
        self.register('md', MarkdownExportStrategy())

    def register(self, format_id: str, strategy: ExportStrategy):
        """
        Register a new export strategy

        Args:
            format_id: Unique identifier for format (e.g., 'txt', 'srt')
            strategy: ExportStrategy instance
        """
        self.strategies[format_id] = strategy
        logger.info(f"Registered export strategy: {format_id} ({strategy.get_format_name()})")

    def get_strategy(self, format_id: str) -> Optional[ExportStrategy]:
        """
        Get export strategy by ID

        Args:
            format_id: Format identifier

        Returns:
            Strategy instance or None
        """
        return self.strategies.get(format_id)

    def available_formats(self) -> Dict[str, str]:
        """
        Get available export formats

        Returns:
            Dictionary mapping format_id to format_name
        """
        return {
            format_id: strategy.get_format_name()
            for format_id, strategy in self.strategies.items()
        }


# Global registry instance
_export_registry: Optional[ExportStrategyRegistry] = None


def get_export_strategy_registry() -> ExportStrategyRegistry:
    """Get or create global export strategy registry"""
    global _export_registry
    if _export_registry is None:
        _export_registry = ExportStrategyRegistry()
    return _export_registry
