"""
Language detection utility for intelligent model selection
Detects Czech vs English to choose appropriate whisper model
"""
import re
from typing import Optional
from transcription_app.utils.logger import get_logger

logger = get_logger(__name__)

# Czech-specific characters
CZECH_CHARS = set('áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ')

# Common Czech words for additional detection
CZECH_WORDS = {
    'schůze', 'schůzka', 'meeting', 'týden', 'den', 'projekt',
    'úkol', 'česky', 'český', 'čeština', 'Praha'
}


def detect_language_from_text(text: str) -> str:
    """
    Detect language from text (meeting title, filename, etc.)

    Args:
        text: Text to analyze

    Returns:
        Language code: 'cs' for Czech, 'en' for English, 'auto' for uncertain
    """
    if not text or len(text.strip()) < 2:
        return 'auto'

    text_lower = text.lower()

    # Check for Czech-specific characters
    czech_char_count = sum(1 for c in text if c in CZECH_CHARS)
    if czech_char_count >= 2:
        logger.debug(f"Detected Czech from characters in: {text[:50]}")
        return 'cs'

    # Check for common Czech words
    words = set(re.findall(r'\w+', text_lower))
    if words & CZECH_WORDS:
        logger.debug(f"Detected Czech from keywords in: {text[:50]}")
        return 'cs'

    # Try langdetect for longer text
    if len(text) > 10:
        try:
            from langdetect import detect, LangDetectException
            detected = detect(text)
            if detected == 'cs':
                logger.debug(f"langdetect identified Czech: {text[:50]}")
                return 'cs'
            elif detected == 'en':
                logger.debug(f"langdetect identified English: {text[:50]}")
                return 'en'
        except (LangDetectException, ImportError) as e:
            logger.debug(f"langdetect failed: {e}")

    # Default to auto if uncertain
    logger.debug(f"Could not determine language, using auto: {text[:50]}")
    return 'auto'


def get_best_model_for_language(language: str) -> str:
    """
    Get the best model for the detected language

    Args:
        language: Language code ('cs', 'en', 'auto')

    Returns:
        Model identifier for faster-whisper
    """
    if language == 'cs':
        # Check if Czech model exists, otherwise fall back to generic
        from pathlib import Path
        czech_model_path = Path.home() / '.cloudcall' / 'models' / 'whisper-large-v3-czech-cv13-ct2'
        if czech_model_path.exists():
            logger.info("Using Czech-specific model for better accuracy")
            return str(czech_model_path)
        else:
            logger.warning("Czech model not found, using generic large-v3")
            return 'large-v3'
    elif language == 'en':
        # Use turbo for English - faster with similar quality
        logger.info("Using turbo model for English")
        return 'large-v3-turbo'
    else:
        # Auto-detect - use generic model
        logger.info("Using generic large-v3 with auto-detection")
        return 'large-v3'


def detect_language_from_teams_meeting(meeting_name: Optional[str]) -> str:
    """
    Detect language from Teams meeting name

    Args:
        meeting_name: Teams meeting title

    Returns:
        Language code: 'cs', 'en', or 'auto'
    """
    if not meeting_name:
        return 'auto'

    return detect_language_from_text(meeting_name)
