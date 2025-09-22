# advanced_sound_recorder.py
# A robust, command-line sound recorder for power users.

import pyaudio
import wave
import argparse
import os
import time
import logging
import threading
import queue
import keyboard
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def list_devices():
    """Prints a list of available audio input devices."""
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    print("\n--- Available Audio Devices ---")
    devices = []
    for i in range(0, num_devices):
        device_info = p.get_device_info_by_host_api_device_index(0, i)
        if device_info.get('maxInputChannels') > 0:
            print(f"Device ID: {i} | Name: {device_info.get('name')}")
            devices.append({'id': i, 'name': device_info.get('name')})
    print("-----------------------------\n")
    p.terminate()
    return devices

def get_unique_filename(name, directory):
    """Generates a unique filename to prevent overwriting existing files."""
    full_path = os.path.join(directory, name + '.wav')
    counter = 1
    while os.path.exists(full_path):
        full_path = os.path.join(directory, f"{name}_{counter}.wav")
        counter += 1
    return full_path

def parse_time_string(time_str):
    """Parses a time string in HH:MM format."""
    try:
        hours, minutes = map(int, time_str.split(':'))
        return hours, minutes
    except (ValueError, IndexError):
        logging.error("Invalid time format. Please use HH:MM (e.g., 23:00).")
        return None, None

def interactive_setup():
    """Walks the user through an interactive setup to configure the recording."""
    print("--- Advanced Interactive Setup ---")
    
    # Filename
    filename_base = input("Enter a file name for your recording (e.g., 'my_podcast'): ").strip()
    if not filename_base:
        logging.error("No filename provided. Exiting.")
        return
    
    # Dynamic Filename
    use_dynamic = input("Use a dynamic filename with a timestamp? (y/n): ").strip().lower()
    if use_dynamic == 'y':
        filename_base += "_{timestamp}"
    
    # Duration
    duration = None
    duration_input = input("Enter a recording duration in seconds (or leave blank for infinite): ").strip()
    if duration_input:
        try:
            duration = int(duration_input)
        except ValueError:
            logging.error("Invalid duration. Using infinite duration.")
    
    # Start Time
    start_time = None
    start_time_input = input("Enter a start time in HH:MM format (e.g., 14:30) or leave blank: ").strip()
    if start_time_input:
        start_time = start_time_input
        
    # Input Device
    print("\nListing available devices...")
    devices = list_devices()
    input_device = None
    device_id_input = input("Enter the ID of the device you want to use (or leave blank for default): ").strip()
    if device_id_input:
        try:
            input_device = int(device_id_input)
        except ValueError:
            logging.error("Invalid device ID. Using default device.")
            
    # Compile arguments
    args = argparse.Namespace(
        filename=filename_base,
        output_dir='.',
        duration=duration,
        input_device=input_device,
        start_time=start_time,
        list_devices=False,
        interactive=True
    )
    return args

