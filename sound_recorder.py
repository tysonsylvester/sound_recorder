# sound_recorder.py
# Advanced Sound Recorder & Editor with interactive editing menu

import os
import time
import threading
import queue
import argparse
import logging
import wave
import keyboard
from datetime import datetime
from pydub import AudioSegment
import pyaudio

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# ---------------------- Audio Device Utilities ----------------------
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

def get_unique_filename(name, directory, ext='wav'):
    """Generates a unique filename to prevent overwriting existing files."""
    full_path = os.path.join(directory, name + f'.{ext}')
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

# ---------------------- Interactive Setup ----------------------
def interactive_setup():
    """Interactive setup for recording configuration."""
    print("--- Advanced Interactive Setup ---")
    
    filename_base = input("Enter a file name for your recording (e.g., 'my_podcast'): ").strip()
    if not filename_base:
        logging.error("No filename provided. Exiting.")
        return
    
    use_dynamic = input("Use a dynamic filename with timestamp? (y/n): ").strip().lower()
    if use_dynamic == 'y':
        filename_base += "_{timestamp}"
    
    duration = None
    duration_input = input("Enter duration in seconds (leave blank for infinite): ").strip()
    if duration_input:
        try:
            duration = int(duration_input)
        except ValueError:
            logging.warning("Invalid duration. Using infinite duration.")
    
    start_time = None
    start_time_input = input("Enter start time HH:MM (leave blank for now): ").strip()
    if start_time_input:
        start_time = start_time_input
        
    print("\nListing devices...")
    devices = list_devices()
    input_device = None
    device_id_input = input("Enter device ID (leave blank for default): ").strip()
    if device_id_input:
        try:
            input_device = int(device_id_input)
        except ValueError:
            logging.warning("Invalid device ID. Using default device.")
    
    output_format = input("Enter output format (wav/mp3/flac) [default wav]: ").strip().lower() or "wav"

    args = argparse.Namespace(
        filename=filename_base,
        output_dir='.',
        duration=duration,
        input_device=input_device,
        start_time=start_time,
        interactive=True,
        output_format=output_format
    )
    return args

# ---------------------- Audio Editing Utilities ----------------------
def list_audio_files(directory='.'):
    audio_extensions = ('.wav', '.mp3', '.flac')
    files = [f for f in os.listdir(directory) if f.lower().endswith(audio_extensions)]
    if not files:
        print("No audio files found in the current directory.")
        return []
    print("\n--- Audio Files ---")
    for idx, f in enumerate(files, start=1):
        print(f"{idx}. {f}")
    print("------------------")
    return files

def select_file(files):
    while True:
        choice = input("Enter the number of the file to edit: ").strip()
        if not choice.isdigit():
            print("Enter a valid number.")
            continue
        idx = int(choice) - 1
        if 0 <= idx < len(files):
            return files[idx]
        print("Number out of range.")

def interactive_edit_menu():
    while True:
        print("\n--- Audio Editing Menu ---")
        print("1. Trim audio")
        print("2. Merge audio files")
        print("3. Fade in/out")
        print("4. Normalize volume")
        print("5. Exit")
        choice = input("Choice [1-5]: ").strip()

        if choice == '1':
            files = list_audio_files()
            if not files: continue
            file_to_edit = select_file(files)
            audio = AudioSegment.from_file(file_to_edit)
            start_ms = int(input("Start time in seconds: ").strip()) * 1000
            end_ms = int(input("End time in seconds: ").strip()) * 1000
            trimmed = audio[start_ms:end_ms]
            output = input("Output filename (leave blank to overwrite): ").strip() or file_to_edit
            trimmed.export(output, format=os.path.splitext(output)[1][1:])
            print(f"Trimmed audio saved as {output}")

        elif choice == '2':
            files = list_audio_files()
            if not files or len(files) < 2:
                print("Need at least 2 files to merge.")
                continue
            print("Enter file numbers to merge, comma-separated:")
            indices = input().split(',')
            try:
                selected_files = [files[int(i.strip())-1] for i in indices]
            except Exception:
                print("Invalid selection.")
                continue
            combined = AudioSegment.empty()
            for f in selected_files:
                combined += AudioSegment.from_file(f)
            output = input("Output filename: ").strip()
            if output:
                combined.export(output, format=os.path.splitext(output)[1][1:])
                print(f"Merged audio saved as {output}")

        elif choice == '3':
            files = list_audio_files()
            if not files: continue
            file_to_edit = select_file(files)
            audio = AudioSegment.from_file(file_to_edit)
            fade_in_ms = int(input("Fade-in duration ms: ").strip())
            fade_out_ms = int(input("Fade-out duration ms: ").strip())
            faded = audio.fade_in(fade_in_ms).fade_out(fade_out_ms)
            output = input("Output filename (leave blank to overwrite): ").strip() or file_to_edit
            faded.export(output, format=os.path.splitext(output)[1][1:])
            print(f"Faded audio saved as {output}")

        elif choice == '4':
            files = list_audio_files()
            if not files: continue
            file_to_edit = select_file(files)
            audio = AudioSegment.from_file(file_to_edit)
            target_dB = float(input("Target dBFS (e.g., -20.0): ").strip())
            change_in_dB = target_dB - audio.dBFS
            normalized = audio.apply_gain(change_in_dB)
            output = input("Output filename (leave blank to overwrite): ").strip() or file_to_edit
            normalized.export(output, format=os.path.splitext(output)[1][1:])
            print(f"Normalized audio saved as {output}")

        elif choice == '5':
            print("Exiting edit menu.")
            break
        else:
            print("Invalid choice. Enter 1-5.")

