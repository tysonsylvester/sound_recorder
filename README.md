# Advanced Sound Recorder & Editor

**Version:** 1.3  
**Date:** 2025-09-22  

A **robust, command-line sound recorder and editor** designed for power users.  
Supports multiple audio formats, scheduling, pausing, and basic editing features.

---

## Features

### Recording
- Record audio in **WAV**, **MP3**, or **FLAC** formats.
- Dynamic filenames with placeholders:
  - `{timestamp}` → `YYYYMMDD_HHMMSS`
  - `{date}` → `YYYYMMDD`
  - `{time}` → `HHMMSS`
  - `{counter}` → Incremental number to prevent overwriting
- **Pause/resume** recording with `p` key.
- **Status check** with `s` key during recording.
- Schedule recordings with `--start-time HH:MM`.

### Editing
- Interactive **edit menu**:
  - Trim audio (select start/end in seconds)
  - Merge multiple audio files
  - Fade in/out
  - Normalize volume
- Automatically lists available audio files for selection.
- Supports overwriting or creating a new file when saving.

### Devices
- Lists all available **audio input devices**.
- Allows selection of a specific device or defaults to the system input.
- Graceful fallback if the chosen device is unavailable.

### Advanced Features
- Threaded **queue-based writing** to prevent data loss.
- Works cross-platform with Windows, Linux, and macOS (requires PyAudio & pydub).
- Interactive setup wizard guides users through configuration.

---

## Installation

1. Clone this repository or download the source.
2. Install dependencies:

```bash
pip install pyaudio pydub keyboard
3. 
For MP3/FLAC support, ensure ffmpeg is installed and available in your system PATH.
 
Usage
Interactive Recording
bash
Copy
python sound_recorder.py record --interactive
Walks you through filename, format, duration, start time, and device selection.
Command-Line Recording
bash
Copy
python sound_recorder.py record -f my_recording_{timestamp} -o recordings -d 300 -i 1 --output-format mp3
• 
Records 5 minutes (300 seconds) from device ID 1, saves as MP3 in the recordings folder.
Editing Mode
bash
Copy
python sound_recorder.py edit
• 
Opens the interactive edit menu for trimming, merging, fading, or normalizing audio files.
 
Hotkeys During Recording
• 
p → Pause/resume recording
• 
s → Show elapsed recording time
• 
Ctrl+C → Stop recording
 
Future Improvements
• 
Multi-track editing support
• 
Background scheduled recording with Task Scheduler or Cron
• 
Preset export options with configurable bitrates
• 
Enhanced audio effects and filtering
 
Notes / Known Issues
• 
MP3/FLAC support requires ffmpeg. A warning appears if it’s not found.
• 
Scheduled recording currently blocks execution during wait. Future versions may integrate system schedulers.
• 
Editing operations require accurate input in seconds or milliseconds for trimming/fading.
