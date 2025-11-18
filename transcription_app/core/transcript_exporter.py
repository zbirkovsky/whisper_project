"""
High-level transcript exporter using pluggable export strategies
"""
from pathlib import Path
from typing import Dict, Any, Optional
from transcription_app.core.export_strategies import get_export_strategy_registry
from transcription_app.utils.logger import get_logger

logger = get_logger(__name__)


class TranscriptExporter:
    """
    Manages transcript export operations using pluggable strategies
    """

    def __init__(self):
        self.registry = get_export_strategy_registry()

    def export(
        self,
        result: Dict[str, Any],
        output_path: Path,
        format_id: Optional[str] = None
    ) -> bool:
        """
        Export transcription result to file

        Args:
            result: Transcription result dictionary
            output_path: Path to save exported file
            format_id: Export format ID (inferred from extension if None)

        Returns:
            True if export successful

        Raises:
            ValueError: If format is not supported
        """
        # Infer format from extension if not specified
        if format_id is None:
            extension = output_path.suffix.lstrip('.')
            format_id = extension

        # Get appropriate strategy
        strategy = self.registry.get_strategy(format_id)
        if strategy is None:
            available = ', '.join(self.registry.available_formats().keys())
            raise ValueError(
                f"Unsupported export format: {format_id}. "
                f"Available formats: {available}"
            )

        # Ensure output path has correct extension
        expected_ext = strategy.get_file_extension()
        if output_path.suffix != expected_ext:
            logger.warning(
                f"Output path extension '{output_path.suffix}' doesn't match "
                f"format extension '{expected_ext}'. Using format extension."
            )
            output_path = output_path.with_suffix(expected_ext)

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Export using strategy
        logger.info(f"Exporting transcript as {strategy.get_format_name()} to: {output_path}")
        success = strategy.export(result, output_path)

        if success:
            logger.info(f"Export successful: {output_path}")
        else:
            logger.error(f"Export failed: {output_path}")

        return success

    def export_multiple(
        self,
        result: Dict[str, Any],
        base_path: Path,
        format_ids: list[str]
    ) -> Dict[str, bool]:
        """
        Export transcript to multiple formats

        Args:
            result: Transcription result dictionary
            base_path: Base path without extension
            format_ids: List of format IDs to export

        Returns:
            Dictionary mapping format_id to success status
        """
        results = {}

        for format_id in format_ids:
            strategy = self.registry.get_strategy(format_id)
            if strategy is None:
                logger.warning(f"Skipping unsupported format: {format_id}")
                results[format_id] = False
                continue

            # Create output path with appropriate extension
            output_path = base_path.with_suffix(strategy.get_file_extension())

            try:
                results[format_id] = self.export(result, output_path, format_id)
            except Exception as e:
                logger.error(f"Error exporting {format_id}: {e}", exc_info=True)
                results[format_id] = False

        return results

    def available_formats(self) -> Dict[str, str]:
        """
        Get available export formats

        Returns:
            Dictionary mapping format_id to format_name
        """
        return self.registry.available_formats()

    def suggest_filename(
        self,
        result: Dict[str, Any],
        format_id: str,
        output_dir: Optional[Path] = None
    ) -> Path:
        """
        Suggest appropriate filename for export

        Args:
            result: Transcription result dictionary
            format_id: Export format ID
            output_dir: Output directory (uses current dir if None)

        Returns:
            Suggested output path

        Raises:
            ValueError: If format is not supported
        """
        strategy = self.registry.get_strategy(format_id)
        if strategy is None:
            raise ValueError(f"Unsupported format: {format_id}")

        # Get base filename from result
        file_name = result.get('file_name', 'transcript')

        # Remove original extension and add new one
        base_name = Path(file_name).stem
        new_filename = f"{base_name}{strategy.get_file_extension()}"

        # Combine with output directory
        if output_dir is None:
            output_dir = Path.cwd()

        return output_dir / new_filename
