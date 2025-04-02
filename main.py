import random
import time
import json
import os
import datetime
import platform
from pydub import AudioSegment
from pydub.playback import play

def play_sound(sound_file, volume):
    """Plays the specified sound file using pydub."""
    try:
        sound = AudioSegment.from_file(sound_file)
        sound.apply_gain(volume)
        play(sound)
    except Exception as e:
        print(f"Error playing sound: {e}")

def get_sound_files(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith(('.wav', '.mp3', '.ogg'))]


def main():
    config_file = 'config.json'

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            interval = config.get('interval', 60)  # Default interval is 60 seconds
            scheduled_sounds = config.get('scheduled_sounds', {})
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading configuration: {e}. Using default interval of 60 seconds and no scheduled sounds.")
        interval = 60
        scheduled_sounds = {}

    general_sounds_dir = 'sounds/general'
    timed_sounds_dir = 'sounds/timed'
    
    volume = config.get('volume', 0.5)  # Default volume is -20 dB

    for dir in [general_sounds_dir, timed_sounds_dir]:
        if not os.path.exists(dir):
            os.makedirs(dir)

    general_sound_files = get_sound_files(general_sounds_dir)
    timed_sound_files = {datetime.datetime.strptime(time, "%H:%M").time(): os.path.join(timed_sounds_dir, file) for time, file in scheduled_sounds.items()}
    
    # print the scheduled sounds
    print("Scheduled sounds:")
    for t, sound_file in timed_sound_files.items():
        print(f"{t}: {sound_file}")


    if not general_sound_files:
        print("No general sound files found in 'sounds/general'.")


    next_general_sound_time = time.time() + interval

    while True:
        current_time = datetime.datetime.strptime(datetime.datetime.now().strftime("%H:%M:%S"), "%H:%M:%S").time()
        print(f"Current time: {current_time}")

        # Play timed sounds
        for scheduled_time, sound_file in timed_sound_files.items():
            if current_time >= scheduled_time and  (current_time.minute * 60 + current_time.second) < (scheduled_time.minute * 60 + scheduled_time.second +5): # play if within the current minute
                play_sound(sound_file, volume)
                print(f"Played scheduled sound: {sound_file} at {current_time}")
                del timed_sound_files[scheduled_time] # remove played sound
                break # only play one timed sound at a time
        
        # Play general sounds
        if time.time() >= next_general_sound_time:
            if general_sound_files:
                play_sound(random.choice(general_sound_files), volume)
                next_general_sound_time = time.time() + interval
                print(f"Played general sound at {datetime.datetime.now()}")
            else:
                print("No general sound files to play.")

        time.sleep(1)  # Check every second


if __name__ == "__main__":
    main()

