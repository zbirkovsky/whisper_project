"""
Tests for export strategies
"""
import tempfile
from pathlib import Path

import pytest


class TestPlainTextExportStrategy:
    """Tests for PlainTextExportStrategy"""

    def test_export_with_timestamps(self, sample_transcription_result, temp_dir):
        """Test plain text export with timestamps"""
        from transcription_app.core.export_strategies import PlainTextExportStrategy

        strategy = PlainTextExportStrategy(include_timestamps=True, include_speakers=True)
        output_path = temp_dir / 'transcript.txt'

        strategy.export(sample_transcription_result, output_path)

        assert output_path.exists()
        content = output_path.read_text(encoding='utf-8')

        # Should contain file info header
        assert 'test_audio.wav' in content
        assert 'Language: en' in content

        # Should contain timestamps
        assert '[0.00s]' in content or '[00:00' in content

        # Should contain speaker labels
        assert 'SPEAKER_00' in content
        assert 'SPEAKER_01' in content

        # Should contain text
        assert 'Hello, this is a test.' in content

    def test_export_without_timestamps(self, sample_transcription_result, temp_dir):
        """Test plain text export without timestamps"""
        from transcription_app.core.export_strategies import PlainTextExportStrategy

        strategy = PlainTextExportStrategy(include_timestamps=False, include_speakers=True)
        output_path = temp_dir / 'transcript.txt'

        strategy.export(sample_transcription_result, output_path)

        content = output_path.read_text(encoding='utf-8')

        # Should not contain timestamp format
        assert '[0.00s]' not in content

        # Should still have speakers
        assert 'SPEAKER_00' in content

    def test_export_without_speakers(self, sample_transcription_result, temp_dir):
        """Test plain text export without speaker labels"""
        from transcription_app.core.export_strategies import PlainTextExportStrategy

        strategy = PlainTextExportStrategy(include_timestamps=True, include_speakers=False)
        output_path = temp_dir / 'transcript.txt'

        strategy.export(sample_transcription_result, output_path)

        content = output_path.read_text(encoding='utf-8')

        # Should contain text without speaker prefix
        assert 'Hello, this is a test.' in content


class TestSRTExportStrategy:
    """Tests for SRTExportStrategy"""

    def test_export_srt_format(self, sample_transcription_result, temp_dir):
        """Test SRT export format"""
        from transcription_app.core.export_strategies import SRTExportStrategy

        strategy = SRTExportStrategy()
        output_path = temp_dir / 'transcript.srt'

        strategy.export(sample_transcription_result, output_path)

        assert output_path.exists()
        content = output_path.read_text(encoding='utf-8')

        # Should have subtitle indices
        assert '1\n' in content
        assert '2\n' in content

        # Should have proper timestamp format (HH:MM:SS,mmm --> HH:MM:SS,mmm)
        assert '-->' in content
        assert ':' in content
        assert ',' in content  # SRT uses comma for milliseconds

    def test_srt_timestamp_format(self, temp_dir):
        """Test SRT timestamp formatting"""
        from transcription_app.core.export_strategies import SRTExportStrategy

        strategy = SRTExportStrategy()

        result = {
            'file_name': 'test.wav',
            'language': 'en',
            'segments': [
                {'start': 0.0, 'end': 1.5, 'text': 'Test', 'speaker': 'S1'},
                {'start': 3661.123, 'end': 3665.456, 'text': 'Hour mark', 'speaker': 'S1'},
            ]
        }

        output_path = temp_dir / 'test.srt'
        strategy.export(result, output_path)

        content = output_path.read_text(encoding='utf-8')

        # First segment: 00:00:00,000 --> 00:00:01,500
        assert '00:00:00,000' in content
        assert '00:00:01,500' in content

        # Second segment at 1h 1m 1.123s: 01:01:01,123
        assert '01:01:01,123' in content


class TestVTTExportStrategy:
    """Tests for VTTExportStrategy"""

    def test_export_vtt_format(self, sample_transcription_result, temp_dir):
        """Test WebVTT export format"""
        from transcription_app.core.export_strategies import VTTExportStrategy

        strategy = VTTExportStrategy()
        output_path = temp_dir / 'transcript.vtt'

        strategy.export(sample_transcription_result, output_path)

        assert output_path.exists()
        content = output_path.read_text(encoding='utf-8')

        # Should have VTT header
        assert 'WEBVTT' in content

        # Should have proper timestamp format (HH:MM:SS.mmm --> HH:MM:SS.mmm)
        assert '-->' in content
        assert '.' in content  # VTT uses dot for milliseconds


class TestJSONExportStrategy:
    """Tests for JSONExportStrategy"""

    def test_export_json_format(self, sample_transcription_result, temp_dir):
        """Test JSON export format"""
        from transcription_app.core.export_strategies import JSONExportStrategy
        import json

        strategy = JSONExportStrategy()
        output_path = temp_dir / 'transcript.json'

        strategy.export(sample_transcription_result, output_path)

        assert output_path.exists()

        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert 'file_name' in data
        assert 'language' in data
        assert 'segments' in data
        assert len(data['segments']) == 3


class TestMarkdownExportStrategy:
    """Tests for MarkdownExportStrategy"""

    def test_export_markdown_format(self, sample_transcription_result, temp_dir):
        """Test Markdown export format"""
        from transcription_app.core.export_strategies import MarkdownExportStrategy

        strategy = MarkdownExportStrategy()
        output_path = temp_dir / 'transcript.md'

        strategy.export(sample_transcription_result, output_path)

        assert output_path.exists()
        content = output_path.read_text(encoding='utf-8')

        # Should have markdown header
        assert '#' in content

        # Should contain speaker labels (possibly as bold)
        assert 'SPEAKER_00' in content or '**SPEAKER_00**' in content


class TestTranscriptExporter:
    """Tests for the main TranscriptExporter class"""

    def test_export_auto_detect_format(self, sample_transcription_result, temp_dir):
        """Test format auto-detection from file extension"""
        from transcription_app.core.transcript_exporter import TranscriptExporter

        exporter = TranscriptExporter()

        # Export with .srt extension should use SRT format
        srt_path = temp_dir / 'test.srt'
        result = exporter.export(sample_transcription_result, srt_path)
        assert result == True
        assert srt_path.exists()
        assert '-->' in srt_path.read_text(encoding='utf-8')

    def test_export_explicit_format(self, sample_transcription_result, temp_dir):
        """Test explicit format specification"""
        from transcription_app.core.transcript_exporter import TranscriptExporter

        exporter = TranscriptExporter()

        # Export with wrong extension but correct format_id
        output_path = temp_dir / 'test.txt'
        result = exporter.export(sample_transcription_result, output_path, format_id='srt')
        assert result == True

    def test_export_multiple_formats(self, sample_transcription_result, temp_dir):
        """Test exporting to multiple formats"""
        from transcription_app.core.transcript_exporter import TranscriptExporter

        exporter = TranscriptExporter()
        base_path = temp_dir / 'transcript'

        results = exporter.export_multiple(
            sample_transcription_result,
            base_path,
            ['txt', 'srt', 'json']
        )

        assert results['txt'] == True
        assert results['srt'] == True
        assert results['json'] == True

        assert (temp_dir / 'transcript.txt').exists()
        assert (temp_dir / 'transcript.srt').exists()
        assert (temp_dir / 'transcript.json').exists()

    def test_available_formats(self):
        """Test getting available formats"""
        from transcription_app.core.transcript_exporter import TranscriptExporter

        exporter = TranscriptExporter()
        formats = exporter.available_formats()

        assert 'txt' in formats
        assert 'srt' in formats
        assert 'json' in formats
