# advanced_sound_recorder.py
# A robust, command-line sound recorder and editor.

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
from pydub import AudioSegment

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# -------------------------------
# Helper Functions
# -------------------------------
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

def get_unique_filename(name, directory, ext="wav"):
    """Generates a unique filename to prevent overwriting existing files."""
    full_path = os.path.join(directory, f"{name}.{ext}")
    counter = 1
    while os.path.exists(full_path):
        full_path = os.path.join(directory, f"{name}_{counter}.{ext}")
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
    """Interactive setup for recording."""
    print("--- Advanced Interactive Setup ---")
    
    # Filename
    filename_base = input("Enter a file name for your recording (e.g., 'my_podcast'): ").strip()
    if not filename_base:
        logging.error("No filename provided. Exiting.")
        return None
    
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
    start_time_input = input("Enter a start time in HH:MM format (leave blank for now): ").strip()
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
            
    # Output Format
    output_format = input("Enter output format (wav/mp3/flac) [default wav]: ").strip().lower()
    if output_format not in ["wav", "mp3", "flac"]:
        output_format = "wav"
    
    # Compile arguments
    args = argparse.Namespace(
        filename=filename_base,
        output_dir='.',
        duration=duration,
        input_device=input_device,
        start_time=start_time,
        output_format=output_format
    )
    return args

# -------------------------------
# Audio Recording
# -------------------------------
def record_audio(args):
    """Record audio based on provided arguments."""
    if not args.filename:
        filename_base = input("Enter a file name for your recording: ").strip()
        if not filename_base:
            logging.error("No filename provided. Exiting.")
            return
    else:
        filename_base = args.filename

    # Replace dynamic placeholders
    filename_base = filename_base.replace('{timestamp}', datetime.now().strftime('%Y%m%d_%H%M%S'))
    filename_base = filename_base.replace('{date}', datetime.now().strftime('%Y%m%d'))
    filename_base = filename_base.replace('{time}', datetime.now().strftime('%H%M%S'))

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    WAVE_OUTPUT_FILENAME = get_unique_filename(filename_base, args.output_dir, ext=args.output_format)

    # Handle scheduled start time
    if args.start_time:
        hours, minutes = parse_time_string(args.start_time)
        if hours is None:
            return
        start_time_dt = datetime.now().replace(hour=hours, minute=minutes, second=0, microsecond=0)
        if start_time_dt < datetime.now():
            start_time_dt = start_time_dt.replace(day=start_time_dt.day + 1)
        delay_seconds = (start_time_dt - datetime.now()).total_seconds()
        if delay_seconds > 0:
            print(f"Scheduled recording. Starting in {int(delay_seconds/60)} min {int(delay_seconds%60)} sec...")
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

    # --- Queue-based writing ---
    frames_queue = queue.Queue()
    writing_is_complete = threading.Event()
    
    def audio_writer():
        wave_file = wave.open(WAVE_OUTPUT_FILENAME if args.output_format=="wav" else WAVE_OUTPUT_FILENAME.replace(".wav",".tmp"), 'wb')
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
        # Convert to final format if needed
        if args.output_format != "wav":
            audio = AudioSegment.from_wav(wave_file.name)
            audio.export(WAVE_OUTPUT_FILENAME, format=args.output_format)
            os.remove(wave_file.name)

    writer_thread = threading.Thread(target=audio_writer)
    writer_thread.start()

    start_time_rec = time.time()
    paused = False

    def status_check():
        duration_secs = int(time.time() - start_time_rec)
        print(f"\nStatus check: {duration_secs} seconds recorded.")

    def toggle_pause():
        nonlocal paused
        paused = not paused
        print("Recording paused" if paused else "Recording resumed")

    keyboard.add_hotkey('s', status_check)
    keyboard.add_hotkey('p', toggle_pause)

    print(f"Recording started. Ctrl+C to stop, 's' for status, 'p' to pause/resume.")

    try:
        while True:
            if args.duration and (time.time() - start_time_rec) > args.duration:
                print("Duration limit reached.")
                break
            if not paused:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames_queue.put(data)
    except KeyboardInterrupt:
        print("\nRecording stopped by user.")
    except Exception as e:
        logging.error(f"Recording error: {e}")
    finally:
        keyboard.remove_hotkey('s')
        keyboard.remove_hotkey('p')
        stream.stop_stream()
        stream.close()
        p.terminate()
        writing_is_complete.set()
        writer_thread.join()
        frames_queue.join()
        duration_secs = time.time() - start_time_rec
        print(f"Recording complete. Saved {args.output_format.upper()}: '{WAVE_OUTPUT_FILENAME}'")
        print(f"Duration: {duration_secs:.2f} seconds ({duration_secs/60:.2f} minutes)")

