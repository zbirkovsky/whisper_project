"""
CloudCall Transcription Application
Main entry point with proper initialization
"""
import sys
import warnings
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Suppress ctranslate2 pkg_resources deprecation warning (library issue, not ours)
warnings.filterwarnings('ignore', category=UserWarning, message='.*pkg_resources is deprecated.*')

from transcription_app.gui.main_window import MainWindow
from transcription_app.viewmodels.transcription_vm import TranscriptionViewModel
from transcription_app.core.transcription_engine import TranscriptionEngine
from transcription_app.core.audio_recorder import AudioRecorder
from transcription_app.utils.logger import setup_logging, get_logger
from transcription_app.utils.config import get_config

# Dependency injection imports
from transcription_app.core.service_container import get_service_container
from transcription_app.core.services import (
    IConfigService,
    ITranscriptionService,
    IExportService,
    IAudioFormatService,
    IAudioRecorderService
)
from transcription_app.core.service_implementations import (
    ConfigService,
    TranscriptionService,
    ExportService,
    AudioFormatService,
    AudioRecorderService
)
from transcription_app.core.audio_formats import get_audio_format_registry


def setup_services(config):
    """
    Setup dependency injection container with all application services

    Args:
        config: Application configuration

    Returns:
        Configured ServiceContainer
    """
    container = get_service_container()
    logger = get_logger(__name__)

    logger.info("Setting up service container...")

    # Register configuration service (singleton)
    container.register_instance(IConfigService, ConfigService(config))

    # Register audio format service (singleton)
    audio_format_registry = get_audio_format_registry()
    container.register_instance(IAudioFormatService, AudioFormatService(audio_format_registry))

    # Register export service (singleton)
    container.register_singleton(
        IExportService,
        lambda: ExportService(),
        lazy=True
    )

    # Register audio recorder service (singleton)
    container.register_singleton(
        IAudioRecorderService,
        lambda: AudioRecorderService(config),
        lazy=True
    )

    # Register transcription service (singleton with lazy loading for heavy model)
    container.register_singleton(
        ITranscriptionService,
        lambda: TranscriptionService(config),
        lazy=True
    )

    logger.info(f"Registered services: {', '.join(container.get_registered_services())}")
    return container


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
        # Setup dependency injection container
        container = setup_services(config)

        # Resolve services from container
        logger.info("Resolving services from container...")
        transcription_service = container.resolve(ITranscriptionService)
        audio_recorder_service = container.resolve(IAudioRecorderService)

        # Get underlying engines for backward compatibility
        transcription_engine = transcription_service.get_engine()
        audio_recorder = audio_recorder_service.get_recorder()

        # Apply default quality preset (gpu_balanced)
        logger.info("Applying default quality preset...")
        transcription_engine.apply_preset("gpu_balanced", override_device=True)

        # Create ViewModel (still using direct instances for now)
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
