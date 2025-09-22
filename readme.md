PyAudio Sound Recorder
A simple, yet powerful, cross-platform command-line application for recording audio. This tool leverages the PyAudio library to capture sound from your microphone and save it as a high-quality .wav file. It's designed for efficiency and ease of use, with multi-threaded operations and a configurable interface.

Features
High-Quality Audio: Records audio with configurable format (16bit, 24bit, 32bit), channels, and sample rate.

Command-Line Control: Supports arguments for specifying the output filename, directory, and recording duration.

Configuration File: Easily manage recording settings using an optional config.ini file.

Timed Delay: Set a specific time delay (in days, hours, or minutes) for the recording to start.

Real-time Status Check: Press the s key at any point during recording to get a quick status update on the duration.

Non-destructive Filenames: Automatically appends a number to the filename (e.g., recording_1.wav) to prevent overwriting existing files.

Multi-threaded Performance: Uses a producer-consumer model to ensure smooth, uninterrupted recording without buffer overflows.

Prerequisites
To run this application, you will need:

Python 3.x

The system-level library PortAudio.

Windows: PortAudio is included with the PyAudio wheel.

macOS: You can install it using Homebrew: brew install portaudio

Installation
Clone this repository or download the script.

Install the required Python packages using pip:

pip install PyAudio keyboard

Note: Depending on your system, you may need to use pip3 instead of pip.

Usage
You can run the script in two primary ways: interactively or with command-line arguments.

Interactive Mode
Simply run the script with no arguments. It will prompt you for a filename and allow you to set a delay for the recording to start.

python your_script_name.py

Command-Line Arguments
Use the available command-line arguments for more control:

-f, --filename: Specify the output filename without the .wav extension.

-o, --output-dir: Set the directory where the recording will be saved. Defaults to the current directory.

--duration: Set a maximum recording duration in seconds.

Examples:

# Record and save to a file named 'meeting_notes.wav' in the current directory
python your_script_name.py -f meeting_notes

# Record for a maximum of 120 seconds and save to a 'recordings' folder
python your_script_name.py --duration 120 -o recordings -f quick_note

# Use a specific configuration file
python your_script_name.py -c my_config.ini

In-Recording Controls
To stop the recording, press Ctrl+C.

To check the current duration of the recording, press the s key.

Configuration
You can customize the recording settings by creating a file named config.ini and placing it in the same directory as the script.

[RECORDING]
# Audio format: 16bit, 24bit, or 32bit
format = 16bit

# Number of audio channels (e.g., 1 for mono, 2 for stereo)
channels = 2

# Sample rate in Hz (e.g., 44100 for CD quality)
rate = 44100

Contributing
Contributions are welcome! Please feel free to open an issue or submit a pull request.

