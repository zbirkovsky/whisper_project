"""
Tests for the translation service
"""
from unittest.mock import patch, MagicMock

import pytest


class TestTranslationService:
    """Tests for TranslationService class"""

    def test_translate_empty_string(self):
        """Test translation of empty string returns empty string"""
        from transcription_app.utils.translator import TranslationService

        service = TranslationService(target_language='en')
        result = service.translate('')
        assert result == ''

    def test_translate_whitespace_string(self):
        """Test translation of whitespace returns whitespace"""
        from transcription_app.utils.translator import TranslationService

        service = TranslationService(target_language='en')
        result = service.translate('   ')
        assert result == '   '

    def test_skip_translation_same_language(self):
        """Test that same source and target language skips translation"""
        from transcription_app.utils.translator import TranslationService

        service = TranslationService(target_language='en')
        text = 'Hello world'

        # When source and target are the same, should return original
        result = service.translate(text, source_language='en', target_language='en')
        assert result == text

    def test_translator_caching(self):
        """Test that translators are cached for reuse"""
        from transcription_app.utils.translator import TranslationService

        service = TranslationService(target_language='en')

        with patch('transcription_app.utils.translator.GoogleTranslator') as mock_translator:
            mock_instance = MagicMock()
            mock_instance.translate.return_value = 'translated'
            mock_translator.return_value = mock_instance

            # First translation should create translator
            service.translate('Ahoj', source_language='cs')
            assert mock_translator.call_count == 1

            # Second translation with same language pair should reuse
            service.translate('Svět', source_language='cs')
            assert mock_translator.call_count == 1  # Still 1

            # Different language pair should create new translator
            service.translate('Bonjour', source_language='fr')
            assert mock_translator.call_count == 2

    def test_translate_fallback_on_error(self):
        """Test that translation returns original on error"""
        from transcription_app.utils.translator import TranslationService

        service = TranslationService(target_language='en')

        with patch('transcription_app.utils.translator.GoogleTranslator') as mock_translator:
            mock_instance = MagicMock()
            mock_instance.translate.side_effect = Exception('Network error')
            mock_translator.return_value = mock_instance

            text = 'Ahoj svět'
            result = service.translate(text, source_language='cs')

            # Should return original text on error
            assert result == text

    def test_translate_segments(self):
        """Test translation of multiple segments"""
        from transcription_app.utils.translator import TranslationService

        service = TranslationService(target_language='en')

        segments = [
            {'start': 0.0, 'end': 1.0, 'text': 'Hello'},
            {'start': 1.0, 'end': 2.0, 'text': 'World'},
        ]

        with patch.object(service, 'translate', return_value='Translated'):
            result = service.translate_segments(segments, source_language='cs')

            assert len(result) == 2
            assert all('translated_text' in seg for seg in result)
            assert all(seg['translated_text'] == 'Translated' for seg in result)

    def test_translate_segments_preserves_other_fields(self):
        """Test that segment translation preserves other fields"""
        from transcription_app.utils.translator import TranslationService

        service = TranslationService(target_language='en')

        segments = [
            {'start': 0.0, 'end': 1.0, 'text': 'Hello', 'speaker': 'SPEAKER_00'},
        ]

        with patch.object(service, 'translate', return_value='Ahoj'):
            result = service.translate_segments(segments, source_language='en', target_language='cs')

            assert result[0]['start'] == 0.0
            assert result[0]['end'] == 1.0
            assert result[0]['speaker'] == 'SPEAKER_00'
            assert result[0]['text'] == 'Hello'  # Original preserved
            assert result[0]['translated_text'] == 'Ahoj'

    def test_clear_cache(self):
        """Test cache clearing"""
        from transcription_app.utils.translator import TranslationService

        service = TranslationService(target_language='en')

        with patch('transcription_app.utils.translator.GoogleTranslator') as mock_translator:
            mock_instance = MagicMock()
            mock_instance.translate.return_value = 'translated'
            mock_translator.return_value = mock_instance

            service.translate('test', source_language='cs')
            assert len(service.translator_cache) == 1

            service.clear_cache()
            assert len(service.translator_cache) == 0


class TestTranslateTextFunction:
    """Tests for the translate_text convenience function"""

    def test_translate_text_quick_translation(self):
        """Test quick translation function"""
        from transcription_app.utils.translator import translate_text

        with patch('transcription_app.utils.translator.GoogleTranslator') as mock_translator:
            mock_instance = MagicMock()
            mock_instance.translate.return_value = 'Hello'
            mock_translator.return_value = mock_instance

            result = translate_text('Ahoj', source='cs', target='en')
            assert result == 'Hello'

    def test_translate_text_default_params(self):
        """Test quick translation with default parameters"""
        from transcription_app.utils.translator import translate_text

        with patch('transcription_app.utils.translator.GoogleTranslator') as mock_translator:
            mock_instance = MagicMock()
            mock_instance.translate.return_value = 'Translated'
            mock_translator.return_value = mock_instance

            result = translate_text('Test')  # source='auto', target='en'

            mock_translator.assert_called_once_with(source='auto', target='en')
