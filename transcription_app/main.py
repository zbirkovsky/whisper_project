"""
CloudCall Transcription Application
Main entry point with proper initialization
"""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from transcription_app.gui.main_window import MainWindow
from transcription_app.viewmodels.transcription_vm import TranscriptionViewModel
from transcription_app.core.transcription_engine import TranscriptionEngine
from transcription_app.core.audio_recorder import AudioRecorder
from transcription_app.utils.logger import setup_logging, get_logger
from transcription_app.utils.config import get_config


def main():
    """Main application entry point"""
    # Enable High DPI scaling (these are automatic in Qt 6, but keep for compatibility)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    # Note: AA_EnableHighDpiScaling and AA_UseHighDpiPixmaps are deprecated in Qt 6
    # and enabled by default, so we don't need to set them

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("CloudCall Transcription")
    app.setOrganizationName("CloudCall")

    # Load configuration
    config = get_config()

    # Setup logging
    setup_logging(
        log_file=config.log_file,
        log_level=config.log_level,
        max_bytes=config.get_max_log_bytes(),
        backup_count=config.backup_count
    )

    logger = get_logger(__name__)
    logger.info("=" * 60)
    logger.info("CloudCall Transcription Application Starting")
    logger.info("=" * 60)
    logger.info(f"App directory: {config.app_dir}")
    logger.info(f"Models directory: {config.models_dir}")
    logger.info(f"Device: {config.device}")
    logger.info(f"Whisper model: {config.whisper_model}")

    try:
        # Initialize core components
        logger.info("Initializing transcription engine...")
        transcription_engine = TranscriptionEngine(config)

        logger.info("Initializing audio recorder...")
        audio_recorder = AudioRecorder(config)

        # Create ViewModel
        logger.info("Creating ViewModel...")
        viewmodel = TranscriptionViewModel(transcription_engine, audio_recorder)

        # Create and show main window
        logger.info("Creating main window...")
        window = MainWindow(viewmodel, config)
        window.show()

        logger.info("Application started successfully")

        # Run application
        exit_code = app.exec()

        logger.info(f"Application exiting with code: {exit_code}")
        return exit_code

    except Exception as e:
        logger.error(f"Application startup failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