# -------------------------------
# Edit Menu
# -------------------------------
def edit_menu():
    """Interactive audio editing menu."""
    import glob
    files = glob.glob("*.wav") + glob.glob("*.mp3") + glob.glob("*.flac")
    if not files:
        print("No audio files found in current directory.")
        return

    print("\nAvailable files:")
    for idx, f in enumerate(files):
        print(f"{idx+1}: {f}")

    choice = input("Select file number to edit: ").strip()
    try:
        file_idx = int(choice)-1
        filename = files[file_idx]
    except Exception:
        print("Invalid selection.")
        return

    audio = AudioSegment.from_file(filename)
    while True:
        print("\n--- Edit Menu ---")
        print("1. Trim")
        print("2. Fade In")
        print("3. Fade Out")
        print("4. Normalize")
        print("5. Save & Exit")
        edit_choice = input("Choose option: ").strip()
        if edit_choice == "1":
            start = int(input("Start (sec): "))
            end = int(input("End (sec): "))
            audio = audio[start*1000:end*1000]
        elif edit_choice == "2":
            duration = int(input("Fade in duration (sec): "))
            audio = audio.fade_in(duration*1000)
        elif edit_choice == "3":
            duration = int(input("Fade out duration (sec): "))
            audio = audio.fade_out(duration*1000)
        elif edit_choice == "4":
            audio = audio.normalize()
        elif edit_choice == "5":
            out_file = input(f"Enter output filename [default overwrite {filename}]: ").strip()
            if not out_file:
                out_file = filename
            audio.export(out_file, format=filename.split('.')[-1])
            print(f"Saved '{out_file}'")
            break
        else:
            print("Invalid choice.")

# -------------------------------
# Main
# -------------------------------
def main():
    parser = argparse.ArgumentParser(
        description='Advanced Sound Recorder & Editor\n\n'
                    'A command-line tool for recording and editing audio files.\n'
                    'Supports WAV, MP3, FLAC, pausing, status check, and interactive setup.',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-I', '--interactive', action='store_true',
                        help='Launch interactive setup mode to configure recording')
    parser.add_argument('-R', '--record', action='store_true',
                        help='Record audio. If combined with -I, opens interactive setup first')
    parser.add_argument('-E', '--edit', action='store_true',
                        help='Open edit menu to trim, merge, fade, or normalize audio files')
    parser.add_argument('-L', '--list-devices', action='store_true',
                        help='List all available audio input devices')
    parser.epilog = (
        "Examples:\n"
        "  python sound_recorder.py -R                # Start recording immediately\n"
        "  python sound_recorder.py -I -R             # Launch interactive setup then record\n"
        "  python sound_recorder.py -E                # Open edit menu\n"
        "  python sound_recorder.py -L                # List audio input devices\n"
        "  python sound_recorder.py                   # Fallback menu for interactive choice\n"
    )

    args = parser.parse_args()

    # If no arguments provided, ask user
    if not any([args.interactive, args.record, args.edit, args.list_devices]):
        resp = input("No mode specified. Launch interactive setup? (y/n) ").strip().lower()
        if resp == 'y':
            args.interactive = True
            args.record = True
        else:
            args.record = True

    if args.list_devices:
        list_devices()
        return

    if args.edit:
        edit_menu()
        return

    if args.record:
        if args.interactive:
            setup_args = interactive_setup()
            if setup_args:
                record_audio(setup_args)
        else:
            # Default recording with basic parameters
            record_audio(argparse.Namespace(
                filename=f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                output_dir='.',
                duration=None,
                input_device=None,
                start_time=None,
                output_format='wav'
            ))

if __name__ == "__main__":
    main()
