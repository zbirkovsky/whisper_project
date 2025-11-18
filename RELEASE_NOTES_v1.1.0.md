# CloudCall Transcription v1.1.0 - Theme System & Quality Improvements

**Release Date**: November 18, 2025

## 🎨 Major Features

### Complete Theme System
- **Dark Mode & Light Mode**: Professional themes for all lighting conditions
- **Instant Theme Switching**: Toggle with `Ctrl+D` or View menu - no restart needed
- **Consistent Design**: All components follow the same visual language in both themes
- **Accessibility**: Improved color contrast and readability in light mode

### Enhanced Configuration
- **Settings File**: Easy configuration via `settings.toml` in user directory
- **Model Selection**: Choose from tiny, base, small, medium, large-v2, or large-v3
- **Default to large-v2**: Excellent balance of quality and compatibility

## 🐛 Bug Fixes

### Theme System Fixes
Fixed numerous theme-related issues where dark colors were hardcoded:

1. **File Queue Widget**
   - Cards now adapt to theme with proper background colors
   - Progress bars use theme-aware gradients
   - Text labels respect theme colors
   - Hover states work correctly in both modes

2. **Recording Sidebar**
   - All input fields (text boxes, dropdowns) now readable in light mode
   - Checkboxes use theme colors
   - Buttons have proper contrast
   - Status indicators follow theme palette

3. **Transcript Display**
   - Syntax highlighting adapts to theme
   - Search buttons visible in both modes
   - Highlight colors appropriate for each theme
   - Fixed search functionality (PySide6 API compatibility)

4. **Dropdown Menus**
   - Fixed black text on dark background issue
   - Added proper hover states
   - All QComboBox items now have correct colors

### Search Functionality
- Fixed transcript search breaking due to PySide6 API changes
- Changed from deprecated `QTextCursor.FindFlag` to `QTextDocument.FindFlag`
- "Prev" and "Next" buttons now work correctly
- Case-sensitive search toggle functional

## 🎯 Improvements

### Visual Design
- **Semantic Colors**: Using teal (primary), green (success), orange (warning), red (error)
- **Better Gradients**: Smoother button hover effects
- **Consistent Spacing**: Using design tokens throughout (xs, sm, md, base, lg, xl)
- **Professional Look**: Modern 2025 design standards

### User Experience
- **Keyboard Shortcuts**: Added comprehensive keyboard navigation
- **Instant Feedback**: Visual feedback for all interactive elements
- **Smooth Transitions**: Theme changes apply without jarring flashes

## 📋 Configuration

### New Settings File Location
Settings are now stored in your user directory for easier access:
- **Windows**: `C:\Users\YourName\.cloudcall\settings.toml`

### Example Configuration
```toml
[transcription]
whisper_model = "large-v2"
device = "cuda"
compute_type = "float16"
batch_size = 16

[ui]
theme = "dark"  # Options: light, dark, auto

[diarization]
diarization_enabled = true
```

## 🔑 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+D` | Toggle dark/light mode |
| `Ctrl+O` | Open audio files |
| `Ctrl+T` | Save as TXT |
| `Ctrl+S` | Save as SRT |
| `Ctrl+C` | Copy transcript |
| `Ctrl+L` | Clear display |

## 📦 Installation

### Upgrade from v1.0.0
1. Download the latest release
2. Run the installer (will preserve your settings)
3. Your existing models and recordings are preserved

### Fresh Installation
1. Download `CloudCallTranscription-Setup-1.1.0.exe`
2. Run installer and follow prompts
3. Configure `settings.toml` if needed (optional)
4. Launch and enjoy!

## 🔧 Technical Changes

### Architecture
- Implemented theme propagation system across widget hierarchy
- Centralized color management in `StyleSheetManager`
- All widgets now have `update_theme()` methods
- Theme-aware color helpers in all custom widgets

### Code Quality
- Removed 100+ instances of hardcoded colors
- Improved code maintainability
- Better separation of concerns
- Consistent styling approach

## 🙏 Acknowledgments

Thank you to all users who reported the theme visibility issues. Your feedback helps make CloudCall Transcription better!

## 📝 Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete details of all changes.

---

**Enjoy the new theme system!** 🎉

For support or feedback, please open an issue on GitHub.
