2025-09-22
• 
Scheduler Added: Implemented a new scheduling feature that allows users to specify delays in days, hours, and minutes before recording starts.
• 
Improved Countdown: The countdown for long delays is now more concise, providing updates in hours and minutes before a final 3-second countdown.
• 
Code Refactoring: The changelog was moved to this dedicated CHANGELOG.md file to follow standard GitHub practices.
2025-09-21
• 
Critical Bug Fix: Corrected a wave library AttributeError caused by a typo (setfrate was replaced with setframerate).
• 
Filename Validation: Added logic to prevent users from starting a recording with an empty filename.
• 
Improved Filename Handling: Replaced spaces in user-provided filenames with underscores to ensure file compatibility across different operating systems.
2025-09-20
• 
Performance: Introduced a multi-threaded "producer-consumer" model to improve recording stability. One thread captures audio, and a separate thread writes the data to the file, preventing dropped frames.
• 
User Interface: Added a feature that allows users to check the current recording duration by pressing the 'S' key, eliminating constant console output during recording.
2025-09-19
• 
Initial Release: The first version of the sound recorder script.
• 
Core Functionality: Implements basic audio recording, configurable recording parameters, and automatic unique filename generation.