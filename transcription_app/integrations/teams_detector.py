"""
Microsoft Teams meeting detection using Windows API
Detects active Teams meetings by monitoring window titles
"""
import re
from typing import Optional
from transcription_app.utils.logger import get_logger

logger = get_logger(__name__)

try:
    import psutil
    import win32gui
    import win32process
    WINDOWS_INTEGRATION_AVAILABLE = True
except ImportError:
    WINDOWS_INTEGRATION_AVAILABLE = False
    logger.warning("Windows integration not available (pywin32/psutil not installed)")


def detect_teams_meeting() -> Optional[str]:
    """
    Detect active Microsoft Teams meeting by scanning window titles

    Returns:
        Meeting name if detected, None otherwise
    """
    if not WINDOWS_INTEGRATION_AVAILABLE:
        logger.debug("Windows integration not available, skipping Teams detection")
        return None

    try:
        # Find all Teams processes
        teams_pids = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'teams' in proc.info['name'].lower():
                    teams_pids.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if not teams_pids:
            logger.debug("No Teams processes found")
            return None

        logger.debug(f"Found {len(teams_pids)} Teams processes")

        # Scan all windows for Teams meeting titles
        meeting_name = None

        def enum_windows_callback(hwnd, _):
            nonlocal meeting_name

            if not win32gui.IsWindowVisible(hwnd):
                return True

            # Get window title
            try:
                title = win32gui.GetWindowText(hwnd)
                if not title:
                    return True

                # Get process ID for this window
                _, pid = win32process.GetWindowThreadProcessId(hwnd)

                # Check if it's a Teams window
                if pid not in teams_pids:
                    return True

                # Parse Teams meeting window title
                # Common patterns:
                # "Meeting Name | Microsoft Teams"
                # "Meeting with Person Name | Microsoft Teams"
                # "Channel - Team Name | Microsoft Teams"

                if "microsoft teams" in title.lower():
                    # Extract meeting name before the pipe
                    parts = title.split('|')
                    if len(parts) >= 2:
                        potential_meeting = parts[0].strip()

                        # Filter out common non-meeting windows
                        exclude_keywords = [
                            'chat', 'teams', 'calendar', 'files',
                            'calls', 'activity', 'settings'
                        ]

                        if potential_meeting.lower() not in exclude_keywords:
                            # This looks like a meeting name
                            logger.info(f"Detected Teams meeting: {potential_meeting}")
                            meeting_name = potential_meeting
                            return False  # Stop enumeration

            except Exception as e:
                logger.debug(f"Error processing window {hwnd}: {e}")

            return True

        # Enumerate all windows
        win32gui.EnumWindows(enum_windows_callback, None)

        if meeting_name:
            return sanitize_meeting_name(meeting_name)

        logger.debug("No Teams meeting window detected")
        return None

    except Exception as e:
        logger.error(f"Error detecting Teams meeting: {e}", exc_info=True)
        return None


def sanitize_meeting_name(meeting_name: str) -> str:
    """
    Sanitize meeting name for use in filenames

    Args:
        meeting_name: Raw meeting name from window title

    Returns:
        Sanitized meeting name safe for filenames
    """
    # Remove or replace invalid filename characters
    # Windows invalid chars: < > : " / \ | ? *
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', meeting_name)

    # Replace multiple spaces/underscores with single underscore
    sanitized = re.sub(r'[_\s]+', '_', sanitized)

    # Remove leading/trailing underscores and spaces
    sanitized = sanitized.strip('_ ')

    # Limit length to avoid overly long filenames
    max_length = 100
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip('_')

    # If somehow we end up with empty string, return default
    if not sanitized:
        sanitized = "Meeting"

    return sanitized


def is_teams_running() -> bool:
    """
    Check if Microsoft Teams is currently running

    Returns:
        True if Teams process is found, False otherwise
    """
    if not WINDOWS_INTEGRATION_AVAILABLE:
        return False

    try:
        for proc in psutil.process_iter(['name']):
            try:
                if 'teams' in proc.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    except Exception as e:
        logger.error(f"Error checking if Teams is running: {e}")
        return False
