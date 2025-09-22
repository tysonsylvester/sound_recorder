import pyaudio
import wave
import argparse
import configparser
import os
import time
import logging
import threading
import queue
import keyboard
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Argument parser
parser = argparse.ArgumentParser(description='Cross-platform Accessible Sound Recorder')
parser.add_argument('-c', '--config', help='Path to configuration file')
parser.add_argument('-f', '--filename', help='Output filename (without .wav extension)')
parser.add_argument('-o', '--output-dir', default='.', help='Directory to save the recording')
parser.add_argument('--duration', type=int, help='Maximum recording duration in seconds (optional)')
args = parser.parse_args()

# Load config
config = configparser.ConfigParser()
default_config = {
    'format': '16bit',
    'channels': '2',
    'rate': '44100'
}

if args.config and os.path.isfile(args.config):
    config.read(args.config)
    if 'RECORDING' not in config:
        config['RECORDING'] = default_config
else:
    config['RECORDING'] = default_config

# Validate format
format_map = {
    '16bit': pyaudio.paInt16,
    '24bit': pyaudio.paInt24,
    '32bit': pyaudio.paInt32
}
fmt_str = config['RECORDING'].get('format', '16bit').lower()
if fmt_str not in format_map:
    logging.warning(f"Invalid format '{fmt_str}'. Defaulting to 16bit.")
    fmt_str = '16bit'
FORMAT = format_map[fmt_str]

# Validate channels and rate
try:
    CHANNELS = int(config['RECORDING'].get('channels', 2))
    RATE = int(config['RECORDING'].get('rate', 44100))
except ValueError:
    logging.warning("Invalid channels or rate in config. Using defaults.")
    CHANNELS = 2
    RATE = 44100

# Prepare output filename
if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)

if args.filename:
    base_name = args.filename.strip().replace(' ', '_')
    if not base_name:
        logging.error("Invalid filename provided via command line. Exiting.")
        exit(1)
else:
    while True:
        base_name = input("Enter a file name for your recording (without extension): ").strip()
        if base_name:
            # Replace spaces with underscores
            base_name = base_name.replace(' ', '_')
            break
        else:
            print("Please enter a valid file name.")

def get_unique_filename(name, directory):
    full_path = os.path.join(directory, name + '.wav')
    counter = 1
    while os.path.exists(full_path):
        full_path = os.path.join(directory, f"{name}_{counter}.wav")
        counter += 1
    return full_path

WAVE_OUTPUT_FILENAME = get_unique_filename(base_name, args.output_dir)

# Initialize PyAudio
audio = pyaudio.PyAudio()
CHUNK = 4096

try:
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True, frames_per_buffer=CHUNK)
except Exception as e:
    logging.error(f"Failed to open audio stream: {e}")
    audio.terminate()
    exit(1)

# Producer-consumer queue
frames_queue = queue.Queue()
writing_is_complete = threading.Event()

def audio_writer():
    wave_file = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wave_file.setnchannels(CHANNELS)
    wave_file.setsampwidth(audio.get_sample_size(FORMAT))
    wave_file.setframerate(RATE)
    
    while not writing_is_complete.is_set() or not frames_queue.empty():
        try:
            data = frames_queue.get(timeout=1)
            wave_file.writeframes(data)
            frames_queue.task_done()
        except queue.Empty:
            continue
            
    wave_file.close()

def get_total_seconds():
    """Prompts the user for a delay in days, hours, and minutes and returns the total in seconds."""
    total_seconds = 0
    
    # Prompt for days
    days_input = input("Enter number of days for delay (0 to skip): ").strip()
    if days_input:
        try:
            total_seconds += int(days_input) * 86400
        except ValueError:
            logging.warning("Invalid input for days. Using 0.")
    
    # Prompt for hours
    hours_input = input("Enter number of hours for delay (0 to skip): ").strip()
    if hours_input:
        try:
            total_seconds += int(hours_input) * 3600
        except ValueError:
            logging.warning("Invalid input for hours. Using 0.")
    
    # Prompt for minutes
    minutes_input = input("Enter number of minutes for delay (0 to skip): ").strip()
    if minutes_input:
        try:
            total_seconds += int(minutes_input) * 60
        except ValueError:
            logging.warning("Invalid input for minutes. Using 0.")

    return total_seconds

# Main delay logic
delay_seconds = get_total_seconds()
if delay_seconds > 0:
    # Convert total seconds back to a readable format for the countdown message
    minutes_to_start = delay_seconds // 60
    
    if minutes_to_start > 60:
        hours_to_start = minutes_to_start // 60
        remaining_minutes = minutes_to_start % 60
        print(f"Recording will start in approximately {hours_to_start} hour{'s' if hours_to_start > 1 else ''} and {remaining_minutes} minute{'s' if remaining_minutes != 1 else ''}...")
    elif minutes_to_start > 0:
        print(f"Recording will start in approximately {minutes_to_start} minute{'s' if minutes_to_start > 1 else ''}...")
    else:
        print("Recording will start in a few seconds...")
    
    time.sleep(delay_seconds - 3) # Sleep for all but the final 3 seconds
    
    # Final countdown
    for i in range(3, 0, -1):
        print(f"Starting in {i}...")
        time.sleep(1)

writer_thread = threading.Thread(target=audio_writer)
writer_thread.start()

start_time = time.time()

# Function to check and print status
def status_check():
    duration_secs = int(time.time() - start_time)
    print(f"\nStatus check: {duration_secs} seconds of audio recorded.")

# Register 's' key listener
keyboard.add_hotkey('s', status_check)

print("Recording started. Press Ctrl+C to stop, or 's' for status.")

try:
    while True:
        if args.duration and (time.time() - start_time) > args.duration:
            print("Duration limit reached.")
            break
        
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames_queue.put(data)
        
except KeyboardInterrupt:
    print("\nRecording stopped by user.")
except Exception as e:
    logging.error(f"Recording error: {e}")

# Unregister key listener to avoid issues after the program exits
keyboard.remove_hotkey('s')

# Cleanup
stream.stop_stream()
stream.close()
audio.terminate()

# Signal writer thread to finish and wait for it
writing_is_complete.set()
writer_thread.join()
frames_queue.join()

duration_secs = time.time() - start_time
print(f"Recording complete. Saved to '{WAVE_OUTPUT_FILENAME}'")
print(f"Duration: {duration_secs:.2f} seconds ({duration_secs / 60:.2f} minutes)")