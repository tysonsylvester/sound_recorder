Sound Recorder & Editor – Changelog
Version: 1.3 (Current)
Date: 2025-09-22
 
New Features
1. 
Audio Format Support
• 
Record audio in WAV, MP3, or FLAC formats.
• 
Added --output-format CLI option and interactive prompt to choose format.
• 
Ensures filename extension matches the selected format.
• 
Includes fallback to WAV if format not specified.
2. 
Pause/Resume & Status Hotkeys
• 
Press p to pause/resume recording.
• 
Press s to print current recording duration.
• 
Fully integrated with interactive and CLI modes.
3. 
Interactive Edit Menu
• 
Added interactive menu for audio editing (mode=edit).
• 
Supports:
• 
Trim audio (select start and end time in seconds)
• 
Merge multiple audio files
• 
Fade in/out
• 
Normalize audio volume
• 
Automatically lists available audio files for selection.
4. 
Dynamic Filenames
• 
{timestamp} placeholder in filename for automatic timestamping.
• 
Ensures unique filenames to avoid overwriting existing recordings.
5. 
Improved Scheduling
• 
Records can be scheduled by specifying --start-time HH:MM.
• 
Handles past times by automatically scheduling for the next day.
 
Enhancements
1. 
Robust PyAudio Handling
• 
Graceful handling when device IDs are invalid or unavailable.
• 
Automatically falls back to default input device if custom device fails.
• 
Improved error logging for stream failures.
2. 
Queue-based Recording
• 
Uses producer-consumer queue for thread-safe audio writing.
• 
Prevents audio data loss during high CPU load.
3. 
Cross-Platform Compatibility
• 
Compatible with Windows (tested), Linux, and macOS (requires PyAudio & pydub).
4. 
Interactive Setup Wizard
• 
Walks users through:
• 
File naming and dynamic timestamp options
• 
Duration (or infinite)
• 
Start time
• 
Input device selection
• 
Output format selection
5. 
Editor Improvements
• 
Users can overwrite or specify a new file when editing.
• 
Menu is persistent until user selects “Exit”.
• 
Supports trimming, merging, fading, and normalization.
 
Bug Fixes / Stability Improvements
1. 
Fixed silent crashes related to missing output directories.
2. 
Fixed stream overflow errors during long recordings.
3. 
Ensured queue and writer threads terminate properly on interrupt.
4. 
Added keyboard hotkey cleanup on exit.
5. 
Added fallback for invalid device IDs or formats.
 
Known Limitations / Notes
1. 
ffmpeg required for MP3/FLAC recording and editing (pydub dependency).
• 
Warning is displayed if ffmpeg is not found.
2. 
Scheduled recording still uses time.sleep, so very long waits block the script.
• 
Future improvement: integrate with Task Scheduler or background threading.
3. 
Merge/fade/normalize operations require user input for file selection in seconds or milliseconds.