def main():
    """Main function to parse arguments and start recording."""
    parser = argparse.ArgumentParser(
        description='A robust, cross-platform sound recorder for power users.',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-f', '--filename',
                        help="""Output filename (e.g., 'podcast_show_{timestamp}').
Dynamic placeholders:
- {timestamp}: YYYYMMDD_HHMMSS
- {date}: YYYYMMDD
- {time}: HHMMSS
- {counter}: Incremental number
Example: --filename 'my_recording_{timestamp}'""")
    parser.add_argument('-o', '--output-dir', default='.', help='Directory to save the recording.')
    parser.add_argument('-d', '--duration', type=int, help='Maximum recording duration in seconds.')
    parser.add_argument('-i', '--input-device', type=int, help='The input device ID to use. Use --list-devices to find IDs.')
    parser.add_argument('-l', '--list-devices', action='store_true', help='List all available audio input devices and exit.')
    parser.add_argument('--start-time', help='Specify a start time in HH:MM format (e.g., 14:30).')
    parser.add_argument('--interactive', action='store_true', help='Start an interactive setup wizard to configure the recording.')
    
    args = parser.parse_args()

    # If interactive mode is requested, run the setup wizard and override CLI args
    if args.interactive:
        args = interactive_setup()
        if not args:
            return # Exit if interactive setup failed
            
    # Handle device listing request if not in interactive mode
    if args.list_devices:
        list_devices()
        return

    # Handle filename and output directory logic
    if not args.filename:
        # If no filename is provided via CLI, prompt the user
        filename_base = input("Enter a file name for your recording: ").strip()
        if not filename_base:
            logging.error("No filename provided. Exiting.")
            return
    else:
        # Process dynamic placeholders in filename
        filename_base = args.filename.replace('{timestamp}', datetime.now().strftime('%Y%m%d_%H%M%S'))
        filename_base = filename_base.replace('{date}', datetime.now().strftime('%Y%m%d'))
        filename_base = filename_base.replace('{time}', datetime.now().strftime('%H%M%S'))
        # Counter will be handled by get_unique_filename

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    WAVE_OUTPUT_FILENAME = get_unique_filename(filename_base, args.output_dir)

    # Handle scheduled start time
    if args.start_time:
        hours, minutes = parse_time_string(args.start_time)
        if hours is None:
            return
        
        start_time_dt = datetime.now().replace(hour=hours, minute=minutes, second=0, microsecond=0)
        if start_time_dt < datetime.now():
            # If the time is in the past, assume they mean tomorrow
            start_time_dt = start_time_dt.replace(day=start_time_dt.day + 1)
        
        delay_seconds = (start_time_dt - datetime.now()).total_seconds()
        
        if delay_seconds > 0:
            print(f"Scheduled recording. Starting in {int(delay_seconds / 60)} minutes and {int(delay_seconds % 60)} seconds...")
            try:
                time.sleep(delay_seconds)
            except KeyboardInterrupt:
                print("\nScheduled recording canceled.")
                return

    # --- PyAudio Setup ---
    p = pyaudio.PyAudio()
    CHUNK = 4096
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100

    # Get device info
    input_device_index = args.input_device
    if input_device_index is not None:
        try:
            device_info = p.get_device_info_by_index(input_device_index)
            print(f"Using device: {device_info['name']}")
            CHANNELS = device_info['maxInputChannels']
            RATE = int(device_info['defaultSampleRate'])
        except Exception as e:
            logging.error(f"Failed to get device info for ID {input_device_index}: {e}. Falling back to default.")
            input_device_index = None

    try:
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=input_device_index)
    except Exception as e:
        logging.error(f"Failed to open audio stream: {e}")
        p.terminate()
        return

    # --- Producer-consumer queue for efficient writing ---
    frames_queue = queue.Queue()
    writing_is_complete = threading.Event()
    
    def audio_writer():
        """Handles writing audio data to a wave file in a separate thread."""
        wave_file = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(p.get_sample_size(FORMAT))
        wave_file.setframerate(RATE)
        
        while not writing_is_complete.is_set() or not frames_queue.empty():
            try:
                data = frames_queue.get(timeout=1)
                wave_file.writeframes(data)
                frames_queue.task_done()
            except queue.Empty:
                continue
                
        wave_file.close()

    writer_thread = threading.Thread(target=audio_writer)
    writer_thread.start()

    start_time = time.time()
    
    def status_check():
        """Prints a real-time status update to the console."""
        duration_secs = int(time.time() - start_time)
        print(f"\nStatus check: {duration_secs} seconds of audio recorded.")

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
    finally:
        keyboard.remove_hotkey('s')
        stream.stop_stream()
        stream.close()
        p.terminate()
        writing_is_complete.set()
        writer_thread.join()
        frames_queue.join()

        duration_secs = time.time() - start_time
        print(f"Recording complete. Saved to '{WAVE_OUTPUT_FILENAME}'")
        print(f"Duration: {duration_secs:.2f} seconds ({duration_secs / 60:.2f} minutes)")

if __name__ == "__main__":
    main()
