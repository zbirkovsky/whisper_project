"""
Translation service using Google Translate (via deep-translator)
Provides real-time translation for transcribed text
"""
import time
from typing import Optional
from deep_translator import GoogleTranslator
from transcription_app.utils.logger import get_logger

logger = get_logger(__name__)


class TranslationService:
    """Handles text translation using Google Translate"""

    def __init__(self, target_language: str = "en"):
        """
        Initialize translation service

        Args:
            target_language: Target language code (default: 'en' for English)
        """
        self.target_language = target_language
        self.translator_cache = {}  # Cache translators for each source language
        logger.info(f"TranslationService initialized with target language: {target_language}")

    def translate(
        self,
        text: str,
        source_language: str = "auto",
        target_language: Optional[str] = None
    ) -> str:
        """
        Translate text from source language to target language

        Args:
            text: Text to translate
            source_language: Source language code ('auto' for auto-detection, 'vi' for Vietnamese, etc.)
            target_language: Target language code (if None, uses instance default)

        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text

        target = target_language or self.target_language

        # Skip translation if source and target are the same
        if source_language == target and source_language != "auto":
            return text

        # Get or create translator for this language pair
        cache_key = f"{source_language}->{target}"
        if cache_key not in self.translator_cache:
            logger.debug(f"Creating new translator: {cache_key}")
            self.translator_cache[cache_key] = GoogleTranslator(
                source=source_language,
                target=target
            )

        translator = self.translator_cache[cache_key]

        # Retry logic with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                translated = translator.translate(text)
                logger.debug(f"Translated ({source_language}->{target}): '{text[:50]}...' -> '{translated[:50]}...'")
                return translated

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    logger.warning(
                        f"Translation attempt {attempt + 1}/{max_retries} failed: {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Translation failed after {max_retries} attempts: {e}")
                    # Return original text if all retries fail
                    return text

        # Fallback (should not reach here)
        return text

    def translate_segments(
        self,
        segments: list,
        source_language: str = "auto",
        target_language: Optional[str] = None
    ) -> list:
        """
        Translate all segments from transcription result

        Args:
            segments: List of transcription segments (each with 'text' field)
            source_language: Source language code
            target_language: Target language code (if None, uses instance default)

        Returns:
            List of segments with added 'translated_text' field
        """
        target = target_language or self.target_language
        translated_segments = []

        for segment in segments:
            translated_segment = segment.copy()
            original_text = segment.get('text', '').strip()

            if original_text:
                translated_text = self.translate(
                    original_text,
                    source_language=source_language,
                    target_language=target
                )
                translated_segment['translated_text'] = translated_text
                translated_segment['translation_target'] = target
                translated_segment['translation_source'] = source_language
            else:
                translated_segment['translated_text'] = original_text

            translated_segments.append(translated_segment)

        logger.info(f"Translated {len(translated_segments)} segments")
        return translated_segments

    def clear_cache(self):
        """Clear translator cache"""
        self.translator_cache.clear()
        logger.info("Translation cache cleared")


# Convenience function for quick translations
def translate_text(text: str, source: str = "auto", target: str = "en") -> str:
    """
    Quick translation function

    Args:
        text: Text to translate
        source: Source language code ('auto', 'vi', 'zh', etc.)
        target: Target language code ('en', 'vi', etc.)

    Returns:
        Translated text
    """
    service = TranslationService(target_language=target)
    return service.translate(text, source_language=source)