# ---------------------- Main Recorder ----------------------
def main():
    parser = argparse.ArgumentParser(
        description='Advanced Sound Recorder & Editor',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('mode', choices=['record','edit'], help='Mode: record or edit')
    parser.add_argument('-f', '--filename', help='Output filename (with optional placeholders)')
    parser.add_argument('-o', '--output-dir', default='.', help='Directory to save the recording')
    parser.add_argument('-d', '--duration', type=int, help='Maximum recording duration in seconds')
    parser.add_argument('-i', '--input-device', type=int, help='Input device ID')
    parser.add_argument('-l', '--list-devices', action='store_true', help='List audio input devices and exit')
    parser.add_argument('--start-time', help='Start time HH:MM')
    parser.add_argument('--interactive', action='store_true', help='Interactive setup')
    parser.add_argument('--output-format', help='Recording format (wav/mp3/flac)', default='wav')

    args = parser.parse_args()

    if args.mode == 'edit':
        interactive_edit_menu()
        return

    if args.mode == 'record':
        if args.interactive:
            args = interactive_setup()
            if not args:
                return

        if args.list_devices:
            list_devices()
            return

        # Prepare filename
        filename_base = args.filename or input("Enter filename: ").strip()
        if not filename_base:
            logging.error("No filename provided. Exiting.")
            return

        # Handle dynamic timestamp
        filename_base = filename_base.replace('{timestamp}', datetime.now().strftime('%Y%m%d_%H%M%S'))
        ext = args.output_format
        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)
        WAVE_OUTPUT_FILENAME = get_unique_filename(filename_base, args.output_dir, ext)

        # Scheduled start
        if args.start_time:
            hours, minutes = parse_time_string(args.start_time)
            if hours is None:
                return
            start_time_dt = datetime.now().replace(hour=hours, minute=minutes, second=0, microsecond=0)
            if start_time_dt < datetime.now():
                start_time_dt = start_time_dt.replace(day=start_time_dt.day + 1)
            delay = (start_time_dt - datetime.now()).total_seconds()
            if delay > 0:
                print(f"Scheduled recording. Starting in {int(delay/60)}m {int(delay%60)}s...")
                try: time.sleep(delay)
                except KeyboardInterrupt:
                    print("Scheduled recording canceled.")
                    return

        # --- PyAudio Setup ---
        p = pyaudio.PyAudio()
        CHUNK = 4096
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        input_device_index = args.input_device
        try:
            if input_device_index is not None:
                device_info = p.get_device_info_by_index(input_device_index)
                CHANNELS = device_info['maxInputChannels']
                RATE = int(device_info['defaultSampleRate'])
                print(f"Using device: {device_info['name']}")
        except Exception as e:
            logging.warning(f"Failed to get device info: {e}. Using default device.")
            input_device_index = None

        try:
            stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
                            frames_per_buffer=CHUNK, input_device_index=input_device_index)
        except Exception as e:
            logging.error(f"Failed to open audio stream: {e}")
            p.terminate()
            return

        frames_queue = queue.Queue()
        writing_done = threading.Event()

        def audio_writer():
            wave_file = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            wave_file.setnchannels(CHANNELS)
            wave_file.setsampwidth(p.get_sample_size(FORMAT))
            wave_file.setframerate(RATE)
            while not writing_done.is_set() or not frames_queue.empty():
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
        paused = False

        def status_check():
            print(f"\nRecorded {int(time.time()-start_time)}s of audio.")

        def toggle_pause():
            nonlocal paused
            paused = not paused
            print("Recording paused" if paused else "Recording resumed")

        keyboard.add_hotkey('s', status_check)
        keyboard.add_hotkey('p', toggle_pause)
        print("Recording started. Ctrl+C to stop, 's' status, 'p' pause/resume.")

        try:
            while True:
                if args.duration and (time.time() - start_time) > args.duration:
                    print("Duration limit reached.")
                    break
                if paused:
                    time.sleep(0.1)
                    continue
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames_queue.put(data)
        except KeyboardInterrupt:
            print("Recording stopped by user.")
        except Exception as e:
            logging.error(f"Recording error: {e}")
        finally:
            keyboard.remove_hotkey('s')
            keyboard.remove_hotkey('p')
            stream.stop_stream()
            stream.close()
            p.terminate()
            writing_done.set()
            writer_thread.join()
            frames_queue.join()
            duration_secs = time.time() - start_time
            print(f"Recording complete: {WAVE_OUTPUT_FILENAME} ({duration_secs:.2f}s)")

if __name__ == "__main__":
    main()
