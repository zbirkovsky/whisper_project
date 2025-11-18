# Changelog

All notable changes to CloudCall Transcription will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-18

### Added
- **Theme System Overhaul**: Complete dark mode and light mode support
  - Added `settings.toml` configuration file for user preferences
  - Implemented theme-aware color system using `StyleSheetManager`
  - Added keyboard shortcut `Ctrl+D` to toggle dark/light mode
  - Added View menu option to switch themes
- **Model Configuration**: Added support for configuring Whisper model via settings
  - Default changed to `large-v2` for optimal quality
  - Models can now be changed in `settings.toml` without code changes

### Fixed
- **Theme System Bugs**: Removed all hardcoded dark colors from UI components
  - Fixed `FileQueueWidget`: Cards, progress bars, and labels now adapt to theme
  - Fixed `RecordingSidebarWidget`: All controls (buttons, checkboxes, inputs) now theme-aware
  - Fixed `TranscriptWidget`: Search buttons and syntax highlighting now respect theme
  - Fixed `DropZoneWidget`: Border and background colors now theme-aware
  - Fixed QComboBox dropdown menus: Text now visible in both dark and light modes
  - Fixed dropdown item hover states for better visibility
- **Search Functionality**: Fixed transcript search breaking due to PySide6 API changes
  - Changed from deprecated `QTextCursor.FindFlag` to `QTextDocument.FindFlag`
  - Search now works correctly with case-sensitive toggle
  - Fixed "Prev" and "Next" navigation buttons
- **UI Layout Bug**: Fixed crash when adding control buttons to recording sidebar

### Changed
- **Color System**: All widgets now use semantic colors from theme palette
  - Primary colors (teal): Buttons, focus states, progress bars
  - Success colors (green): Speaker labels, completion states
  - Warning colors (orange): Search highlights, pause button
  - Error colors (red): Error states, stop button
  - Neutral colors: Backgrounds, borders, text (adapts to theme)
- **Button Gradients**: Improved visual feedback with lighter hover states
- **Model Default**: Changed default Whisper model from `large-v3` to `large-v2`
  - `large-v2` provides excellent quality with broader compatibility
  - Users can still configure `large-v3` in settings if desired

### Improved
- **Visual Consistency**: All UI components now follow the same design language
  - Consistent spacing using design tokens (xs, sm, md, base, lg, xl)
  - Consistent border radius across all cards and buttons
  - Consistent typography hierarchy
- **Accessibility**: Better color contrast in light mode for improved readability
- **User Experience**: Smoother theme transitions without requiring app restart

### Technical
- Implemented theme propagation system across widget hierarchy
- Added `update_theme()` methods to all custom widgets
- Centralized color management in `StyleSheetManager`
- Added `_get_colors()` helper methods for theme-aware styling
- Updated all QSS stylesheets to use f-strings with theme variables

## [1.0.0] - 2025-10-20

### Added
- Initial release of CloudCall Transcription
- WhisperX integration for high-accuracy transcription
- Pyannote.audio speaker diarization
- GPU acceleration support (CUDA)
- Multi-language support (Czech, English with auto-detection)
- Audio recording with WASAPI loopback
- Teams meeting integration
- Drag-and-drop file support
- Export to TXT and SRT formats
- Modern Fluent Design UI
- Quality presets (GPU Balanced, GPU Fast, CPU Optimized)
- Batch file processing
- Real-time transcription progress
