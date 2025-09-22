Advanced PyAudio Sound Recorder
A robust, command-line tool for professional and power users who need complete control over their audio recordings. This application is designed to be highly flexible and easily integrated into automated workflows using command-line arguments and external schedulers.
Features
• 
Interactive Setup: Use the new --interactive flag to be guided through a simple wizard for complex recording setups.
Prerequisites
To run this application, you need Python 3 and the following dependencies.
• 
PyAudio: For capturing audio from your microphone.
You can install them directly using pip:
pip install pyaudio keyboard


For platform-specific prerequisites, you may also need to install portaudio.
• 
Linux: sudo apt-get install portaudio19-dev
Usage
Interactive Setup (Recommended for new users)
For complex, one-time recording sessions, use the --interactive flag to launch a user-friendly setup wizard.
python sound_recorder.py --interactive


The program will then prompt you for a filename, duration, start time, and input device.
Listing Audio Devices
To find the ID of your desired audio device, use the --list-devices flag. This is often the first step before a complex recording.
python sound_recorder.py --list-devices


This will output a list of available devices and their corresponding IDs.
Non-Interactive Recording
Record for a specific duration with a predefined filename and output directory. This is ideal for automation.
python sound_recorder.py -f my_show -o recordings --duration 3600


This command will record for 1 hour (3600 seconds), save the file as my_show.wav in the recordings directory, and exit automatically.
Dynamic Filenames
Use placeholders to automatically generate unique filenames based on the current date and time.
python sound_recorder.py -f 'podcast_{timestamp}'


This will create a file named something like podcast_20240523_143000.wav.
Scheduled Recording
Schedule a recording to begin at a specific time (e.g., 23:00 or 11 PM). The script will wait until the specified time and then start recording.
# Wait until 11:00 PM to start recording
python sound_recorder.py --start-time 23:00 -f 'late_night_show'


For recurring schedules, you should integrate this command with a system-level scheduler like cron (on Linux/macOS) or Task Scheduler (on Windows).
Selecting an Input Device
To record from a specific microphone, use the --input-device flag with the ID from the --list-devices command.
# Example: Using device ID 5 to record for 20 minutes
python sound_recorder.py -i 5 --duration 1200 -f 'pro_mic_recording'
