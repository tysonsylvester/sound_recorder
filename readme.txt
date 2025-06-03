Sound Recorder README

A simple command-line sound recorder written in Python.

Features

• Records audio from the default input device
• Saves recordings in WAV format
• Allows user to specify file name for recording
• Records continuously until user stops with 'esc' key


Requirements

• Python 3.x
• pyaudio library (install with pip install pyaudio)
• keyboard library (install with pip install keyboard)


Usage

1. Run the script using python sound_recorder.py
2. Enter a file name for your recording when prompted
3. Press 'esc' to stop recording
4. The recording will be saved to the specified file name


Configuration

You can customize the recording settings by creating a configuration file. Use the -c or --config option to specify the path to your configuration file.

Example configuration file:
[RECORDING]
format = 16bit
channels = 2
rate = 44100

Troubleshooting

• Make sure to install the required libraries using pip
• If you encounter issues with pyaudio, check the official documentation for installation instructions specific to your operating system


License

This script is released under the MIT License. Feel free to modify and distribute it as you see fit.